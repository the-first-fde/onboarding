import json
from urllib.parse import parse_qs, urlparse

import pytest
from collaboration.http_api import (
    ApiError,
    AuthError,
    HttpRequest,
    HttpResponse,
    JsonApi,
    TransportError,
    UncertainWriteError,
    urllib_transport,
)
from collaboration.notion_client import NOTION_VERSION, NotionClient, notion_headers

DATA_SOURCE = "0123456789abcdef0123456789abcdef"


class Scripted:
    """준비된 응답 또는 예외를 순서대로 돌려주는 transport."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.requests: list[HttpRequest] = []

    def __call__(self, request):
        self.requests.append(request)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def payload(self, index):
        return json.loads(self.requests[index].body or b"{}")


def reply(status=200, body=None, headers=None):
    raw = json.dumps(body).encode() if body is not None else b""
    return HttpResponse(status, headers or {}, raw)


def api(transport, sleeps=None):
    sleep = sleeps.append if sleeps is not None else (lambda _: None)
    return JsonApi("https://api.notion.com/v1", notion_headers("fake"), transport, sleep)


def client(*outcomes):
    transport = Scripted(*outcomes)
    return NotionClient(api(transport), DATA_SOURCE), transport


# --- 재시도·오류 처리(http_api) -----------------------------------------------


def test_rate_limit_respects_retry_after_then_succeeds():
    sleeps = []
    transport = Scripted(reply(429, {"code": "rate_limited"}, {"retry-after": "7"}), reply())

    api(transport, sleeps).request("POST", "/pages", {}, idempotent=False)

    assert sleeps == [7.0]


def test_rate_limit_retry_is_bounded_and_capped():
    sleeps = []
    transport = Scripted(*[reply(429, {}, {"retry-after": "99999"})] * 4)

    with pytest.raises(ApiError) as error:
        api(transport, sleeps).request("GET", "/x", idempotent=True)

    assert error.value.status == 429
    assert sleeps == [60.0, 60.0, 60.0]


@pytest.mark.parametrize("status", [401, 403])
def test_auth_errors_fail_immediately(status):
    sleeps = []

    with pytest.raises(AuthError):
        api(Scripted(reply(status, {"code": "unauthorized"})), sleeps).request(
            "GET", "/x", idempotent=True
        )

    assert sleeps == []


def test_validation_error_keeps_code_but_hides_message():
    transport = Scripted(reply(400, {"code": "validation_error", "message": "issue text"}))

    with pytest.raises(ApiError) as error:
        api(transport).request("PATCH", "/x", {}, idempotent=False)

    assert error.value.code == "validation_error"
    assert "issue text" not in str(error.value)


def test_transient_error_on_read_is_retried_with_growing_backoff():
    sleeps = []
    transport = Scripted(reply(502), reply(503), reply(200, {"ok": 1}))

    assert api(transport, sleeps).request("GET", "/x", idempotent=True) == {"ok": 1}
    assert len(sleeps) == 2
    assert sleeps[0] < sleeps[1]


@pytest.mark.parametrize("failure", [reply(503), TransportError("timeout")])
def test_failed_write_is_uncertain_and_not_repeated(failure):
    transport = Scripted(failure)

    with pytest.raises(UncertainWriteError):
        api(transport).request("POST", "/pages", {}, idempotent=False)

    assert len(transport.requests) == 1


def test_network_failure_on_read_is_retried_then_raised():
    transport = Scripted(*[TransportError("timeout")] * 4)

    with pytest.raises(TransportError):
        api(transport).request("GET", "/x", idempotent=True)

    assert len(transport.requests) == 4


def test_github_secondary_rate_limit_403_with_retry_after_is_retried():
    sleeps = []
    transport = Scripted(reply(403, {}, {"retry-after": "2"}), reply())

    api(transport, sleeps).request("GET", "/x", idempotent=True)

    assert sleeps == [2.0]


def test_invalid_json_is_api_error():
    with pytest.raises(ApiError) as error:
        api(Scripted(HttpResponse(200, {}, b"<html>"))).request("GET", "/x", idempotent=True)

    assert error.value.code == "invalid_json"


def test_requests_outside_api_host_or_without_https_are_rejected():
    with pytest.raises(ValueError):
        api(Scripted()).request("GET", "https://evil.test/x", idempotent=True)
    with pytest.raises(ValueError):
        urllib_transport(HttpRequest("GET", "http://api.notion.com/v1", {}))


# --- Notion endpoints ----------------------------------------------------


def rich(value):
    return {"rich_text": [{"plain_text": value}]}


def page(page_id, key, sync_hash="h1"):
    return {"id": page_id, "properties": {"Sync Key": rich(key), "Sync Hash": rich(sync_hash)}}


def test_headers_pin_api_version():
    headers = notion_headers("t")

    assert headers["Notion-Version"] == NOTION_VERSION == "2026-03-11"
    assert headers["Authorization"] == "Bearer t"


def test_get_property_types_reads_data_source_schema():
    notion, transport = client(reply(body={"properties": {"Title": {"type": "title"}}}))

    assert notion.get_property_types() == {"Title": "title"}
    assert transport.requests[0].url.endswith(f"/data_sources/{DATA_SOURCE}")


def test_find_pages_filters_by_sync_key():
    notion, transport = client(reply(body={"results": [page("p1", "repo#1")], "has_more": False}))

    pages = notion.find_pages("repo#1")

    assert [(p.page_id, p.sync_key, p.sync_hash) for p in pages] == [("p1", "repo#1", "h1")]
    assert transport.requests[0].url.endswith(f"/data_sources/{DATA_SOURCE}/query")
    assert transport.payload(0)["filter"] == {
        "property": "Sync Key",
        "rich_text": {"equals": "repo#1"},
    }


def test_list_pages_paginates_with_cursor():
    notion, transport = client(
        reply(body={"results": [page("p1", "r#1")], "has_more": True, "next_cursor": "c2"}),
        reply(body={"results": [page("p2", "r#2")], "has_more": False}),
    )

    assert [p.page_id for p in notion.list_pages("r")] == ["p1", "p2"]
    assert "start_cursor" not in transport.payload(0)
    assert transport.payload(1)["start_cursor"] == "c2"
    assert transport.payload(0)["filter"]["property"] == "Repository"


def test_create_page_uses_data_source_parent():
    notion, transport = client(reply(body={"id": "new"}))

    assert notion.create_page({"Title": {}}, [{"type": "toggle"}]) == "new"
    assert transport.payload(0)["parent"] == {
        "type": "data_source_id",
        "data_source_id": DATA_SOURCE,
    }
    assert transport.payload(0)["children"] == [{"type": "toggle"}]


def test_update_page_patches_only_given_properties():
    notion, transport = client(reply(body={"id": "p1"}))

    notion.update_page("p1", {"Issue State": {"select": {"name": "Closed"}}})

    assert transport.requests[0].method == "PATCH"
    assert transport.requests[0].url.endswith("/pages/p1")
    assert transport.payload(0) == {"properties": {"Issue State": {"select": {"name": "Closed"}}}}


def test_block_children_list_delete_and_append():
    notion, transport = client(
        reply(body={"results": [{"id": "b1"}], "has_more": True, "next_cursor": "c2"}),
        reply(body={"results": [{"id": "b2"}], "has_more": False}),
        reply(body={}),
        reply(body={}),
    )

    assert [b["id"] for b in notion.list_children("p1")] == ["b1", "b2"]
    notion.delete_block("b1")
    notion.append_children("t1", [{"type": "paragraph"}])

    assert parse_qs(urlparse(transport.requests[1].url).query)["start_cursor"] == ["c2"]
    assert transport.requests[2].method == "DELETE"
    assert transport.requests[3].url.endswith("/blocks/t1/children")
    assert transport.payload(3) == {"children": [{"type": "paragraph"}]}


def test_urllib_transport_converts_http_and_network_errors(monkeypatch):
    import io
    import urllib.error
    from email.message import Message

    from collaboration import http_api

    headers = Message()
    headers["Retry-After"] = "3"

    def http_error(*args, **kwargs):
        raise urllib.error.HTTPError("https://x", 429, "limited", headers, io.BytesIO(b"{}"))

    monkeypatch.setattr(http_api._OPENER, "open", http_error)
    result = urllib_transport(HttpRequest("GET", "https://api.notion.com/v1/x", {}))
    assert (result.status, result.headers["retry-after"], result.body) == (429, "3", b"{}")

    def network_error(*args, **kwargs):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(http_api._OPENER, "open", network_error)
    with pytest.raises(TransportError):
        urllib_transport(HttpRequest("GET", "https://api.notion.com/v1/x", {}))


def test_redirect_is_not_followed_and_fails():
    transport = Scripted(reply(301, {}, {"location": "http://evil.test/"}))

    with pytest.raises(ApiError) as error:
        api(transport).request("GET", "/x", idempotent=True)

    assert error.value.code == "redirect_blocked"
    assert len(transport.requests) == 1


def test_urllib_opener_does_not_follow_redirects():
    from collaboration import http_api

    handler = http_api._NoRedirect()
    assert handler.redirect_request(None, None, 301, "moved", {}, "http://evil.test/") is None


def test_github_primary_rate_limit_is_not_reported_as_auth_failure():
    transport = Scripted(reply(403, {"message": "API rate limit"}, {"x-ratelimit-remaining": "0"}))

    with pytest.raises(ApiError) as error:
        api(transport).request("GET", "/x", idempotent=True)

    assert not isinstance(error.value, AuthError)
    assert error.value.code == "rate_limited"


def test_pagination_without_cursor_stops_with_error():
    notion, _ = client(reply(body={"results": [], "has_more": True, "next_cursor": None}))

    with pytest.raises(ApiError, match="missing_cursor"):
        notion.list_children("p1")
