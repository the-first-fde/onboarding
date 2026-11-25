"""GitHub Issue(REST)와 Projects v2(GraphQL)를 읽기 전용으로 조회한다."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from collaboration.http_api import ApiError, JsonApi, TransportError

GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"
ISSUES_PAGE_SIZE = 100
PROJECT_ITEMS_PAGE_SIZE = 100
ISSUE_PROJECT_ITEMS_LIMIT = 20
# 무한 페이지네이션 방지 상한(100 x 100 = 10,000건).
MAX_PAGES = 100

# Project 필드 이름 → (GraphQL dataType, ProjectFields 속성). 2026-11-25 "HR AX" Project 조사 기준.
PROJECT_FIELD_MAP: dict[str, tuple[str, str]] = {
    "Status": ("SINGLE_SELECT", "status"),
    "Priority": ("SINGLE_SELECT", "priority"),
    "Size": ("SINGLE_SELECT", "size"),
    "Estimate": ("NUMBER", "estimate"),
    "Start date": ("DATE", "start_date"),
    "Target date": ("DATE", "target_date"),
}
KNOWN_STATUSES = frozenset({"Backlog", "Ready", "In progress", "In review", "Done"})

_FIELD_VALUE_FRAGMENT = """
fragment FieldValue on ProjectV2ItemFieldValue {
  __typename
  ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } }
  ... on ProjectV2ItemFieldDateValue { date field { ... on ProjectV2FieldCommon { name } } }
  ... on ProjectV2ItemFieldNumberValue { number field { ... on ProjectV2FieldCommon { name } } }
}
"""

SCHEMA_QUERY = """
query($owner: String!, $number: Int!) {
  organization(login: $owner) { projectV2(number: $number) {
    fields(first: 50) { nodes { ... on ProjectV2FieldCommon { name dataType } } }
  } }
}
"""

ISSUE_ITEMS_QUERY = (
    """
query($owner: String!, $name: String!, $number: Int!, $first: Int!) {
  repository(owner: $owner, name: $name) { issue(number: $number) {
    projectItems(first: $first) { pageInfo { hasNextPage } nodes {
      isArchived
      project { number owner { ... on Organization { login } } }
      fieldValues(first: 50) { nodes { ...FieldValue } }
    } }
  } }
}
"""
    + _FIELD_VALUE_FRAGMENT
)

PROJECT_ITEMS_QUERY = (
    """
query($owner: String!, $number: Int!, $first: Int!, $cursor: String) {
  organization(login: $owner) { projectV2(number: $number) {
    items(first: $first, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        isArchived
        content { __typename ... on Issue { id repository { nameWithOwner } } }
        fieldValues(first: 50) { nodes { ...FieldValue } }
      }
    }
  } }
}
"""
    + _FIELD_VALUE_FRAGMENT
)


@dataclass(frozen=True)
class IssueSnapshot:
    """GitHub에서 조회한 최신 Issue. 작성자 입력(title/body)은 신뢰하지 않는 데이터다."""

    issue_id: int
    node_id: str
    number: int
    repository: str
    title: str
    body: str
    state: str
    state_reason: str | None
    author: str
    assignees: tuple[str, ...]
    labels: tuple[str, ...]
    milestone: str | None
    url: str
    created_at: str
    updated_at: str


class ProjectLookup(StrEnum):
    """Issue의 Project 조회 결과 종류."""

    OK = "ok"
    NOT_IN_PROJECT = "not_in_project"
    UNMAPPED = "unmapped"
    ERROR = "error"


@dataclass(frozen=True)
class ProjectFields:
    """동기화 대상 Project 필드 값. 비어 있으면 None."""

    status: str | None = None
    priority: str | None = None
    size: str | None = None
    estimate: float | None = None
    start_date: str | None = None
    target_date: str | None = None


@dataclass(frozen=True)
class ProjectResult:
    """한 Issue의 Project 조회 결과."""

    lookup: ProjectLookup
    fields: ProjectFields = field(default_factory=ProjectFields)


PROJECT_ERROR = ProjectResult(ProjectLookup.ERROR)
NOT_IN_PROJECT = ProjectResult(ProjectLookup.NOT_IN_PROJECT)


class ProjectUnavailableError(Exception):
    """권한·스키마·응답 문제로 Project 값을 신뢰할 수 없음."""


def github_headers(token: str) -> dict[str, str]:
    """GitHub API 공통 header를 만든다. 반환값은 로그에 출력하지 않는다."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "notion-sync",
    }


def parse_issue(raw: dict[str, Any], repository: str) -> IssueSnapshot | None:
    """REST Issue 응답을 정규화한다.

    Args:
        raw: Issue API 응답 객체.
        repository: `owner/name`.

    Returns:
        Pull Request이면 None, 아니면 IssueSnapshot.
    """
    if "pull_request" in raw:
        return None
    milestone = raw.get("milestone") or {}
    return IssueSnapshot(
        issue_id=int(raw["id"]),
        node_id=str(raw["node_id"]),
        number=int(raw["number"]),
        repository=repository,
        title=str(raw.get("title") or ""),
        body=str(raw.get("body") or ""),
        state=str(raw["state"]),
        state_reason=raw.get("state_reason"),
        author=str((raw.get("user") or {}).get("login") or ""),
        assignees=tuple(sorted(a["login"] for a in raw.get("assignees") or [])),
        labels=tuple(sorted(label["name"] for label in raw.get("labels") or [])),
        milestone=milestone.get("title"),
        url=str(raw["html_url"]),
        created_at=str(raw["created_at"]),
        updated_at=str(raw["updated_at"]),
    )


def parse_field_values(nodes: list[dict[str, Any]]) -> ProjectResult:
    """Project item의 field value 목록을 변환한다. 모르는 Status 옵션은 UNMAPPED."""
    values: dict[str, Any] = {}
    for node in nodes:
        name = (node.get("field") or {}).get("name")
        if name in PROJECT_FIELD_MAP:
            attribute = PROJECT_FIELD_MAP[name][1]
            values[attribute] = node.get("name", node.get("date", node.get("number")))
    fields = ProjectFields(**values)
    if fields.status is not None and fields.status not in KNOWN_STATUSES:
        return ProjectResult(ProjectLookup.UNMAPPED, fields)
    return ProjectResult(ProjectLookup.OK, fields)


class GitHubClient:
    """동기화 대상 Repository의 Issue와 Organization Project를 조회한다."""

    def __init__(self, api: JsonApi, repository: str, project_number: int | None) -> None:
        """클라이언트를 만든다.

        Args:
            api: Issues·Projects 읽기 권한 토큰으로 인증한 GitHub API.
            repository: `owner/name`. owner는 Project를 소유한 Organization이다.
            project_number: Organization Project 번호. 없으면 Project 조회는 ERROR.
        """
        self._api = api
        self._repository = repository
        self._owner, self._name = repository.split("/", 1)
        self._project_number = project_number

    def get_issue(self, number: int) -> IssueSnapshot | None:
        """Issue 하나의 최신 상태를 조회한다. Pull Request이면 None."""
        path = f"/repos/{self._repository}/issues/{number}"
        return parse_issue(self._api.request("GET", path, idempotent=True), self._repository)

    def list_issues(self) -> list[IssueSnapshot]:
        """Open·Closed Issue 전체를 페이지 단위로 조회하고 Pull Request는 제외한다."""
        issues: list[IssueSnapshot] = []
        for page in range(1, MAX_PAGES + 1):
            path = (
                f"/repos/{self._repository}/issues?state=all&sort=created&direction=asc"
                f"&per_page={ISSUES_PAGE_SIZE}&page={page}"
            )
            raws = self._api.request("GET", path, idempotent=True)
            if not isinstance(raws, list):
                raise ApiError(200, "unexpected_shape")
            issues.extend(i for r in raws if (i := parse_issue(r, self._repository)) is not None)
            if len(raws) < ISSUES_PAGE_SIZE:
                return issues
        raise ApiError(200, "too_many_pages")

    def get_project_result(self, issue: IssueSnapshot) -> ProjectResult:
        """Issue 하나의 Project 필드를 조회한다. 실패는 ERROR로 돌려 기존 값을 보존하게 한다."""
        try:
            self._check_schema()
            variables = {
                "owner": self._owner,
                "name": self._name,
                "number": issue.number,
                "first": ISSUE_PROJECT_ITEMS_LIMIT,
            }
            data = self._query(ISSUE_ITEMS_QUERY, variables)
            connection = data["repository"]["issue"]["projectItems"]
            for item in connection["nodes"]:
                project = item.get("project") or {}
                owner = (project.get("owner") or {}).get("login")
                if (
                    project.get("number") == self._project_number
                    and owner == self._owner
                    and not item.get("isArchived")
                ):
                    return parse_field_values(item["fieldValues"]["nodes"])
            truncated = bool(connection["pageInfo"]["hasNextPage"])
        except (ProjectUnavailableError, ApiError, TransportError, KeyError, TypeError):
            return PROJECT_ERROR
        # 다른 Project가 많아 목록이 잘렸으면 없다고 단정하지 않고 기존 값을 보존한다.
        return PROJECT_ERROR if truncated else NOT_IN_PROJECT

    def load_project_index(self) -> dict[str, ProjectResult] | None:
        """Project의 Issue item 전체를 Issue node ID별로 조회한다.

        Pull Request·Draft Issue·다른 Repository·보관된 item은 제외한다.

        Returns:
            node ID → 결과 dict. 조회에 실패하면 None.
        """
        try:
            self._check_schema()
            results: dict[str, ProjectResult] = {}
            cursor: str | None = None
            for _ in range(MAX_PAGES):
                variables = {
                    "owner": self._owner,
                    "number": self._project_number,
                    "first": PROJECT_ITEMS_PAGE_SIZE,
                    "cursor": cursor,
                }
                data = self._query(PROJECT_ITEMS_QUERY, variables)
                items = data["organization"]["projectV2"]["items"]
                for item in items["nodes"]:
                    content = item.get("content") or {}
                    if (
                        content.get("__typename") == "Issue"
                        and content["repository"]["nameWithOwner"] == self._repository
                        and not item.get("isArchived")
                    ):
                        results[content["id"]] = parse_field_values(item["fieldValues"]["nodes"])
                if not items["pageInfo"]["hasNextPage"]:
                    return results
                cursor = items["pageInfo"]["endCursor"]
                if not cursor:
                    return None
            return None
        except (ProjectUnavailableError, ApiError, TransportError, KeyError, TypeError):
            return None

    def _check_schema(self) -> None:
        data = self._query(SCHEMA_QUERY, {"owner": self._owner, "number": self._project_number})
        project = (data.get("organization") or {}).get("projectV2")
        if not project:
            raise ProjectUnavailableError("project not found")
        types = {f.get("name"): f.get("dataType") for f in project["fields"]["nodes"]}
        for name, (data_type, _) in PROJECT_FIELD_MAP.items():
            if types.get(name) != data_type:
                raise ProjectUnavailableError(f"project field mismatch: {name}")

    def _query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        if self._project_number is None:
            raise ProjectUnavailableError("project number not configured")
        reply = self._api.request(
            "POST", "/graphql", {"query": query, "variables": variables}, idempotent=True
        )
        if not isinstance(reply, dict) or reply.get("errors"):
            raise ProjectUnavailableError("graphql error")
        return reply.get("data") or {}
