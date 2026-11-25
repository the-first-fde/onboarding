"""동기화 로직 검증용 in-memory GitHub·Notion fake와 입력 생성 helper."""

import itertools
from dataclasses import replace

from collaboration.github_client import (
    NOT_IN_PROJECT,
    PROJECT_ERROR,
    IssueSnapshot,
    ProjectLookup,
    ProjectResult,
)
from collaboration.http_api import AuthError, UncertainWriteError
from collaboration.notion_client import NotionPage
from collaboration.notion_sync import OPTIONAL_PROPERTIES, REQUIRED_PROPERTIES

REPO = "the-first-fde/onboarding"


def make_issue(number, **overrides):
    values = {
        "issue_id": 1000 + number,
        "node_id": f"I_node{number}",
        "number": number,
        "repository": REPO,
        "title": f"Issue {number}",
        "body": "본문",
        "state": "open",
        "state_reason": None,
        "author": "member-a",
        "assignees": ("member-a",),
        "labels": ("feature",),
        "milestone": "SPRINT 1",
        "url": f"https://github.com/{REPO}/issues/{number}",
        "created_at": "2026-11-20T01:00:00Z",
        "updated_at": "2026-11-21T01:00:00Z",
    }
    values.update(overrides)
    return IssueSnapshot(**values)


def plain(prop):
    return "".join(p["text"]["content"] for p in prop["rich_text"])


class FakeGitHub:
    """GitHubClient와 같은 메서드를 가진 in-memory GitHub."""

    def __init__(self):
        self.issues: dict[int, IssueSnapshot] = {}
        self.pull_requests: set[int] = set()
        self.projects: dict[str, ProjectResult] = {}
        self.project_available = True

    def add(self, issue):
        self.issues[issue.number] = issue

    def update(self, number, **changes):
        self.issues[number] = replace(self.issues[number], **changes)

    def set_project(self, number, lookup=ProjectLookup.OK, **fields):
        node_id = self.issues[number].node_id
        current = self.projects.get(node_id, ProjectResult(ProjectLookup.OK))
        self.projects[node_id] = ProjectResult(lookup, replace(current.fields, **fields))

    def get_issue(self, number):
        return None if number in self.pull_requests else self.issues[number]

    def list_issues(self):
        return list(self.issues.values())

    def get_project_result(self, issue):
        if not self.project_available:
            return PROJECT_ERROR
        return self.projects.get(issue.node_id, NOT_IN_PROJECT)

    def load_project_index(self):
        return dict(self.projects) if self.project_available else None


class FakeNotion:
    """NotionClient와 같은 메서드를 가진 in-memory Data Source."""

    def __init__(self):
        self.pages: dict[str, dict] = {}
        self.ids = itertools.count(1)
        self.writes: list[str] = []
        # 제목 속성 이름을 Title이 아닌 값으로 두어 유형 기반 인식을 항상 거치게 한다.
        self.schema = (
            {"Name": "title"} | REQUIRED_PROPERTIES | OPTIONAL_PROPERTIES | {"Notes": "rich_text"}
        )
        self.lose_next_create_response = False
        self.create_never_visible = False
        self.fail_next_update = False
        self.auth_fails = False

    def get_property_types(self):
        if self.auth_fails:
            raise AuthError(401, "unauthorized")
        return dict(self.schema)

    def _page(self, page_id):
        props = self.pages[page_id]["properties"]

        def text(name):
            return plain(props[name]) if name in props else ""

        return NotionPage(page_id, text("Sync Key"), text("Sync Hash"), text("Body Hash"))

    def find_pages(self, key):
        return [self._page(pid) for pid in self.pages if self._page(pid).sync_key == key]

    def list_pages(self, repository):
        return [
            self._page(pid)
            for pid, page in self.pages.items()
            if plain(page["properties"].get("Repository", {"rich_text": []})) == repository
        ]

    def _new_block(self, block):
        kind = block["type"]
        stored = {**block, "id": f"b{next(self.ids)}"}
        stored["_children"] = [self._new_block(c) for c in block[kind].get("children", [])]
        return stored

    def create_page(self, properties, children):
        self.writes.append("create")
        page_id = f"p{next(self.ids)}"
        self.pages[page_id] = {
            "properties": dict(properties),
            "blocks": [self._new_block(b) for b in children],
        }
        if self.create_never_visible:
            del self.pages[page_id]  # 조회 인덱스 반영 지연을 흉내 낸다.
            raise UncertainWriteError("response lost")
        if self.lose_next_create_response:
            self.lose_next_create_response = False
            raise UncertainWriteError("response lost")
        return page_id

    def update_page(self, page_id, properties):
        if self.fail_next_update:
            self.fail_next_update = False
            raise UncertainWriteError("update lost")
        self.writes.append("update")
        self.pages[page_id]["properties"].update(properties)

    def _children_of(self, block_id):
        for page_id, page in self.pages.items():
            if page_id == block_id:
                return page["blocks"]
            for block in page["blocks"]:
                if block["id"] == block_id:
                    return block["_children"]
        raise KeyError(block_id)

    def list_children(self, block_id):
        return [dict(b) for b in self._children_of(block_id)]

    def delete_block(self, block_id):
        self.writes.append("delete")
        for page in self.pages.values():
            page["blocks"] = [b for b in page["blocks"] if b["id"] != block_id]
            for block in page["blocks"]:
                block["_children"] = [c for c in block["_children"] if c["id"] != block_id]

    def append_children(self, block_id, children):
        self.writes.append("append")
        self._children_of(block_id).extend(self._new_block(b) for b in children)

    def only_page(self):
        assert len(self.pages) == 1
        return next(iter(self.pages.values()))

    def add_human_block(self, page_id, text):
        block = {"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": text}}]}}
        self.pages[page_id]["blocks"].append(self._new_block(block))
