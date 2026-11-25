import json
from urllib.parse import parse_qs, urlparse

from collaboration.github_client import GitHubClient, ProjectFields, ProjectLookup
from collaboration.http_api import HttpResponse, JsonApi

REPO = "the-first-fde/onboarding"


def raw_issue(number, **overrides):
    issue = {
        "id": 1000 + number,
        "node_id": f"I_node{number}",
        "number": number,
        "title": f"Issue {number}",
        "body": "본문",
        "state": "open",
        "state_reason": None,
        "user": {"login": "member-a"},
        "assignees": [{"login": "member-b"}, {"login": "member-a"}],
        "labels": [{"name": "feature"}, {"name": "area:ci"}],
        "milestone": {"title": "SPRINT 1"},
        "html_url": f"https://github.com/{REPO}/issues/{number}",
        "created_at": "2026-11-20T01:00:00Z",
        "updated_at": "2026-11-21T01:00:00Z",
    }
    issue.update(overrides)
    return issue


def value(typename, field_name, **data):
    return {"__typename": typename, "field": {"name": field_name}, **data}


SCHEMA = [
    {"name": "Status", "dataType": "SINGLE_SELECT"},
    {"name": "Priority", "dataType": "SINGLE_SELECT"},
    {"name": "Size", "dataType": "SINGLE_SELECT"},
    {"name": "Estimate", "dataType": "NUMBER"},
    {"name": "Start date", "dataType": "DATE"},
    {"name": "Target date", "dataType": "DATE"},
    {"name": "Title", "dataType": "TITLE"},
]
SELECT = "ProjectV2ItemFieldSingleSelectValue"
FULL_VALUES = [
    value(SELECT, "Status", name="In progress"),
    value(SELECT, "Priority", name="P1"),
    value(SELECT, "Size", name="M"),
    value("ProjectV2ItemFieldNumberValue", "Estimate", number=3.0),
    value("ProjectV2ItemFieldDateValue", "Start date", date="2026-11-25"),
    value("ProjectV2ItemFieldDateValue", "Target date", date="2026-12-01"),
    {"__typename": "ProjectV2ItemFieldTextValue"},
]


def ok(body):
    return HttpResponse(200, {}, json.dumps(body).encode())


class GitHubFake:
    """REST 경로와 GraphQL 쿼리 종류로 응답을 고르는 가상 transport."""

    def __init__(self, issues=(), schema=SCHEMA, items=(), issue_items=(), truncated=False):
        self.issues = list(issues)
        self.schema = schema
        self.items = list(items)
        self.issue_items = list(issue_items)
        self.truncated = truncated
        self.drop_cursor = False
        self.graphql_errors = None
        self.requests = []

    def __call__(self, request):
        self.requests.append(request)
        url = urlparse(request.url)
        if url.path == "/graphql":
            return self._graphql(json.loads(request.body))
        if url.path.endswith("/issues"):
            query = parse_qs(url.query)
            page, size = int(query["page"][0]), int(query["per_page"][0])
            return ok(self.issues[(page - 1) * size : page * size])
        number = int(url.path.rsplit("/", 1)[1])
        return ok(next(i for i in self.issues if i["number"] == number))

    def _graphql(self, payload):
        if self.graphql_errors:
            return ok({"data": None, "errors": self.graphql_errors})
        query, variables = payload["query"], payload["variables"]
        project = {"fields": {"nodes": self.schema}}
        if "projectItems" in query:
            page_info = {"hasNextPage": self.truncated}
            issue = {"projectItems": {"pageInfo": page_info, "nodes": self.issue_items}}
            return ok({"data": {"repository": {"issue": issue}}})
        if "items(" in query:
            start = int(variables["cursor"] or 0)
            project["items"] = {
                "pageInfo": {
                    "hasNextPage": start + 2 < len(self.items),
                    "endCursor": None if self.drop_cursor else str(start + 2),
                },
                "nodes": self.items[start : start + 2],
            }
        return ok({"data": {"organization": {"projectV2": project}}})


def make_client(fake, project_number=1):
    api = JsonApi("https://api.github.com", {"Authorization": "Bearer fake"}, fake, lambda _: None)
    return GitHubClient(api, REPO, project_number)


def issue_item(values, number=1, archived=False):
    project = {"number": number, "owner": {"login": "the-first-fde"}}
    return {"isArchived": archived, "project": project, "fieldValues": {"nodes": values}}


def project_item(node_id, values, typename="Issue", repo=REPO, archived=False):
    content = {"__typename": typename}
    if typename == "Issue":
        content |= {"id": node_id, "repository": {"nameWithOwner": repo}}
    return {"isArchived": archived, "content": content, "fieldValues": {"nodes": values}}


def lookup_for(fake):
    client = make_client(fake)
    return client.get_project_result(client.get_issue(1))


# --- Issue -----------------------------------------------------------------


def test_get_issue_normalizes_latest_rest_data():
    fake = GitHubFake(issues=[raw_issue(7, state="closed", state_reason="not_planned")])

    issue = make_client(fake).get_issue(7)

    assert issue.issue_id == 1007
    assert issue.state_reason == "not_planned"
    assert issue.author == "member-a"
    assert issue.assignees == ("member-a", "member-b")
    assert issue.labels == ("area:ci", "feature")
    assert issue.milestone == "SPRINT 1"
    assert fake.requests[0].url.endswith(f"/repos/{REPO}/issues/7")


def test_get_issue_returns_none_for_pull_request():
    fake = GitHubFake(issues=[raw_issue(3, pull_request={"url": "x"})])

    assert make_client(fake).get_issue(3) is None


def test_list_issues_paginates_all_states_and_excludes_pull_requests():
    issues = [raw_issue(n) for n in range(1, 151)]
    issues[4] = raw_issue(5, pull_request={"url": "x"})
    fake = GitHubFake(issues=issues)

    result = make_client(fake).list_issues()

    assert len(result) == 149
    assert 5 not in {i.number for i in result}
    assert parse_qs(urlparse(fake.requests[0].url).query)["state"] == ["all"]
    assert len(fake.requests) == 2


# --- Project: Issue 하나 -----------------------------------------------------


def test_issue_project_fields_are_parsed():
    fake = GitHubFake(issues=[raw_issue(1)], issue_items=[issue_item(FULL_VALUES)])

    result = lookup_for(fake)

    assert result.lookup is ProjectLookup.OK
    assert result.fields == ProjectFields(
        status="In progress",
        priority="P1",
        size="M",
        estimate=3.0,
        start_date="2026-11-25",
        target_date="2026-12-01",
    )


def test_issue_only_in_other_or_archived_project_is_not_in_project():
    items = [issue_item(FULL_VALUES, number=9), issue_item(FULL_VALUES, archived=True)]
    fake = GitHubFake(issues=[raw_issue(1)], issue_items=items)

    assert lookup_for(fake).lookup is ProjectLookup.NOT_IN_PROJECT


def test_unknown_status_option_is_unmapped():
    items = [issue_item([value(SELECT, "Status", name="Blocked")])]
    fake = GitHubFake(issues=[raw_issue(1)], issue_items=items)

    result = lookup_for(fake)

    assert result.lookup is ProjectLookup.UNMAPPED
    assert result.fields.status == "Blocked"


def test_missing_project_number_is_project_error():
    fake = GitHubFake(issues=[raw_issue(1)])
    client = make_client(fake, project_number=None)

    assert client.get_project_result(client.get_issue(1)).lookup is ProjectLookup.ERROR


def test_organization_project_permission_error_is_project_error():
    fake = GitHubFake(issues=[raw_issue(1)])
    fake.graphql_errors = [{"type": "INSUFFICIENT_SCOPES", "message": "x"}]

    assert lookup_for(fake).lookup is ProjectLookup.ERROR


def test_missing_or_retyped_custom_field_is_project_error():
    schema = [f for f in SCHEMA if f["name"] != "Target date"]
    fake = GitHubFake(issues=[raw_issue(1)], schema=schema, issue_items=[issue_item(FULL_VALUES)])
    assert lookup_for(fake).lookup is ProjectLookup.ERROR

    schema.append({"name": "Target date", "dataType": "TEXT"})
    assert lookup_for(GitHubFake(issues=[raw_issue(1)], schema=schema)).lookup is (
        ProjectLookup.ERROR
    )


# --- Project: 전체 색인 -----------------------------------------------------


def test_project_index_paginates_and_excludes_pr_draft_other_repo_and_archived():
    items = [
        project_item("I_node1", FULL_VALUES),
        project_item("PR_1", FULL_VALUES, typename="PullRequest"),
        project_item("DI_1", FULL_VALUES, typename="DraftIssue"),
        project_item("I_other", FULL_VALUES, repo="the-first-fde/other"),
        project_item("I_node2", [], archived=True),
        project_item("I_node3", []),
    ]
    fake = GitHubFake(items=items)

    index = make_client(fake).load_project_index()

    assert set(index) == {"I_node1", "I_node3"}
    assert index["I_node1"].fields.status == "In progress"
    assert index["I_node3"].fields == ProjectFields()
    graphql_calls = [r for r in fake.requests if r.url.endswith("/graphql")]
    assert len(graphql_calls) == 4  # schema + 3 item pages


def test_project_index_failure_returns_none():
    fake = GitHubFake()
    fake.graphql_errors = [{"type": "FORBIDDEN", "message": "x"}]

    assert make_client(fake).load_project_index() is None


def test_truncated_project_list_without_target_is_error_not_cleared():
    fake = GitHubFake(issues=[raw_issue(1)], issue_items=[issue_item([], number=9)], truncated=True)

    assert lookup_for(fake).lookup is ProjectLookup.ERROR


def test_project_index_with_missing_cursor_stops_as_failure():
    fake = GitHubFake(items=[project_item(f"I_node{n}", []) for n in range(5)])
    fake.drop_cursor = True

    assert make_client(fake).load_project_index() is None


def test_unexpected_issue_list_shape_is_api_error():
    import pytest
    from collaboration.http_api import ApiError

    class ObjectInsteadOfList(GitHubFake):
        def __call__(self, request):
            return ok({"message": "unexpected"})

    with pytest.raises(ApiError, match="unexpected_shape"):
        make_client(ObjectInsteadOfList()).list_issues()
