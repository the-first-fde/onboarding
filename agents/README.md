# 런타임 업무 Markdown

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

사람이 리뷰할 수 있는 업무 에이전트 정의를 두는 곳이다. Python 호출은 SDK 모듈이 담당한다.

## 2. 무엇을 개발해야 하는가?

승인 후 업무별 목적, 사용할 근거, 기대하는 산출물, 누락 시 질문, 승인 경계를 Markdown으로 작성한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | 계획·진행 업무 Markdown | 계획·진행 목적과 범위 | [계획 Spec](../docs/specs/onboarding-planning.md) |
| 종은 | 안내·준비 요청 업무 Markdown | 초안별 업무 정의 | [안내 Spec](../docs/specs/communication-preparation.md) |
| 정현 | 검토·수정 요청 업무 Markdown | 검토·사람 승인 경계 | [검토 Spec](../docs/specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

Markdown은 텍스트 문서 형식이다. 런타임 프롬프트는 에이전트의 역할과 금지 경계를 전달한다. 템플릿을 읽는 기술 검증은 모델 생성과 별개다.

## 5. 파일 및 모듈별 역할

[template.md](template.md)는 작성 양식이다. 구체적인 역할 문서는 각 Spec과 데이터 근거 확인 후 이곳에 추가한다. [review-approval.md](review-approval.md)는 검토·승인(HITL) 업무 정의(PROVISIONAL)다.

## 6. 입력 및 출력 데이터

현재 읽기는 Markdown 파일 경로를 받아 비어 있지 않은 텍스트를 돌려준다. 실제 프롬프트 입력과 산출물 형식은 담당 계약에서 확인한다.

## 7. 다른 모듈과의 관계

[Python SDK 연결](../src/hr_onboarding/agents/README.md)이 업무 정의를 소비한다. 개발용 프롬프트와 리뷰 역할은 [.claude](../.claude/README.md)에 있다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. template.md에서 목적, 도구, 승인 항목을 찾고 계약에 근거가 있는 항목과 질문으로 남길 항목을 구분한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
from pathlib import Path
from hr_onboarding.smoke import read_template


def load_local_template(path: Path) -> str:
    """승인된 로컬 작성 양식을 읽는다.

    Args:
        path: 프로젝트 안의 Markdown 양식 경로.

    Returns:
        검토 가능한 Markdown 텍스트.
    """
    return read_template(path)


assert load_local_template(Path("agents/template.md")).strip()
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 안내 메일 등 한 가지 역할의 Markdown의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “template.md의 목적·출력·권한 항목를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 가상 양식 읽기 예제만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 SDK가 읽는 양식과 워크플로우 입출력에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “확인되지 않은 산출물 형식 또는 발송 권한가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_runtime_template_is_readable
```

양식 읽기 한 건이 통과해야 한다. 실패 시 루트 위치, 확장자, 내용 유무부터 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 정의가 Spec 및 잠정 계약과 연결된다.
- [ ] 승인 경계와 미확정 값이 명확하며 실제 발송 단계가 없다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 고객사 문안과 업무 규칙을 임의로 채우지 않는다. 메일 발송과 입사 확정은 사람이 맡는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [계약 양식](../docs/contracts/template.md) · [SDK 연결 안내](../src/hr_onboarding/agents/README.md) · [Agent SDK 공식 문서](https://code.claude.com/docs/en/agent-sdk/python)
