# 테스트 작성과 검증

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

변경이 기대 결과를 유지하는지 확인하는 위치다. 실행 코드는 src에 두고, 여기에는 그 결과를 검증하는 작은 시나리오를 둔다.

## 2. 무엇을 개발해야 하는가?

기술 테스트를 유지하고, 승인된 업무부터 정상·실패·권한 조건을 별도 테스트로 작성한다. 외부 호출은 mock으로 대체한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | test_smoke.py에서 그래프 테스트를 참고 | 계획·진행 테스트 | [계획 Spec](../docs/specs/onboarding-planning.md) |
| 종은 | Markdown·SDK 테스트를 참고 | 초안 경계 테스트 | [안내 Spec](../docs/specs/communication-preparation.md) |
| 정현 | 그래프·권한 실패 테스트를 참고 | 수정·승인 흐름 테스트 | [검토 Spec](../docs/specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

pytest는 test_로 시작하는 테스트를 찾는다. assert는 실제 결과가 기대 조건을 만족하는지 확인한다. fixture는 반복 입력을 제공한다.

## 5. 파일 및 모듈별 역할

[test_smoke.py](test_smoke.py)는 그래프·SDK·Markdown·MCP 가상 응답을 검사한다. [test_hooks.py](test_hooks.py)는 hook 판단을 검증한다. [conftest.py](conftest.py)는 테스트 중 소켓 연결을 차단한다. [collaboration/](collaboration)은 GitHub → Notion 동기화를 transport fake와 in-memory fake로 검증한다.

## 6. 입력 및 출력 데이터

현재 입력은 비식별 기술 문자열·카운터·가상 도구 요청이며 출력은 테스트 결과와 실패 근거다. 고객사 검증은 계약 확인 뒤 추가한다.

## 7. 다른 모듈과의 관계

[Python 패키지](../src/hr_onboarding/README.md)와 [hooks](../.claude/README.md)를 검증한다. 승인된 공통 가상 데이터는 [fixtures](../fixtures/README.md)에 둘 수 있다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 실행 결과 하나를 고르고 테스트명에 동작을 적는다. 실패 입력과 기대값을 먼저 정한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
from hr_onboarding.smoke import offline_options


def test_local_agent_has_no_tools() -> None:
    """인증 없는 기술 옵션에 도구가 없는지 확인한다."""
    assert offline_options().tools == []


test_local_agent_has_no_tools()
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 추가할 관찰 가능 테스트의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “conftest.py의 네트워크 차단과 현재 테스트를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 가상 입력과 명확한 실패 조건의 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 검증 변경이 CI와 fixtures에 주는 영향에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “실제 자료 없이는 기대값을 정할 수 없는 경우가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py
uv run --locked pytest -q tests/test_hooks.py
uv run --locked python scripts/verify.py
```

기술 테스트와 hook 테스트가 통과하고 verify가 coverage.xml을 생성한다. 실패하면 첫 테스트 이름과 실제 값을 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 업무마다 정상·실패 조건과 기대 결과가 구분된다.
- [ ] 기술 PASS와 고객사 업무 인수를 별도 기록했다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

고객사 자료·실제 인증·원격 MCP는 기본 테스트에서 사용하지 않는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [테스트 가이드](../docs/guides/testing-guide.md) · [가상 데이터 안내](../fixtures/README.md) · [pytest 공식 문서](https://docs.pytest.org/en/stable/getting-started.html)
