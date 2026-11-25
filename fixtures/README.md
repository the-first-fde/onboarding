# 가상 테스트 자료

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

여러 테스트가 같은 가상 입력을 필요로 할 때 보관하는 위치다. 테스트 자체는 tests에 둔다.

## 2. 무엇을 개발해야 하는가?

현재는 기술 mock을 테스트 안에 둔다. 계약 확인 뒤 공통 재사용이 필요한 가상 자료만 출처·용도·리뷰 근거와 함께 추가한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 예빈 | 공유 가상 계획 입력 요구 정리 | 자료 필요성·검증 근거 | [계획 Spec](../docs/specs/onboarding-planning.md) |
| 종은 | 준비 요청용 가상 시나리오 요구 정리 | 초안 테스트 입력 요구 | [안내 Spec](../docs/specs/communication-preparation.md) |
| 정현 | 가상 검토·승인 경계 요구 정리 | 정상·오류 시나리오 요구 | [검토 Spec](../docs/specs/review-approval.md) |

## 4. 개발에 필요한 기초 개념

fixture는 테스트에서 재사용하는 초기 데이터다. 순수 가상 값은 실제 고객 정보와 관계없이 만든다.

## 5. 파일 및 모듈별 역할

현재 이 폴더에는 README와 지침만 있다. 기술 예제는 [test_smoke.py](../tests/test_smoke.py)에 있다. 승인 후 자료가 생기면 각 파일에 목적과 연결 테스트를 설명한다.

## 6. 입력 및 출력 데이터

입력은 확인된 테스트 조건이며 출력은 그 조건을 재현하는 가상 자료다. HR 데이터 열과 상태는 계약 확정까지 보류한다.

## 7. 다른 모듈과의 관계

[테스트](../tests/README.md)가 자료를 사용한다. 담당자 간 재사용이 필요하면 [계약 양식](../docs/contracts/template.md)에 필요한 근거를 남긴다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 같은 자료를 실제로 재사용할 테스트가 있는지 확인하고 출처와 승인 범위를 문서화한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```python
def fake_counter_input() -> dict[str, int]:
    """업무 데이터와 무관한 기술 카운터 입력을 만든다.

    Returns:
        기술 smoke와 같은 시작값을 담은 새 딕셔너리.
    """
    return {"count": 0}


assert fake_counter_input()["count"] == 0
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 공유 가상 자료가 필요한 테스트의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “현재 test_smoke.py 내부 카운터와 별도 fixture의 차이를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 가상 기술 입력 검증만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 가상 입력을 참조할 테스트와 계약에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “자료 출처 또는 비식별 여부 불명확가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked pytest -q tests/test_smoke.py::test_graph_runs_without_network
```

현재 가상 카운터 테스트가 통과한다. 실패하면 실제 자료를 찾는 대신 기술 입력과 기대값을 대조한다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 자료가 순수 가상이며 출처와 연결 테스트가 있다.
- [ ] 계약에 없는 필드나 승인 규칙이 추가되지 않았다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

실제 고객사 자료는 이 저장소에 넣지 않는다. 공통 업무 fixtures는 보류 상태다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [계약 양식](../docs/contracts/template.md) · [보안 가이드](../docs/guides/security-guide.md) · [테스트 가이드](../docs/guides/testing-guide.md) · [pytest fixture 공식 문서](https://docs.pytest.org/en/stable/how-to/fixtures.html)
