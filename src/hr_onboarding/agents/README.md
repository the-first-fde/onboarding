# Python Claude Agent SDK 연결

[프로젝트 시작 안내](../../../README.md) · [공통 착수·완료 기준](../../../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

업무 Markdown과 모델 실행을 연결하는 Python 경계다. 워크플로우가 호출 순서를 정하고 이 경계는 옵션과 결과를 관리한다.

## 2. 무엇을 개발해야 하는가?

승인 후 지정된 업무 Markdown을 골라 SDK 옵션을 구성하고, 결과·실패를 호출자에게 반환한다. 가장 작은 초안 하나부터 가상 응답으로 검증한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 종은 | 안내·준비 초안과 SDK 연결 | 생성 인터페이스와 가상 결과 검증 | [안내 Spec](../../../docs/specs/communication-preparation.md) |
| 예빈 | 계획 생성 인터페이스 협의 | 계획 입력과 반환값 요구 | [계획 Spec](../../../docs/specs/onboarding-planning.md) |
| 정현 | 검토 입출력 협의 | 검토·오류 전달 요구 | [검토 Spec](../../../docs/specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

SDK는 모델 에이전트 실행에 필요한 옵션과 호출 인터페이스를 제공하는 라이브러리다. 옵션 객체 생성만으로는 모델을 호출하지 않는다.

## 5. 파일 및 모듈별 역할

이 폴더에는 지침과 README가 있다. [smoke.py](../smoke.py)의 offline_options는 현재 기술 예제다. 승인 후 Markdown 선택과 SDK 응답 변환의 코드를 둔다.

## 6. 입력 및 출력 데이터

현재 입력은 고정된 안전 옵션이며 출력은 ClaudeAgentOptions 객체다. 향후 업무 입력과 반환 구조는 담당 Spec 및 잠정 계약을 확인한다.

## 7. 다른 모듈과의 관계

[업무 Markdown](../../../agents/README.md)을 읽고 [워크플로우](../workflows/README.md)에 결과를 돌려준다. 외부 도구는 [연동 경계](../integrations/README.md)의 정책을 따른다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. template.md의 역할과 제한을 읽고 옵션의 tools, mcp_servers, setting_sources가 비어 있는 이유를 확인한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
from claude_agent_sdk import ClaudeAgentOptions
from hr_onboarding.smoke import offline_options


def make_local_options() -> ClaudeAgentOptions:
    """인증 없는 기술 확인용 SDK 옵션을 만든다.

    Returns:
        기본 도구와 외부 서버를 사용하지 않는 SDK 옵션.
    """
    return offline_options()


assert make_local_options().tools == []
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 업무 Markdown과 SDK 연결의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “offline_options가 도구를 제한하는 방식를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 SDK 옵션과 가상 응답 경계의 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 런타임 Markdown과 워크플로우 반환 경계에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “비용·도구 허용 범위 불일치가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_sdk_options_do_not_enable_tools
```

SDK import와 옵션 검증 한 건이 통과해야 한다. 실패하면 잠금 버전과 옵션 구성을 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 인증이나 네트워크 없이 옵션을 검증했다.
- [ ] 업무 적용 시 정해진 권한과 결과·오류 인터페이스를 리뷰했다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 SDK query, API 키, 모델 비용, 도구 실행 권한은 현 단계 검증에서 제외한다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../../../docs/guides/README.md) · [데이터 확인 Issue 초안](../../../docs/issue-drafts/research-data-contract.md) · [안내 Spec](../../../docs/specs/communication-preparation.md) · [런타임 Markdown](../../../agents/README.md) · [Claude Agent SDK 공식 문서](https://code.claude.com/docs/en/agent-sdk/python)
