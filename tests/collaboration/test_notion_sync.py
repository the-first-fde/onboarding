import subprocess

import pytest
from collaboration.github_client import (
    IssueMetaLookup, IssueMetaResult, ProjectFields, ProjectLookup, ProjectResult,
)
from collaboration.http_api import ApiError
from collaboration.notion_sync import (
    BODY_MARKER,
    MAX_BODY_BLOCKS,
    ConfigError,
    SyncOutcome,
    SyncSettings,
    body_blocks,
    build_properties,
    content_hash,
    load_settings,
    main,
    run_all,
    run_issue,
    sync_key,
)
from fakes import REPO, make_issue, plain

NOW = "2026-11-25T09:00:00Z"
ALLOWED = frozenset({"member-a", "member-b", "member-c"})
URL = f"https://github.com/{REPO}/issues/1"


def settings(write=True):
    return SyncSettings(repository=REPO, allowed_authors=ALLOWED, write_enabled=write)


def sync_one(github, notion, number=1, write=True):
    return run_issue(number, github, notion, settings(write), NOW)


def sync_all(github, notion, write=True):
    return run_all(github, notion, settings(write), NOW)


def outcome(report, number=1):
    return next(r for r in report.results if r.number == number).outcome


def block_text(block):
    return "".join(p["text"]["content"] for p in block[block["type"]]["rich_text"])


def body_text(page):
    toggle = next(b for b in page["blocks"] if b["type"] == "toggle")
    return [block_text(child) for child in toggle["_children"]]


def prop(notion, name):
    return notion.only_page()["properties"][name]


# --- 매핑 -----------------------------------------------------------------

FIELDS = ProjectFields(
    status="In review",
    size="S",
    estimate=2.0,
    start_date="2026-11-25",
    target_date="2026-12-01",
)


def test_sync_key_uses_repository_and_stable_issue_id():
    assert sync_key(make_issue(1)) == f"{REPO}#1001"


def test_properties_map_issue_and_project_fields():
    props = build_properties(
        make_issue(1), ProjectResult(ProjectLookup.OK, FIELDS), IssueMetaResult(IssueMetaLookup.OK)
    )

    assert props["Title"]["title"][0]["text"]["content"] == "Issue 1"
    assert props["Issue Number"] == {"number": 1}
    assert props["Issue State"] == {"select": {"name": "Open"}}
    assert props["Close Reason"] == {"select": None}
    assert props["Labels"] == {"multi_select": [{"name": "feature"}]}
    assert props["Project Status"] == {"select": {"name": "In review"}}
    assert props["Size"] == {"select": {"name": "S"}}
    assert props["Estimate"] == {"number": 2.0}
    assert props["Target Date"] == {"date": {"start": "2026-12-01"}}
    assert props["Project Sync State"] == {"select": {"name": "ok"}}
    assert "Notes" not in props


def test_project_error_omits_project_properties():
    props = build_properties(
        make_issue(1), ProjectResult(ProjectLookup.ERROR), IssueMetaResult(IssueMetaLookup.OK)
    )

    for name in ("Project Status", "Size", "Estimate", "Start Date", "Target Date"):
        assert name not in props


def test_text_is_bounded_and_commas_removed_from_options():
    props = build_properties(
        make_issue(1, title="t" * 5000, labels=("a,b",)),
        ProjectResult(ProjectLookup.OK),
        IssueMetaResult(IssueMetaLookup.OK),
    )

    assert len(props["Title"]["title"][0]["text"]["content"]) == 2000
    assert props["Labels"] == {"multi_select": [{"name": "a b"}]}


def test_content_hash_is_order_independent():
    assert content_hash({"a": 1, "b": [1]}) == content_hash({"b": [1], "a": 1})
    assert content_hash({"a": 1}) != content_hash({"a": 2})


def test_body_becomes_plain_paragraphs_without_links():
    blocks = body_blocks("# 제목\n- 항목\n\n[click](https://evil.test) <b>x</b>", URL)

    assert [block_text(b) for b in blocks] == [
        "# 제목\n- 항목",
        "[click](https://evil.test) <b>x</b>",
    ]
    assert all(b["type"] == "paragraph" for b in blocks)
    assert "link" not in blocks[1]["paragraph"]["rich_text"][0]["text"]


def test_empty_body_has_placeholder():
    assert block_text(body_blocks("", URL)[0]) == "(본문 없음)"


def test_long_paragraph_is_split_into_rich_text_chunks():
    parts = body_blocks("가" * 4500, URL)[0]["paragraph"]["rich_text"]

    assert [len(p["text"]["content"]) for p in parts] == [2000, 2000, 500]


def test_too_many_paragraphs_are_truncated_with_github_link():
    blocks = body_blocks("\n\n".join(f"문단 {n}" for n in range(500)), URL)

    assert len(blocks) == MAX_BODY_BLOCKS + 1
    assert URL in block_text(blocks[-1])


# --- 생성·갱신·멱등성 ---------------------------------------------------------


def test_new_issue_creates_page_with_body_region(github, notion):
    github.add(make_issue(1, body="첫 본문"))
    github.set_project(1, status="Backlog")

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.CREATED
    page = notion.only_page()
    assert plain(page["properties"]["Sync Key"]) == f"{REPO}#1001"
    assert page["properties"]["Synced At"] == {"date": {"start": NOW}}
    assert block_text(page["blocks"][0]) == BODY_MARKER
    assert body_text(page) == ["첫 본문"]
    assert report.exit_code() == 0


def test_resync_without_changes_makes_no_writes(github, notion):
    github.add(make_issue(1))
    sync_one(github, notion)
    notion.writes.clear()

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.UNCHANGED
    assert notion.writes == []


@pytest.mark.parametrize(
    ("changes", "name", "expected"),
    [
        (
            {"title": "새 제목"},
            "Name",
            {"title": [{"type": "text", "text": {"content": "새 제목"}}]},
        ),
        (
            {"state": "closed", "state_reason": "completed"},
            "Issue State",
            {"select": {"name": "Closed"}},
        ),
        (
            {"state": "closed", "state_reason": "completed"},
            "Close Reason",
            {"select": {"name": "completed"}},
        ),
        (
            {"labels": ("bug", "docs")},
            "Labels",
            {"multi_select": [{"name": "bug"}, {"name": "docs"}]},
        ),
    ],
)
def test_issue_changes_update_existing_page(github, notion, changes, name, expected):
    github.add(make_issue(1))
    sync_one(github, notion)

    github.update(1, **changes)
    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.UPDATED
    assert prop(notion, name) == expected
    assert len(notion.pages) == 1


@pytest.mark.parametrize(
    ("changes", "name", "expected"),
    [
        ({"assignees": ("member-b", "member-c")}, "Assignees", "member-b, member-c"),
        ({"milestone": "SPRINT 2"}, "Milestone", "SPRINT 2"),
    ],
)
def test_assignee_and_milestone_changes(github, notion, changes, name, expected):
    github.add(make_issue(1))
    sync_one(github, notion)

    github.update(1, **changes)
    sync_one(github, notion)

    assert plain(prop(notion, name)) == expected


def test_reopen_returns_to_open_and_clears_reason(github, notion):
    github.add(make_issue(1, state="closed", state_reason="completed"))
    sync_one(github, notion)

    github.update(1, state="open", state_reason="reopened")
    sync_one(github, notion)

    assert prop(notion, "Issue State") == {"select": {"name": "Open"}}
    assert prop(notion, "Close Reason") == {"select": None}


def test_lost_create_response_is_rechecked_without_duplicate(github, notion):
    github.add(make_issue(1))
    notion.lose_next_create_response = True

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.CREATED
    assert notion.writes.count("create") == 1
    assert len(notion.pages) == 1


def test_duplicate_pages_are_reported_not_deleted(github, notion):
    github.add(make_issue(1))
    sync_one(github, notion)
    first = notion.only_page()
    notion.pages["dup"] = {"properties": dict(first["properties"]), "blocks": []}
    notion.writes.clear()

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.CONFLICT
    assert len(notion.pages) == 2
    assert notion.writes == []
    assert report.exit_code() == 1


# --- 사람 메모 보존 ----------------------------------------------------------


def test_body_update_preserves_human_notes_and_blocks(github, notion):
    github.add(make_issue(1, body="v1"))
    sync_one(github, notion)
    page_id = next(iter(notion.pages))
    notion.pages[page_id]["properties"]["Notes"] = {"rich_text": [{"text": {"content": "회의"}}]}
    notion.add_human_block(page_id, "사람이 쓴 회의록")

    github.update(1, body="v2")
    sync_one(github, notion)

    page = notion.pages[page_id]
    assert body_text(page) == ["v2"]
    assert plain(page["properties"]["Notes"]) == "회의"
    assert block_text(page["blocks"][1]) == "사람이 쓴 회의록"


def test_deleted_body_region_is_not_recreated_until_github_changes(github, notion):
    github.add(make_issue(1, body="v1"))
    sync_one(github, notion)
    notion.only_page()["blocks"] = []

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.UNCHANGED
    assert notion.only_page()["blocks"] == []


def test_deleted_body_region_is_recreated(github, notion):
    github.add(make_issue(1, body="v1"))
    sync_one(github, notion)
    notion.only_page()["blocks"] = []

    github.update(1, body="v2")
    sync_one(github, notion)

    assert body_text(notion.only_page()) == ["v2"]


# --- 대상 필터·쓰기 차단 -----------------------------------------------------


def test_pull_request_is_skipped(github, notion):
    github.add(make_issue(2))
    github.pull_requests.add(2)

    assert outcome(sync_one(github, notion, number=2), 2) is SyncOutcome.SKIPPED
    assert notion.writes == []


def test_dry_run_reports_plan_without_writes(github, notion):
    github.add(make_issue(1))

    report = sync_all(github, notion, write=False)

    assert outcome(report) is SyncOutcome.CREATED
    assert report.dry_run
    assert notion.writes == []
    assert "dry-run" in report.to_markdown()


def test_auth_failure_stops_run(github, notion):
    github.add(make_issue(1))
    notion.auth_fails = True

    report = sync_all(github, notion)

    assert report.fatal.startswith("AuthError")
    assert report.exit_code() == 1


def test_notion_schema_mismatch_stops_before_writes(github, notion):
    github.add(make_issue(1))
    notion.schema["Labels"] = "rich_text"

    report = sync_one(github, notion)

    assert "Labels" in report.fatal
    assert notion.writes == []


def test_hostile_issue_content_is_stored_as_data_only(github, notion, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("no subprocess")

    monkeypatch.setattr(subprocess, "run", forbidden)
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    hostile = "$(cat ~/.ssh/id_rsa) ${{ secrets.NOTION_SYNC_TOKEN }} `whoami`"
    github.add(make_issue(1, title=hostile, body=hostile))

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.CREATED
    assert body_text(notion.only_page()) == [hostile]
    assert hostile not in report.to_markdown()


# --- 전체 동기화 ------------------------------------------------------------


def test_full_sync_processes_all_and_reports_orphans(github, notion):
    for number in (1, 2, 3):
        github.add(make_issue(number))
    sync_all(github, notion)
    del github.issues[3]

    report = sync_all(github, notion)

    assert {r.number for r in report.results} == {1, 2}
    assert report.orphans == (f"{REPO}#1003",)
    assert len(notion.pages) == 3
    assert report.exit_code() == 0


def test_partial_failure_is_recorded_and_fails_run(github, notion, monkeypatch):
    github.add(make_issue(1))
    github.add(make_issue(2))
    original = notion.create_page

    def flaky(properties, children):
        if plain(properties["Sync Key"]).endswith("#1002"):
            raise ApiError(400, "validation_error")
        return original(properties, children)

    monkeypatch.setattr(notion, "create_page", flaky)

    report = sync_all(github, notion)

    assert outcome(report, 1) is SyncOutcome.CREATED
    assert outcome(report, 2) is SyncOutcome.FAILED
    assert "validation_error" in report.to_markdown()
    assert report.exit_code() == 1


# --- GitHub Projects -------------------------------------------------------


@pytest.mark.parametrize(
    ("change", "name", "expected"),
    [
        ({"status": "In progress"}, "Project Status", {"select": {"name": "In progress"}}),
        ({"track": "DevOps"}, "Track", {"select": {"name": "DevOps"}}),
        ({"size": "XL"}, "Size", {"select": {"name": "XL"}}),
        ({"estimate": 5.0}, "Estimate", {"number": 5.0}),
        ({"start_date": "2026-11-26"}, "Start Date", {"date": {"start": "2026-11-26"}}),
        ({"target_date": "2026-12-02"}, "Target Date", {"date": {"start": "2026-12-02"}}),
    ],
)
def test_scheduled_sync_reflects_project_only_changes(github, notion, change, name, expected):
    github.add(make_issue(1))
    github.set_project(1, status="Backlog")
    sync_all(github, notion)

    github.set_project(1, **change)
    report = sync_all(github, notion)

    assert outcome(report) is SyncOutcome.UPDATED
    assert prop(notion, name) == expected


def test_project_failure_preserves_existing_project_values(github, notion):
    github.add(make_issue(1))
    github.set_project(1, status="In review")
    github.set_meta(1, priority="P1")
    sync_all(github, notion)

    github.project_available = False
    github.update(1, title="변경")
    report = sync_all(github, notion)

    assert prop(notion, "Project Status") == {"select": {"name": "In review"}}
    assert prop(notion, "Priority") == {"select": {"name": "P1"}}
    assert prop(notion, "Project Sync State") == {"select": {"name": "error"}}
    assert report.exit_code() == 1


def test_unknown_status_is_reported_and_existing_status_kept(github, notion):
    github.add(make_issue(1))
    github.set_project(1, status="Ready")
    sync_one(github, notion)

    github.set_project(1, lookup=ProjectLookup.UNMAPPED, status="Blocked")
    github.set_meta(1, priority="P0")
    report = sync_one(github, notion)

    assert prop(notion, "Project Status") == {"select": {"name": "Ready"}}
    assert prop(notion, "Priority") == {"select": {"name": "P0"}}
    assert "unmapped" in report.to_markdown()
    assert report.exit_code() == 1


def test_issue_not_in_project_is_marked_and_cleared(github, notion):
    github.add(make_issue(1))

    report = sync_one(github, notion)

    assert prop(notion, "Project Sync State") == {"select": {"name": "not_in_project"}}
    assert prop(notion, "Project Status") == {"select": None}
    assert report.exit_code() == 0


def test_closed_issue_with_open_project_status_is_flagged_not_forced(github, notion):
    github.add(make_issue(1, state="closed", state_reason="completed"))
    github.set_project(1, status="In progress")

    report = sync_one(github, notion)

    assert prop(notion, "Project Status") == {"select": {"name": "In progress"}}
    assert report.results[0].detail == "state_mismatch"
    assert report.exit_code() == 0


# --- 설정·CLI ---------------------------------------------------------------

BASE_ENV = {
    "GITHUB_REPOSITORY": REPO,
    "NOTION_SYNC_ENABLED": "true",
    "NOTION_SYNC_ALLOWED_ACTORS": "Member-A, member-b ,",
    "NOTION_DATA_SOURCE_ID": "01234567-89ab-cdef-0123-456789abcdef",
    "NOTION_SYNC_TOKEN": "fake-notion",
    "GITHUB_TOKEN": "fake-github",
    "PROJECT_NUMBER": "1",
}


def test_settings_parse_allowlist_and_enable_flag():
    loaded = load_settings(BASE_ENV, dry_run=False)

    assert loaded.write_enabled
    assert loaded.allowed_authors == frozenset({"member-a", "member-b"})


@pytest.mark.parametrize("value", ["", "false", "TRUE", "1", "yes"])
def test_sync_is_disabled_unless_exactly_true(value):
    assert not load_settings(BASE_ENV | {"NOTION_SYNC_ENABLED": value}, dry_run=False).write_enabled


def test_dry_run_disables_writes_even_when_enabled():
    assert not load_settings(BASE_ENV, dry_run=True).write_enabled


def test_empty_allowlist_blocks_real_writes():
    with pytest.raises(ConfigError, match="NOTION_SYNC_ALLOWED_ACTORS"):
        load_settings(BASE_ENV | {"NOTION_SYNC_ALLOWED_ACTORS": " , "}, dry_run=False)


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("NOTION_DATA_SOURCE_ID", "../../pages/abc"),
        ("PROJECT_NUMBER", "one"),
        ("GITHUB_REPOSITORY", "not-a-repo"),
        ("NOTION_SYNC_TOKEN", ""),
    ],
)
def test_invalid_configuration_names_variable_without_values(name, value):
    with pytest.raises(ConfigError) as error:
        load_settings(BASE_ENV | {name: value}, dry_run=True)

    assert name in str(error.value)
    assert "fake" not in str(error.value)


def test_main_reports_config_error_without_network(capsys):
    assert main(["--all"], env={}) == 2
    assert "GITHUB_REPOSITORY" in capsys.readouterr().out


def test_main_writes_job_summary_without_secrets(tmp_path, monkeypatch, capsys):
    from collaboration import notion_sync
    from collaboration.notion_sync import SyncReport

    monkeypatch.setattr(notion_sync, "run_all", lambda *args: SyncReport(dry_run=True))
    summary = tmp_path / "summary.md"

    code = main(["--all", "--dry-run"], env=BASE_ENV | {"GITHUB_STEP_SUMMARY": str(summary)})

    assert code == 0
    written = summary.read_text(encoding="utf-8")
    assert "dry-run" in written
    assert "fake-" not in written + capsys.readouterr().out


# --- 리뷰 반영 회귀 테스트 ------------------------------------------------------


def test_unconfirmed_create_is_failed_without_second_create(github, notion):
    github.add(make_issue(1))
    notion.create_never_visible = True

    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.FAILED
    assert report.results[0].detail == "UncertainWriteError"
    assert notion.writes.count("create") == 1
    assert report.exit_code() == 1


def test_project_only_change_does_not_rewrite_body(github, notion):
    github.add(make_issue(1, body="\n\n".join(f"p{n}" for n in range(10))))
    github.set_project(1, status="Backlog")
    sync_all(github, notion)
    notion.writes.clear()

    github.set_project(1, status="Ready")
    sync_all(github, notion)

    assert notion.writes == ["update"]


def test_failed_property_update_after_body_replace_is_retried_next_run(github, notion):
    github.add(make_issue(1, body="v1"))
    sync_one(github, notion)
    github.update(1, body="v2")
    notion.fail_next_update = True

    assert outcome(sync_one(github, notion)) is SyncOutcome.FAILED
    notion.writes.clear()
    report = sync_one(github, notion)

    assert outcome(report) is SyncOutcome.UPDATED
    assert body_text(notion.only_page()) == ["v2"]
    assert "update" in notion.writes


def test_project_recovers_after_error(github, notion):
    github.add(make_issue(1))
    github.project_available = False
    sync_all(github, notion)
    assert "Project Status" not in notion.only_page()["properties"]

    github.project_available = True
    github.set_project(1, status="In review")
    report = sync_all(github, notion)

    assert prop(notion, "Project Status") == {"select": {"name": "In review"}}
    assert report.exit_code() == 0


def test_unallowed_author_is_skipped_before_project_and_notion_lookup(github, notion, monkeypatch):
    github.add(make_issue(1, author="outsider"))

    def forbidden(*args):
        raise AssertionError("must not be called")

    monkeypatch.setattr(github, "get_project_result", forbidden)
    monkeypatch.setattr(notion, "find_pages", forbidden)

    assert outcome(sync_one(github, notion)) is SyncOutcome.SKIPPED


def test_orphan_with_edited_sync_key_is_counted_not_printed(github, notion):
    github.add(make_issue(1))
    sync_all(github, notion)
    page = notion.only_page()
    page["properties"]["Sync Key"] = {
        "rich_text": [{"text": {"content": "![x](https://evil.test)"}}]
    }

    report = sync_all(github, notion)

    assert report.invalid_orphans == 1
    assert "evil.test" not in report.to_markdown()


def test_unexpected_response_shape_fails_issue_without_traceback(github, notion, monkeypatch):
    github.add(make_issue(1))

    def broken(*args):
        raise KeyError("id")

    monkeypatch.setattr(notion, "create_page", broken)

    report = sync_one(github, notion)

    assert report.results[0].detail == "unexpected_response"


def test_main_reports_unexpected_exception_as_fatal_type(monkeypatch, capsys):
    from collaboration import notion_sync

    def explode(*args):
        raise RuntimeError("detail with token-like text")

    monkeypatch.setattr(notion_sync, "run_all", explode)

    assert main(["--all", "--dry-run"], env=BASE_ENV) == 1
    out = capsys.readouterr().out
    assert "FATAL: RuntimeError" in out
    assert "token-like" not in out


def test_dry_run_with_empty_allowlist_warns(monkeypatch, capsys):
    from collaboration import notion_sync
    from collaboration.notion_sync import SyncReport

    monkeypatch.setattr(notion_sync, "run_all", lambda *args: SyncReport(dry_run=True))
    env = BASE_ENV | {"NOTION_SYNC_ALLOWED_ACTORS": ""}

    assert main(["--all", "--dry-run"], env=env) == 0
    assert "WARNING: NOTION_SYNC_ALLOWED_ACTORS is empty" in capsys.readouterr().out


def test_project_number_rejects_non_ascii_digits():
    with pytest.raises(ConfigError, match="PROJECT_NUMBER"):
        load_settings(BASE_ENV | {"PROJECT_NUMBER": "\u00b2"}, dry_run=True)


def test_F_059_AC_02_03_04_05_06_metadata_sync(github, notion):
    github.add(make_issue(1))
    github.set_meta(
        1, priority="P1", issue_type="Task", parent=26,
        sub_issues_total=2, sub_issues_completed=1, blocked_by=(43, 44),
    )
    assert outcome(sync_all(github, notion)) is SyncOutcome.CREATED
    assert prop(notion, "Priority") == {"select": {"name": "P1"}}
    assert plain(prop(notion, "Parent Issue")) == "#26"
    assert plain(prop(notion, "Sub-issues Progress")) == "1/2"
    assert plain(prop(notion, "Blocked By")) == "#43, #44"
    assert outcome(sync_all(github, notion)) is SyncOutcome.UNCHANGED
    github.meta_available = False
    report = sync_all(github, notion)
    assert report.exit_code() == 1
    assert prop(notion, "Priority") == {"select": {"name": "P1"}}
    assert prop(notion, "Issue Meta Sync State") == {"select": {"name": "error"}}
    github.meta_available = True
    github.set_meta(
        1, priority=None, priority_known=False, parent=None,
        sub_issues_total=0, sub_issues_completed=0, blocked_by=(),
    )
    sync_all(github, notion)
    assert prop(notion, "Priority") == {"select": {"name": "P1"}}
    assert plain(prop(notion, "Parent Issue")) == ""
    del notion.schema["Issue Type"]
    assert sync_all(github, notion).exit_code() == 0


def test_F_059_AC_07_new_schema_backfills(github, notion):
    github.add(make_issue(1))
    del notion.schema["Parent Issue"]
    github.set_meta(1, parent=26)
    sync_all(github, notion)
    notion.schema["Parent Issue"] = "rich_text"
    assert outcome(sync_all(github, notion)) is SyncOutcome.UPDATED
    assert plain(prop(notion, "Parent Issue")) == "#26"


@pytest.mark.parametrize("priority", ["P0", "P1", "P2", None])
def test_F_059_AC_01_04_priority_select_from_meta(priority):
    from collaboration.github_client import IssueMeta

    result = IssueMetaResult(IssueMetaLookup.OK, IssueMeta(priority=priority))
    props = build_properties(make_issue(1), ProjectResult(ProjectLookup.ERROR), result)
    assert props["Priority"] == {"select": {"name": priority} if priority else None}
