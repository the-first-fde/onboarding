"""GitHub Issue·Project 데이터를 Notion Data Source에 단방향 upsert한다.

실행 예(저장소 루트): `uv run --locked python -m collaboration.notion_sync --all --dry-run`
(`PYTHONPATH=scripts` 필요). 쓰기는 `NOTION_SYNC_ENABLED=true`이고 dry-run이 아닐 때만 한다.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from collaboration.github_client import (
    GITHUB_API_URL,
    META_ERROR,
    IssueMetaResult,
    IssueMetaLookup,
    NOT_IN_PROJECT,
    PROJECT_ERROR,
    GitHubClient,
    IssueSnapshot,
    ProjectLookup,
    ProjectResult,
    github_headers,
)
from collaboration.http_api import ApiError, AuthError, JsonApi, TransportError, UncertainWriteError
from collaboration.notion_client import NOTION_API_URL, NotionClient, NotionPage, notion_headers

MAX_TEXT_CHARS = 2000
MAX_BODY_CHARS = 50_000
MAX_BODY_BLOCKS = 90
BODY_MARKER = "GitHub 본문 (자동 동기화 영역: 이 토글 안의 내용은 덮어써집니다)"
EMPTY_BODY = "(본문 없음)"

# 반드시 있어야 하는 Notion 속성과 유형. 제목은 이름과 무관하게 title 유형 속성을 찾는다.
REQUIRED_PROPERTIES: dict[str, str] = {
    "Sync Key": "rich_text",
    "Sync Hash": "rich_text",
    "Body Hash": "rich_text",
    "Repository": "rich_text",
    "GitHub URL": "url",
    "Issue State": "select",
    "Project Status": "select",
    "Assignees": "rich_text",
}
# DB에 있을 때만 쓰는 속성. 나중에 추가하면 다음 실행에서 해시가 달라져 기존 페이지도 채워진다.
OPTIONAL_PROPERTIES: dict[str, str] = {
    "Issue Number": "number",
    "Close Reason": "select",
    "Labels": "multi_select",
    "Milestone": "rich_text",
    "Created At": "date",
    "Updated At": "date",
    "Priority": "select",
    "Issue Type": "select",
    "Feature ID": "rich_text",
    "Track": "select",
    "Parent Issue": "rich_text",
    "Sub-issues Progress": "rich_text",
    "Blocked By": "rich_text",
    "Issue Meta Sync State": "select",
    "Size": "select",
    "Estimate": "number",
    "Start Date": "date",
    "Target Date": "date",
    "Project Sync State": "select",
    "Synced At": "date",
}
# 이 두 목록 밖의 속성(예: Notes)은 사람이 관리하며 동기화가 쓰지 않는다.
TITLE = "Title"  # build_properties 안에서 쓰는 제목 키. 실제 Notion 속성 이름으로 바꿔 쓴다.

_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_DATA_SOURCE_PATTERN = re.compile(r"^[0-9a-fA-F]{8}-?([0-9a-fA-F]{4}-?){3}[0-9a-fA-F]{12}$")
_NUMBER_PATTERN = re.compile(r"^[0-9]{1,9}$")
# 응답 형태가 예상과 다를 때 나는 예외. 공개 로그에 traceback을 남기지 않고 코드로 보고한다.
_SHAPE_ERRORS = (KeyError, TypeError, ValueError, AttributeError)


class ConfigError(Exception):
    """환경 변수 누락 또는 형식 오류. 메시지에는 변수 이름만 담는다."""


class SchemaError(Exception):
    """Notion Data Source 속성이 동기화 요구와 다름."""


class SyncOutcome(StrEnum):
    """Issue 하나의 동기화 결과."""

    CREATED = "created"
    UPDATED = "updated"
    UNCHANGED = "unchanged"
    SKIPPED = "skipped"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass(frozen=True)
class SyncSettings:
    """검증된 실행 설정."""

    repository: str
    allowed_authors: frozenset[str]
    write_enabled: bool


@dataclass(frozen=True)
class IssueResult:
    """Issue 하나의 결과. detail에는 고정 코드만 담고 Issue 내용은 담지 않는다."""

    number: int
    outcome: SyncOutcome
    project: ProjectLookup | None = None
    detail: str = ""
    meta: IssueMetaLookup | None = None


@dataclass(frozen=True)
class SyncReport:
    """한 번의 실행 결과."""

    dry_run: bool
    results: tuple[IssueResult, ...] = ()
    orphans: tuple[str, ...] = ()
    invalid_orphans: int = 0
    fatal: str | None = None
    warnings: tuple[str, ...] = ()

    def exit_code(self) -> int:
        """실패·충돌·Project 조회 문제가 있으면 1을 반환한다."""
        if self.fatal:
            return 1
        for result in self.results:
            if result.outcome in (SyncOutcome.FAILED, SyncOutcome.CONFLICT):
                return 1
            if result.meta is IssueMetaLookup.ERROR:
                return 1
            if result.project in (ProjectLookup.ERROR, ProjectLookup.UNMAPPED):
                return 1
        return 0

    def to_markdown(self) -> str:
        """GitHub Job Summary용 요약을 만든다. 번호·결과 코드만 포함한다."""
        mode = "dry-run (no Notion writes)" if self.dry_run else "write"
        lines = [f"## Notion sync: {mode}", ""]
        if self.fatal:
            lines.append(f"FATAL: {self.fatal}")
        lines.extend(f"WARNING: {warning}" for warning in self.warnings)
        counts = {o: sum(r.outcome is o for r in self.results) for o in SyncOutcome}
        lines.append(" · ".join(f"{o.value}={n}" for o, n in counts.items()))
        attention = [
            r
            for r in self.results
            if r.outcome not in (SyncOutcome.UNCHANGED, SyncOutcome.CREATED, SyncOutcome.UPDATED)
            or r.project not in (None, ProjectLookup.OK, ProjectLookup.NOT_IN_PROJECT)
            or r.meta is IssueMetaLookup.ERROR
            or r.detail
        ]
        lines.extend(
            (
                f"- #{r.number}: {r.outcome.value} project={r.project or '-'} "
                f"meta={r.meta or '-'} {r.detail}"
            ).rstrip()
            for r in attention
        )
        lines.extend(f"- orphan page (no GitHub issue): {key}" for key in self.orphans)
        if self.invalid_orphans:
            lines.append(f"- pages with unexpected Sync Key: {self.invalid_orphans}")
        return "\n".join(lines) + "\n"


# --- 매핑 -----------------------------------------------------------------


def sync_key(issue: IssueSnapshot) -> str:
    """Repository와 변하지 않는 Issue ID로 Notion 페이지 식별자를 만든다."""
    return f"{issue.repository}#{issue.issue_id}"


def _text(value: str) -> dict[str, Any]:
    return {"type": "text", "text": {"content": value}}


def _rich(value: str | None) -> dict[str, Any]:
    return {"rich_text": [_text(value[:MAX_TEXT_CHARS])] if value else []}


def _select(value: str | None) -> dict[str, Any]:
    # Notion select 옵션 이름에는 쉼표를 쓸 수 없다.
    return {"select": {"name": value.replace(",", " ")[:100]} if value else None}


def _date(value: str | None) -> dict[str, Any]:
    return {"date": {"start": value} if value else None}


def build_properties(
    issue: IssueSnapshot, project: ProjectResult, meta: IssueMetaResult
) -> dict[str, Any]:
    """GitHub이 소유하는 Notion 속성 값을 만든다.

    Project 조회가 ERROR면 Project 속성을 빼서 기존 값을 보존하고, UNMAPPED면
    Project Status만 뺀다. Issue Close 여부로 Project Status를 추론하지 않는다.
    Issue 메타데이터가 ERROR면 관련 속성을 빼서 기존 값을 보존하고,
    priority_known이 False면 Priority만 빼서 기존 값을 보존한다.
    """
    props: dict[str, Any] = {
        TITLE: {"title": [_text(issue.title[:MAX_TEXT_CHARS])]},
        "Sync Key": _rich(sync_key(issue)),
        "Issue Number": {"number": issue.number},
        "Repository": _rich(issue.repository),
        "GitHub URL": {"url": issue.url},
        "Issue State": _select("Closed" if issue.state == "closed" else "Open"),
        "Close Reason": _select(issue.state_reason if issue.state == "closed" else None),
        "Assignees": _rich(", ".join(issue.assignees)),
        "Labels": {"multi_select": [{"name": n.replace(",", " ")[:100]} for n in issue.labels]},
        "Milestone": _rich(issue.milestone),
        "Created At": _date(issue.created_at),
        "Updated At": _date(issue.updated_at),
        "Project Sync State": _select(project.lookup.value),
    }
    props["Issue Meta Sync State"] = _select(meta.lookup.value)
    if meta.lookup is IssueMetaLookup.OK:
        value = meta.meta
        if value.priority_known:
            props["Priority"] = _select(value.priority)
        props["Issue Type"] = _select(value.issue_type)
        props["Parent Issue"] = _rich(f"#{value.parent}" if value.parent is not None else None)
        props["Sub-issues Progress"] = _rich(
            f"{value.sub_issues_completed}/{value.sub_issues_total}"
            if value.sub_issues_total else None
        )
        props["Blocked By"] = _rich(", ".join(f"#{n}" for n in value.blocked_by))
    if project.lookup is not ProjectLookup.ERROR:
        fields = project.fields
        if project.lookup is not ProjectLookup.UNMAPPED:
            props["Project Status"] = _select(fields.status)
        props["Size"] = _select(fields.size)
        props["Estimate"] = {"number": fields.estimate}
        props["Start Date"] = _date(fields.start_date)
        props["Target Date"] = _date(fields.target_date)
        props["Track"] = _select(fields.track)
        props["Feature ID"] = _rich(fields.feature_id)
    return props


def _paragraph(value: str) -> dict[str, Any]:
    chunks = [value[i : i + MAX_TEXT_CHARS] for i in range(0, len(value), MAX_TEXT_CHARS)]
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [_text(c) for c in chunks]},
    }


def body_blocks(body: str, source_url: str) -> list[dict[str, Any]]:
    """Issue 본문을 빈 줄 기준 문단 블록으로 바꾼다.

    Markdown은 해석하지 않고 원문 텍스트로 둔다. 링크·HTML을 만들지 않으므로 본문의
    URL로 요청하지 않는다. 길이·블록 수 제한을 넘으면 원문 링크 안내로 끝낸다.
    """
    text = body.replace("\r\n", "\n").strip()
    truncated = len(text) > MAX_BODY_CHARS
    paragraphs = [p.strip("\n") for p in re.split(r"\n\s*\n", text[:MAX_BODY_CHARS]) if p.strip()]
    if not paragraphs:
        return [_paragraph(EMPTY_BODY)]
    truncated = truncated or len(paragraphs) > MAX_BODY_BLOCKS
    blocks = [_paragraph(p) for p in paragraphs[:MAX_BODY_BLOCKS]]
    if truncated:
        blocks.append(_paragraph(f"(본문이 길어 일부만 표시합니다. 원문: {source_url})"))
    return blocks


def body_toggle(blocks: list[dict[str, Any]]) -> dict[str, Any]:
    """사람이 쓴 블록과 분리된 GitHub 본문 토글 블록을 만든다."""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {"rich_text": [_text(BODY_MARKER)], "children": blocks},
    }


def fit_properties(props: dict[str, Any], types: Mapping[str, str]) -> dict[str, Any]:
    """실제 Notion 스키마에 맞춰 제목 이름을 바꾸고 없는 선택 속성을 뺀다.

    Args:
        props: build_properties 결과와 동기화 메타데이터.
        types: `_check_schema`로 검증한 속성 이름 → 유형.

    Returns:
        Notion에 보낼 속성.
    """
    title = next(name for name, kind in types.items() if kind == "title")
    fitted: dict[str, Any] = {}
    for name, value in props.items():
        if name == TITLE:
            fitted[title] = value
        elif name in REQUIRED_PROPERTIES or name in types:
            fitted[name] = value
    return fitted


def content_hash(value: Any) -> str:
    """키 순서와 무관한 SHA-256 해시를 만든다."""
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


# --- 동기화 ----------------------------------------------------------------


def _block_text(block: dict[str, Any]) -> str:
    parts = (block.get(block.get("type", "")) or {}).get("rich_text") or []
    return "".join(p.get("plain_text", (p.get("text") or {}).get("content", "")) for p in parts)


def _replace_body(notion: NotionClient, page_id: str, blocks: list[dict[str, Any]]) -> None:
    toggle = next(
        (
            b
            for b in notion.list_children(page_id)
            if b.get("type") == "toggle" and _block_text(b) == BODY_MARKER
        ),
        None,
    )
    if toggle is None:  # 사람이 토글을 지웠다면 페이지 끝에 새로 붙인다.
        notion.append_children(page_id, [body_toggle(blocks)])
        return
    for child in notion.list_children(toggle["id"]):
        notion.delete_block(child["id"])
    notion.append_children(toggle["id"], blocks)


def _create(
    notion: NotionClient, key: str, props: dict[str, Any], blocks: list[dict[str, Any]]
) -> None:
    try:
        notion.create_page(props, [body_toggle(blocks)])
    except UncertainWriteError:
        # 응답만 유실된 경우를 확인한다. 조회 반영이 늦을 수 있어 여기서 다시 만들지 않고
        # 실패로 남긴다. 다음 이벤트·예약 실행이 다시 조회해 처리한다.
        if not notion.find_pages(key):
            raise


def _state_note(issue: IssueSnapshot, project: ProjectResult) -> str:
    status = project.fields.status
    if project.lookup is not ProjectLookup.OK or status is None:
        return ""
    if (issue.state == "closed") != (status == "Done"):
        return "state_mismatch"
    return ""


def sync_issue(
    issue: IssueSnapshot,
    project: ProjectResult,
    meta: IssueMetaResult,
    pages: Sequence[NotionPage],
    notion: NotionClient,
    types: Mapping[str, str],
    settings: SyncSettings,
    now: str,
) -> IssueResult:
    """Issue 하나를 upsert한다.

    GitHub 데이터로 만든 해시와 Notion에 저장한 해시만 비교한다. Notion에서 사람이 바꾼
    GitHub 소유 속성은 다음 GitHub 변경 때 덮어쓴다. 본문은 본문 해시가 바뀔 때만 다시 쓴다.

    Args:
        issue: GitHub에서 조회한 최신 Issue.
        project: 같은 Issue의 Project 조회 결과.
        pages: 같은 Sync Key를 가진 Notion 페이지.
        notion: Notion 클라이언트.
        types: 검증된 Notion 속성 이름 → 유형.
        settings: 실행 설정. 쓰기 비활성이면 예정 결과만 반환한다.
        now: Synced At에 쓸 UTC 시각.

    Returns:
        결과 코드. detail에는 고정 코드만 담는다.

    Raises:
        ApiError: Notion 요청 실패.
        UncertainWriteError: 쓰기 반영 여부를 확인할 수 없음.
    """
    if issue.author.lower() not in settings.allowed_authors:
        return IssueResult(issue.number, SyncOutcome.SKIPPED, detail="author_not_allowed")
    if len(pages) > 1:
        return IssueResult(
            issue.number, SyncOutcome.CONFLICT, project.lookup, "duplicate_pages", meta.lookup
        )
    props = fit_properties(build_properties(issue, project, meta), types)
    blocks = body_blocks(issue.body, issue.url)
    props_hash, body_hash = content_hash(props), content_hash(blocks)
    note = _state_note(issue, project)
    page = pages[0] if pages else None
    if page and page.sync_hash == props_hash and page.body_hash == body_hash:
        return IssueResult(issue.number, SyncOutcome.UNCHANGED, project.lookup, note, meta.lookup)
    outcome = SyncOutcome.UPDATED if page else SyncOutcome.CREATED
    if not settings.write_enabled:
        return IssueResult(issue.number, outcome, project.lookup, note, meta.lookup)
    # 해시는 본문 교체가 끝난 뒤 저장한다. 중간에 실패하면 다음 실행이 다시 시도한다.
    sync_meta = fit_properties(
        {"Sync Hash": _rich(props_hash), "Body Hash": _rich(body_hash), "Synced At": _date(now)},
        types,
    )
    if page is None:
        _create(notion, sync_key(issue), props | sync_meta, blocks)
        return IssueResult(issue.number, outcome, project.lookup, note, meta.lookup)
    if page.body_hash != body_hash:
        _replace_body(notion, page.page_id, blocks)
    notion.update_page(page.page_id, props | sync_meta)
    return IssueResult(issue.number, outcome, project.lookup, note, meta.lookup)


def _check_schema(notion: NotionClient) -> dict[str, str]:
    types = notion.get_property_types()
    wrong = [name for name, kind in REQUIRED_PROPERTIES.items() if types.get(name) != kind]
    wrong += [n for n, kind in OPTIONAL_PROPERTIES.items() if n in types and types[n] != kind]
    if "title" not in types.values():
        wrong.append("(title)")
    if wrong:
        raise SchemaError("Notion property missing or wrong type: " + ", ".join(wrong))
    return types


def _safe_sync(
    issue: IssueSnapshot,
    project: ProjectResult,
    meta: IssueMetaResult,
    pages: Sequence[NotionPage],
    notion: NotionClient,
    types: Mapping[str, str],
    settings: SyncSettings,
    now: str,
) -> IssueResult:
    """Issue 하나의 API 실패를 결과로 기록한다. 인증 실패는 전체 실행을 멈춘다."""
    try:
        return sync_issue(issue, project, meta, pages, notion, types, settings, now)
    except AuthError:
        raise
    except (ApiError, TransportError, UncertainWriteError) as error:
        return IssueResult(
            issue.number, SyncOutcome.FAILED, project.lookup, _describe(error), meta.lookup
        )
    except _SHAPE_ERRORS:
        return IssueResult(
            issue.number, SyncOutcome.FAILED, project.lookup, "unexpected_response", meta.lookup
        )


def _describe(error: Exception) -> str:
    if isinstance(error, ApiError):
        return f"{type(error).__name__}:{error.status}:{error.code}"
    return type(error).__name__


def run_issue(
    number: int, github: GitHubClient, notion: NotionClient, settings: SyncSettings, now: str
) -> SyncReport:
    """Issue 이벤트 또는 수동 실행에서 Issue 하나를 최신 GitHub 데이터로 동기화한다.

    이벤트 payload를 쓰지 않고 번호로 다시 조회하므로 순서가 바뀐 이벤트도 최신 상태가 된다.
    허용되지 않은 작성자는 Project·Notion을 조회하기 전에 건너뛴다.

    Args:
        number: Issue 번호.
        github: GitHub 클라이언트.
        notion: Notion 클라이언트.
        settings: 실행 설정.
        now: Synced At에 쓸 UTC 시각.

    Returns:
        결과 1건 또는 fatal 사유를 담은 보고.
    """
    dry_run = not settings.write_enabled
    try:
        types = _check_schema(notion)
        issue = github.get_issue(number)
        if issue is None:
            result = IssueResult(number, SyncOutcome.SKIPPED, detail="pull_request")
            return SyncReport(dry_run, (result,))
        if issue.author.lower() not in settings.allowed_authors:
            result = IssueResult(number, SyncOutcome.SKIPPED, detail="author_not_allowed")
            return SyncReport(dry_run, (result,))
        project = github.get_project_result(issue)
        meta = github.get_issue_meta(issue)
        pages = notion.find_pages(sync_key(issue))
        return SyncReport(
            dry_run, (_safe_sync(issue, project, meta, pages, notion, types, settings, now),)
        )
    except SchemaError as error:
        return SyncReport(dry_run, fatal=str(error))
    except (ApiError, TransportError, UncertainWriteError) as error:
        return SyncReport(dry_run, fatal=_describe(error))
    except _SHAPE_ERRORS:
        return SyncReport(dry_run, fatal="unexpected_response")


def run_all(
    github: GitHubClient, notion: NotionClient, settings: SyncSettings, now: str
) -> SyncReport:
    """전체 Issue와 Project 상태를 다시 맞춘다. 누락 이벤트 복구와 예약 실행에 쓴다.

    Args:
        github: GitHub 클라이언트.
        notion: Notion 클라이언트.
        settings: 실행 설정.
        now: Synced At에 쓸 UTC 시각.

    Returns:
        Issue별 결과, GitHub에 없는 페이지(orphan), fatal 사유를 담은 보고.
    """
    dry_run = not settings.write_enabled
    try:
        types = _check_schema(notion)
        issues = github.list_issues()
        index = github.load_project_index()
        meta_index = github.load_issue_meta_index()
        pages: dict[str, list[NotionPage]] = defaultdict(list)
        for page in notion.list_pages(settings.repository):
            pages[page.sync_key].append(page)
        results = []
        for issue in issues:
            project = PROJECT_ERROR if index is None else index.get(issue.node_id, NOT_IN_PROJECT)
            meta = META_ERROR if meta_index is None else meta_index.get(issue.node_id, META_ERROR)
            existing = pages.get(sync_key(issue), [])
            results.append(_safe_sync(issue, project, meta, existing, notion, types, settings, now))
        known = {sync_key(issue) for issue in issues}
        unknown = [key for key in pages if key not in known]
        # Sync Key는 Notion에서 사람이 고칠 수 있으므로 형식이 맞는 값만 공개 로그에 쓴다.
        pattern = re.compile(re.escape(settings.repository) + r"#[0-9]+")
        orphans = tuple(sorted(key for key in unknown if pattern.fullmatch(key)))
        return SyncReport(dry_run, tuple(results), orphans, len(unknown) - len(orphans))
    except SchemaError as error:
        return SyncReport(dry_run, fatal=str(error))
    except (ApiError, TransportError, UncertainWriteError) as error:
        return SyncReport(dry_run, fatal=_describe(error))
    except _SHAPE_ERRORS:
        return SyncReport(dry_run, fatal="unexpected_response")


# --- 설정과 CLI ------------------------------------------------------------


def load_settings(env: Mapping[str, str], dry_run: bool) -> SyncSettings:
    """환경 변수를 검증한다.

    Args:
        env: 환경 변수.
        dry_run: True면 쓰기를 항상 끈다.

    Returns:
        검증된 설정.

    Raises:
        ConfigError: 누락·형식 오류. 메시지에는 변수 이름만 담는다.
    """
    errors: list[str] = []
    repository = env.get("GITHUB_REPOSITORY", "")
    if not _REPOSITORY_PATTERN.fullmatch(repository):
        errors.append("GITHUB_REPOSITORY")
    if not _DATA_SOURCE_PATTERN.fullmatch(env.get("NOTION_DATA_SOURCE_ID", "")):
        errors.append("NOTION_DATA_SOURCE_ID")
    for name in ("NOTION_SYNC_TOKEN", "GITHUB_TOKEN"):
        if not env.get(name):
            errors.append(name)
    if env.get("PROJECT_NUMBER") and not _NUMBER_PATTERN.fullmatch(env["PROJECT_NUMBER"]):
        errors.append("PROJECT_NUMBER")
    authors = frozenset(
        a.strip().lower() for a in env.get("NOTION_SYNC_ALLOWED_ACTORS", "").split(",") if a.strip()
    )
    write_enabled = env.get("NOTION_SYNC_ENABLED") == "true" and not dry_run
    if write_enabled and not authors:
        errors.append("NOTION_SYNC_ALLOWED_ACTORS")
    if errors:
        raise ConfigError("missing or invalid: " + ", ".join(errors))
    return SyncSettings(repository, authors, write_enabled)


def _parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GitHub Issues/Projects → Notion one-way sync")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--issue", type=int, help="Issue number to sync")
    target.add_argument("--all", action="store_true", help="Sync every issue")
    parser.add_argument("--dry-run", action="store_true", help="Read only; never write to Notion")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, env: Mapping[str, str] | None = None) -> int:
    """CLI 진입점. 0=성공, 1=동기화 실패·확인 필요, 2=설정 오류."""
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    env = os.environ if env is None else env
    try:
        settings = load_settings(env, args.dry_run)
    except ConfigError as error:
        print(f"Configuration FAIL: {error}")
        return 2
    project_number = env.get("PROJECT_NUMBER")
    github = GitHubClient(
        JsonApi(GITHUB_API_URL, github_headers(env["GITHUB_TOKEN"])),
        settings.repository,
        int(project_number) if project_number else None,
    )
    notion = NotionClient(
        JsonApi(NOTION_API_URL, notion_headers(env["NOTION_SYNC_TOKEN"])),
        env["NOTION_DATA_SOURCE_ID"],
    )
    now = datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")
    try:
        if args.issue is not None:
            report = run_issue(args.issue, github, notion, settings, now)
        else:
            report = run_all(github, notion, settings, now)
    except Exception as error:  # noqa: BLE001 - 공개 로그에 traceback 대신 유형만 남긴다.
        report = SyncReport(not settings.write_enabled, fatal=type(error).__name__)
    if not settings.allowed_authors:
        warning = "NOTION_SYNC_ALLOWED_ACTORS is empty; every issue is skipped"
        report = replace(report, warnings=(*report.warnings, warning))
    summary = report.to_markdown()
    print(summary)
    if summary_path := env.get("GITHUB_STEP_SUMMARY"):
        with open(summary_path, "a", encoding="utf-8") as stream:
            stream.write(summary)
    return report.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
