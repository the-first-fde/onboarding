# LangGraph 워크플로우

[프로젝트 시작 안내](../../../README.md) · [공통 착수·완료 기준](../../../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

계획·진행·검토를 실행 순서로 연결하는 개발 위치다. 업무 문안이나 외부 도구 접속 대신 단계 이동과 상태 전달을 관리한다.

## 2. 무엇을 개발해야 하는가?

승인 후 계획과 진행 작업을 작은 노드로 나눈다. 검토 요청, 수정 후 재검토, 사람 판단 대기를 연결한다. 다음 노드의 실행 여부는 합의된 조건에 따라 정한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | 계획·진행 노드 | 계획 초안·진행 요약 | [계획 Spec](../../../docs/specs/onboarding-planning.md) |
| 정현 | 검토·수정 요청·승인 흐름 | 검토 결과와 흐름 검증 | [검토 Spec](../../../docs/specs/review-approval.md) |
| 종은 | 초안 생성 노드의 인터페이스 협의 | 입력·결과 전달 합의 | [안내 Spec](../../../docs/specs/communication-preparation.md) |

## 4. 개발에 필요한 기초 개념

노드는 한 단계, 엣지는 다음 단계와의 연결이다. State는 단계 사이에 전달하는 값이다. HITL은 사람이 결정을 내릴 때까지 실행을 보류하는 설계다.

## 5. 파일 및 모듈별 역할

[preparation_checklist/](preparation_checklist/README.md)는 담당별 준비 목록 생성·기준일 계산·표시 구간 분류를 담당하는 순수 함수 패키지다.

현재 폴더에는 README와 지침이 있다. 실행 예제는 [smoke.py](../smoke.py)의 run_smoke다. 승인 후 이곳에 업무 노드와 그래프 조립 코드를 책임별로 둔다.

## 6. 입력 및 출력 데이터

기술 예제는 카운터 0을 받아 1을 반환한다. 업무 입력은 승인된 계획 근거와 산출물이며, 출력은 다음 단계가 소비하는 처리 결과다. 실제 필드, 상태와 오류 규칙은 잠정 계약에서 확인한다.

## 7. 다른 모듈과의 관계

[SDK 연결](../agents/README.md)은 초안을 생성하고, [MCP 경계](../integrations/README.md)는 외부 응답을 제공할 수 있다. 예빈과 정현은 진행 상태와 승인 상태의 소유자가 겹치지 않도록 합의한다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. smoke.py에서 START → increment → END를 따라가고, 수정 요청 시 누가 무엇을 받아야 하는지 합의한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
import asyncio
from hr_onboarding.smoke import run_smoke


def graph_result() -> int:
    """기술 카운터 그래프를 실행한다.

    Returns:
        노드가 한 번 실행된 뒤의 카운터.
    """
    return asyncio.run(run_smoke())


assert graph_result() == 1
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 계획 또는 검토 노드의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “START에서 END까지 상태가 전달되는 방식를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 가상 노드의 로컬 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 계획·안내·승인 단계의 상태 전달에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “상태 변경 주체 충돌가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_graph_runs_without_network
```

카운터 검증 한 건이 통과해야 한다. 실패하면 노드 추가·엣지 순서와 반환값을 smoke.py에서 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 기술 그래프가 외부 호출 없이 동작한다.
- [ ] 업무 추가 시 승인 대기·수정·복구의 합의된 인수 조건을 각각 검증했다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 HR State, 승인 조건, 체크포인트 저장 방식은 보류 중이다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../../../docs/guides/README.md) · [데이터 확인 Issue 초안](../../../docs/issue-drafts/research-data-contract.md) · [계획 Spec](../../../docs/specs/onboarding-planning.md) · [검토 Spec](../../../docs/specs/review-approval.md) · [기술 설계](../../../docs/architecture.md) · [팀 LangGraph 안내](../../../docs/guides/workflow-guide.md) · [LangGraph 공식 문서](https://docs.langchain.com/oss/python/langgraph/overview)
