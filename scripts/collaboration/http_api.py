"""GitHub·Notion 호출에 공통으로 쓰는 JSON HTTP 계층과 재시도 정책."""

from __future__ import annotations

import json
import random
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

REQUEST_TIMEOUT_SECONDS = 30
MAX_ATTEMPTS = 4
BASE_BACKOFF_SECONDS = 1.0
MAX_JITTER_SECONDS = 0.5
MAX_WAIT_SECONDS = 60.0
RATE_LIMIT_STATUSES = frozenset({429, 529})
TRANSIENT_STATUSES = frozenset({500, 502, 503, 504})
AUTH_STATUSES = frozenset({401, 403})


@dataclass(frozen=True)
class HttpRequest:
    """전송할 HTTP 요청."""

    method: str
    url: str
    headers: Mapping[str, str]
    body: bytes | None = None


@dataclass(frozen=True)
class HttpResponse:
    """수신한 HTTP 응답. header 이름은 소문자다."""

    status: int
    headers: Mapping[str, str]
    body: bytes


Transport = Callable[[HttpRequest], HttpResponse]
Sleep = Callable[[float], None]


class ApiError(Exception):
    """재시도로 해결되지 않았거나 재시도 대상이 아닌 API 오류.

    응답 본문의 message는 Issue 내용 등을 되돌려줄 수 있어 보관하지 않는다.
    """

    def __init__(self, status: int, code: str) -> None:
        """상태 코드와 API 오류 코드로 오류를 만든다."""
        super().__init__(f"HTTP {status} ({code})")
        self.status = status
        self.code = code


class AuthError(ApiError):
    """인증 실패 또는 권한 부족(401/403)."""


class TransportError(Exception):
    """네트워크 연결 실패 또는 타임아웃."""


class UncertainWriteError(Exception):
    """쓰기 요청이 서버에 반영됐는지 알 수 없는 상태."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """3xx를 따라가지 않는다. 따라가면 Authorization header가 다른 주소로 전달될 수 있다."""

    def redirect_request(self, *args: Any, **kwargs: Any) -> None:
        """Redirect 요청을 만들지 않아 3xx가 HTTPError 응답으로 남게 한다."""
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def urllib_transport(request: HttpRequest) -> HttpResponse:
    """표준 라이브러리 urllib으로 HTTPS 요청을 보낸다. redirect는 따라가지 않는다.

    Args:
        request: 보낼 요청. HTTPS URL만 허용한다.

    Returns:
        상태 코드와 무관하게 수신한 응답.

    Raises:
        ValueError: HTTPS가 아닌 URL.
        TransportError: 연결 실패나 타임아웃.
    """
    if not request.url.startswith("https://"):
        raise ValueError("Only HTTPS URLs are allowed")
    raw = urllib.request.Request(  # noqa: S310 - 위에서 https 스킴만 허용한다.
        request.url, data=request.body, headers=dict(request.headers), method=request.method
    )
    try:
        with _OPENER.open(raw, timeout=REQUEST_TIMEOUT_SECONDS) as reply:
            return HttpResponse(reply.status, _lower(reply.headers.items()), reply.read())
    except urllib.error.HTTPError as error:
        return HttpResponse(error.code, _lower(error.headers.items()), error.read())
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise TransportError(type(error).__name__) from error


def _lower(items: Iterable[tuple[str, str]]) -> dict[str, str]:
    return {name.lower(): value for name, value in items}


@dataclass(frozen=True)
class JsonApi:
    """한 API 호스트에 대한 JSON 요청과 제한적 재시도.

    Attributes:
        base_url: `https://` 로 시작하는 API 기본 주소.
        headers: 모든 요청에 붙일 header. 로그에 출력하지 않는다.
        transport: 실제 전송 함수. 테스트에서 fake로 교체한다.
        sleep: 대기 함수. 테스트에서 기록용 함수로 교체한다.
    """

    base_url: str
    headers: Mapping[str, str]
    transport: Transport = urllib_transport
    sleep: Sleep = time.sleep

    def request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
        *,
        idempotent: bool,
    ) -> Any:
        """JSON 요청을 보내고 응답 객체를 반환한다.

        429/529는 Retry-After를 존중해 재시도한다. 5xx와 네트워크 오류는 idempotent
        요청만 지수 backoff로 재시도하고, 쓰기 요청은 중복 반영을 막기 위해 즉시
        UncertainWriteError로 알린다.

        Args:
            method: HTTP method.
            path: base_url 뒤의 경로 또는 base_url로 시작하는 절대 주소.
            payload: JSON body.
            idempotent: 같은 요청을 반복해도 결과가 같으면 True.

        Returns:
            디코딩한 JSON 값(object 또는 array). 본문이 없으면 빈 dict.

        Raises:
            ValueError: base_url 밖의 절대 주소.
            AuthError: 401/403.
            ApiError: 그 밖의 실패 또는 재시도 소진.
            TransportError: idempotent 요청의 네트워크 오류 재시도 소진.
            UncertainWriteError: 쓰기 요청의 반영 여부를 알 수 없음.
        """
        request = self._build(method, path, payload)
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                response = self.transport(request)
            except TransportError as error:
                if not idempotent:
                    raise UncertainWriteError(str(error)) from error
                if attempt == MAX_ATTEMPTS:
                    raise
                self.sleep(_backoff(attempt))
                continue
            if 200 <= response.status < 300:
                return _decode(response)
            wait = _retry_wait(response, attempt, idempotent)
            if wait is None or attempt == MAX_ATTEMPTS:
                raise _to_error(response, idempotent)
            self.sleep(wait)
        raise AssertionError("unreachable")

    def _build(self, method: str, path: str, payload: Mapping[str, Any] | None) -> HttpRequest:
        if path.startswith("https://") and not path.startswith(self.base_url + "/"):
            raise ValueError("Absolute URL outside the configured API host")
        url = path if path.startswith("https://") else self.base_url + path
        headers = dict(self.headers)
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        return HttpRequest(method=method, url=url, headers=headers, body=body)


def _backoff(attempt: int) -> float:
    jitter = random.uniform(0, MAX_JITTER_SECONDS)  # noqa: S311 - 보안 용도가 아닌 재시도 분산.
    return min(MAX_WAIT_SECONDS, BASE_BACKOFF_SECONDS * 2 ** (attempt - 1) + jitter)


def _retry_after(response: HttpResponse) -> float | None:
    value = response.headers.get("retry-after")
    if value is None:
        return None
    try:
        return min(MAX_WAIT_SECONDS, max(0.0, float(value)))
    except ValueError:
        return None


def _retry_wait(response: HttpResponse, attempt: int, idempotent: bool) -> float | None:
    retry_after = _retry_after(response)
    if response.status in RATE_LIMIT_STATUSES:
        return retry_after if retry_after is not None else _backoff(attempt)
    if response.status == 403 and retry_after is not None:
        return retry_after  # GitHub secondary rate limit
    if response.status in TRANSIENT_STATUSES and idempotent:
        return _backoff(attempt)
    return None


def _error_code(response: HttpResponse) -> str:
    try:
        data = json.loads(response.body or b"{}")
    except ValueError:
        return "http_error"
    code = data.get("code") if isinstance(data, dict) else None
    return code if isinstance(code, str) and code.isidentifier() else "http_error"


def _to_error(response: HttpResponse, idempotent: bool) -> Exception:
    if response.status in TRANSIENT_STATUSES and not idempotent:
        return UncertainWriteError(f"HTTP {response.status}")
    if 300 <= response.status < 400:
        return ApiError(response.status, "redirect_blocked")
    if response.headers.get("x-ratelimit-remaining") == "0":
        return ApiError(response.status, "rate_limited")  # GitHub primary rate limit
    code = _error_code(response)
    if response.status in AUTH_STATUSES:
        return AuthError(response.status, code)
    return ApiError(response.status, code)


def _decode(response: HttpResponse) -> Any:
    if not response.body:
        return {}
    try:
        return json.loads(response.body)
    except ValueError as error:
        raise ApiError(response.status, "invalid_json") from error
