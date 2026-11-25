# MCP 연동

[프로젝트 시작 안내](../../../README.md) · [공통 착수·완료 기준](../../../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

승인된 외부 도구의 경계를 관리하는 위치다. SDK가 접근 요청을 전달하고 이 영역은 도구 결과나 오류를 처리한다.

## 2. 무엇을 개발해야 하는가?

승인 후 도구 결과를 내부 코드가 이해할 수 있게 변환하고 실패를 호출자에게 돌려준다. 기술 확인은 실제 전송 대신 가상 응답을 사용한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | 도구 응답 경계와 오류 처리 | 가상 도구 테스트·승인 범위 문서 | [초기화 Spec](../../../docs/specs/0001-bootstrap.md) |

## 4. 개발에 필요한 기초 개념

MCP는 모델과 외부 도구가 주고받는 요청·응답을 표준화한다. mock은 네트워크 없이 같은 호출 경계를 검증하기 위한 대역이다.

## 5. 파일 및 모듈별 역할

현재 폴더에는 지침과 README가 있으며 가상 예제는 [test_smoke.py](../../../tests/test_smoke.py)에 있다. 승인 후 연결 설정과 변환 코드를 별도 책임으로 둔다.

## 6. 입력 및 출력 데이터

기술 테스트는 도구 이름과 빈 인자를 넘겨 가상 CallToolResult를 받는다. 실제 도구 이름, 입력 필드와 응답 규약은 미정이다.

## 7. 다른 모듈과의 관계

[SDK](../agents/README.md)의 도구 경계와 [워크플로우](../workflows/README.md)의 실행 승인 조건에 의존한다. 담당자에게 필요한 읽기 범위와 안전한 오류 메시지를 확인한다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 기존 AsyncMock 테스트를 읽고 승인된 연동 범위, 도구 실패를 소비할 모듈과 출력 경계를 문서화한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
from mcp.types import CallToolResult, TextContent


def fake_response() -> CallToolResult:
    """MCP의 로컬 가상 응답을 만든다.

    Returns:
        외부 연결 없이 만든 기술 확인용 텍스트 응답.
    """
    return CallToolResult(
        content=[TextContent(type="text", text="technical mock")],
        is_error=False,
    )


assert not fake_response().is_error
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 도구 응답 변환의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “AsyncMock이 원격 도구를 대체하는 방식를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 가상 결과와 오류의 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 SDK·워크플로우가 받을 응답 또는 예외에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “도구 권한 경계 또는 외부 전송가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_mcp_mock_result_without_transport
```

mock 응답 한 건이 통과해야 한다. 실패하면 잠금 버전과 응답 속성 is_error를 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 정상 가상 응답을 확인했다.
- [ ] 연동 구현이 생기면 오류와 승인된 권한 범위를 각각 검증한다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 MCP 쓰기·인증 정보·고객사 데이터 사용은 금지된다. 실제 서비스 연동에는 별도 승인과 명세가 필요하다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../../../docs/guides/README.md) · [데이터 확인 Issue 초안](../../../docs/issue-drafts/research-data-contract.md) · [기술 설계](../../../docs/architecture.md) · [보안 가이드](../../../docs/guides/security-guide.md) · [MCP 공식 문서](https://modelcontextprotocol.io/docs/getting-started/intro)
