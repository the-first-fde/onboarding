"""Notion Data Source의 페이지·블록을 다루는 최소 클라이언트(API 2026-03-11)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

from collaboration.http_api import ApiError, JsonApi

NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"
NOTION_PAGE_SIZE = 100
# 무한 페이지네이션 방지 상한(100 x 100 = 10,000건). Data Source query 한도와 같다.
MAX_PAGES = 100


def notion_headers(token: str) -> dict[str, str]:
    """Notion API 공통 header를 만든다. 반환값은 로그에 출력하지 않는다."""
    return {"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION}


@dataclass(frozen=True)
class NotionPage:
    """동기화 판단에 필요한 Notion 페이지 정보."""

    page_id: str
    sync_key: str
    sync_hash: str
    body_hash: str


def _plain(prop: dict[str, Any] | None) -> str:
    parts = (prop or {}).get("rich_text") or []
    return "".join(p.get("plain_text", (p.get("text") or {}).get("content", "")) for p in parts)


def _to_page(raw: dict[str, Any]) -> NotionPage:
    props = raw.get("properties") or {}
    return NotionPage(
        page_id=str(raw["id"]),
        sync_key=_plain(props.get("Sync Key")),
        sync_hash=_plain(props.get("Sync Hash")),
        body_hash=_plain(props.get("Body Hash")),
    )


class NotionClient:
    """한 Data Source에 대한 조회·생성·갱신을 수행한다."""

    def __init__(self, api: JsonApi, data_source_id: str) -> None:
        """클라이언트를 만든다.

        Args:
            api: Notion Integration 토큰으로 인증한 API.
            data_source_id: 검증된 Data Source ID(Database ID와 다르다).
        """
        self._api = api
        self._data_source_id = data_source_id

    def get_property_types(self) -> dict[str, str]:
        """Data Source 스키마의 속성 이름 → 유형을 반환한다."""
        raw = self._api.request("GET", f"/data_sources/{self._data_source_id}", idempotent=True)
        return {name: str(prop["type"]) for name, prop in (raw.get("properties") or {}).items()}

    def find_pages(self, sync_key: str) -> list[NotionPage]:
        """Sync Key가 같은 페이지를 모두 반환한다."""
        return self._query({"property": "Sync Key", "rich_text": {"equals": sync_key}})

    def list_pages(self, repository: str) -> list[NotionPage]:
        """Repository에 속한 페이지 전체를 페이지네이션하며 반환한다."""
        return self._query({"property": "Repository", "rich_text": {"equals": repository}})

    def create_page(self, properties: dict[str, Any], children: list[dict[str, Any]]) -> str:
        """Data Source 아래 페이지를 만든다. 재시도하지 않는 쓰기다."""
        payload = {
            "parent": {"type": "data_source_id", "data_source_id": self._data_source_id},
            "properties": properties,
            "children": children,
        }
        return str(self._api.request("POST", "/pages", payload, idempotent=False)["id"])

    def update_page(self, page_id: str, properties: dict[str, Any]) -> None:
        """주어진 속성만 덮어쓴다. 같은 값을 반복 적용해도 결과가 같다."""
        self._api.request(
            "PATCH", f"/pages/{quote(page_id)}", {"properties": properties}, idempotent=True
        )

    def list_children(self, block_id: str) -> list[dict[str, Any]]:
        """블록(또는 페이지)의 직계 자식 블록 전체를 반환한다."""
        blocks: list[dict[str, Any]] = []
        cursor: str | None = None
        for _ in range(MAX_PAGES):
            path = f"/blocks/{quote(block_id)}/children?page_size={NOTION_PAGE_SIZE}"
            if cursor:
                path += f"&start_cursor={quote(cursor)}"
            raw = self._api.request("GET", path, idempotent=True)
            blocks.extend(raw.get("results") or [])
            if not raw.get("has_more"):
                return blocks
            cursor = _next_cursor(raw)
        raise ApiError(200, "too_many_pages")

    def delete_block(self, block_id: str) -> None:
        """블록을 휴지통으로 옮긴다."""
        self._api.request("DELETE", f"/blocks/{quote(block_id)}", idempotent=True)

    def append_children(self, block_id: str, children: list[dict[str, Any]]) -> None:
        """블록 끝에 자식 블록을 추가한다. 재시도하지 않는 쓰기다."""
        self._api.request(
            "PATCH",
            f"/blocks/{quote(block_id)}/children",
            {"children": children},
            idempotent=False,
        )

    def _query(self, filter_: dict[str, Any]) -> list[NotionPage]:
        pages: list[NotionPage] = []
        payload: dict[str, Any] = {"filter": filter_, "page_size": NOTION_PAGE_SIZE}
        for _ in range(MAX_PAGES):
            raw = self._api.request(
                "POST", f"/data_sources/{self._data_source_id}/query", payload, idempotent=True
            )
            pages.extend(_to_page(r) for r in raw.get("results") or [])
            if not raw.get("has_more"):
                return pages
            payload = {**payload, "start_cursor": _next_cursor(raw)}
        raise ApiError(200, "too_many_pages")


def _next_cursor(raw: dict[str, Any]) -> str:
    cursor = raw.get("next_cursor")
    if not isinstance(cursor, str) or not cursor:
        raise ApiError(200, "missing_cursor")
    return cursor
