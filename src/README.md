# Python 소스 배치

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

제품 Python 파일의 배치 기준을 제공한다. 테스트와 운영 스크립트는 각자의 디렉터리에 유지한다.

## 2. 무엇을 개발해야 하는가?

새 기능을 바로 src 아래에 두기 전에 업무 순서, SDK 실행, 외부 도구 중 책임을 결정한다. 순수 로직과 외부 호출 경계를 구분해 테스트하기 쉽게 만든다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | Python 워크플로우 배치 | 계획·진행 노드 변경 | [계획 Spec](../docs/specs/onboarding-planning.md) |
| 종은 | SDK 생성 경계 배치 | 초안 생성 연결 변경 | [안내 Spec](../docs/specs/communication-preparation.md) |
| 정현 | 검토와 승인 흐름 배치 | HITL 검증 변경 | [검토 Spec](../docs/specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

모듈은 기능을 담은 Python 파일이다. import는 다른 모듈의 이름을 참조한다. 역할을 한 곳에 두면 어느 코드를 고칠지 찾기 쉽다.

## 5. 파일 및 모듈별 역할

[hr_onboarding](hr_onboarding/README.md)이 실제 패키지다. 각 하위 README의 제안 위치와 현재 파일을 먼저 확인한다. 공통 스키마나 저장 모듈은 합의 후 배치한다.

## 6. 입력 및 출력 데이터

입력은 각 함수의 인자, 출력은 반환값과 예외로 문서화한다. 구체적인 HR 필드 대신 기술 예제에서 먼저 읽는 방법을 익힌다.

## 7. 다른 모듈과의 관계

소스는 pyproject와 uv.lock 환경으로 실행된다. 동작 검증은 [tests](../tests/README.md), 명세 근거는 [docs](../docs/README.md)에 둔다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 패키지 안내에서 해당 개발 위치를 고르고, 입출력과 예외를 설명하는 한국어 Google Style Docstring을 작성한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
def next_count(count: int) -> int:
    """기술 예제 카운터를 한 번 증가시킨다.

    Args:
        count: 현재 카운터.

    Returns:
        하나 증가한 카운터.
    """
    return count + 1


assert next_count(0) == 1
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 변경할 Python 모듈의 파일 배치의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “src 레이아웃과 import를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 결과를 반환하는 작은 함수 테스트만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 공통 타입과 하위 모듈 import에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “공통 모듈 책임 중복가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py
```

기술 테스트가 모두 통과해야 한다. 실패하면 첫 traceback의 호출 파일과 해당 모듈 책임부터 확인한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 모듈 위치와 호출자가 명확하다.
- [ ] 입출력의 타입과 실패 시 처리 방법이 동작과 일치한다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

미합의 HR 공통 데이터 모델과 업무 저장 구조를 추가하지 않는다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [코딩 규칙](../docs/guides/coding-conventions.md) · [패키지 안내](hr_onboarding/README.md) · [Python 모듈 공식 문서](https://docs.python.org/3.12/tutorial/modules.html)
