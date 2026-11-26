# 담당별 준비 체크리스트

## 1. 이 디렉터리의 목적

입사자 한 건과 가상 양식에서 리더·총무·버디의 준비 항목과 기준일을 만들고, 기준 날짜에 따라 여섯 구간으로 나눈다. LangGraph가 입력 검증 → 목록 생성 → 구간 분류 → 노션 페이지 초안까지 연결한다(외부 쓰기 없음).

## 2. 무엇을 개발해야 하는가?

이 패키지는 순수 계산 함수와 LangGraph 그래프를 함께 담당한다(외부 쓰기 없음). [목록 생성 Spec](../../../../docs/specs/preparation-checklist-builder.md)과 [그래프 Spec](../../../../docs/specs/preparation-checklist-graph.md)의 모듈 전용 잠정 계약을 따른다.

## 3. 담당자별 개발 업무

종은 담당 영역의 목록 생성 로직과 Issue #7 그래프가 이 패키지에 있다. 승인·노션 mock 쓰기는 Issue #8에서 `draft_pages` 뒤에 연결한다. 진행 상태 처리는 별도 담당 영역이다.

## 4. 개발에 필요한 기초 개념

모델은 frozen dataclass, 묶음은 tuple이다. 해당 없음이 보류보다 우선하며 날짜가 있어도 조건 미정이면 보류한다.

## 5. 파일 및 모듈별 역할

| 파일 | 역할 |
|---|---|
| [request.py](request.py) | 입력의 전체·페이지 보류 검증 |
| [notion_draft.py](notion_draft.py) | 중립 블록과 담당별 페이지 초안 생성 |
| [graph.py](graph.py) | 전용 State와 네 단계 그래프 |
| [models.py](models.py) | 입력·중간·출력 불변 모델과 열거형 |
| [constants.py](constants.py) | PROVISIONAL 역할·주 시작·접힘·조건·보류 설명 |
| [due_date.py](due_date.py) | 기준일 해석, 날짜 계산, 주말 보정 |
| [conditions.py](conditions.py) | 조건 해당 여부 판정 |
| [builder.py](builder.py) | 담당별 목록 생성 |
| [sections.py](sections.py) | 여섯 구간 분류와 안정 정렬 |
| [__init__.py](__init__.py) | 공개 모델·함수·상수 재노출 |

## 6. 입력 및 출력 데이터

| 공개 함수 | 입력 → 출력 |
|---|---|
| `build_preparation_graph` | `request`, `template`, `today` 입력 State → `hire`, `input_hold_reasons`, `page_holds`, `checklist`, `role_sections`, `page_drafts`, `outcome`(정상 경로) |
| `build_notion_page_draft` | 입사자 ID, 양식 판, `RoleSections` → `NotionPageDraft` |
| `validate_request` | `PreparationRequest`, 양식, `today` → `RequestValidation` |
| `parse_due_rule` | 기준일 문자열 → `DueRule` |
| `shift_to_previous_weekday` | `date` → 보정한 `date` |
| `resolve_due_date` | `DueRule`, 입사일 → `DueDateResolution` |
| `evaluate_condition` | 조건 문자열, `NewHire` → 해당 여부·보류 사유 |
| `build_preparation_checklist` | `NewHire`, `ChecklistTemplate` → `PreparationChecklist` |
| `split_into_sections` | `Sequence[ChecklistEntry]`, `today` → `SectionedChecklist` |

중복 ID와 모르는 조건은 `ValueError`다. 지원하지 않는 기준일은 보류된다. 날짜가 없는 생성 결과에는 보류 사유가 있다.

`split_into_sections`는 날짜와 보류 사유가 모두 없는 항목을 `ValueError`로 거부한다. 단, 「해당 없음」 항목은 날짜와 보류 사유가 없어도 「해당 없음」 구간에 둔다. `HOLD_REASON_LABELS`는 모든 보류 사유의 설명을 담은 읽기 전용 매핑이다.

`validate_request`는 필수 칸 누락을 `InputHoldReason` 순서로 모으고 전체 보류 시 `hire=None`을 반환한다. 리더 누락은 전체 보류, 버디 누락은 버디 페이지 보류다(G3). 노트북 지급 미정은 검증을 통과하고 기존 항목 단위 보류로 처리한다. 그래프의 정상 경로는 입력 키와 위 출력 키를 모두 가진다. 필수 입력 누락 시 입력 키와 `input_hold_reasons`·`page_holds`·`outcome=ON_HOLD`만 남기고 종료하며, `hire`·`checklist`·`role_sections`·`page_drafts`는 생성하지 않는다. 버디만 누락하면 리더·총무 페이지를 만들고 `DRAFTED`로 종료한다. `RoleSections.item_ids`와 페이지 `item_ids`는 구간 정렬과 별개로 양식 순서를 유지한다.

## 7. 다른 모듈과의 관계

호출자는 `hr_onboarding.workflows.preparation_checklist`에서 공개 이름을 가져온다. CSV·노션 입출력은 호출자 책임이다. 리더·버디 인물 누락 판정은 `validate_request`가 담당한다. 공통 HR Schema·State를 확정하지 않는다. 승인 연결은 `draft_pages` 뒤에 Issue #8에서 추가한다(G4).

## 8. 단계별 개발 방법

Spec 확인 → 가상 입력 테스트의 RED 확인 → 최소 구현 → 개별 테스트와 공통 verify 순서로 진행한다.

## 9. 최소 구현 예제

```python
from datetime import date
from hr_onboarding.workflows.preparation_checklist import (
    CareerType,
    ChecklistTemplate,
    ChecklistTemplateItem,
    GraphOutcome,
    PreparationRequest,
    PreparationState,
    build_preparation_graph,
)

template = ChecklistTemplate(
    "vtest",
    (
        ChecklistTemplateItem(
            "VT-01", "가상 단계", "D-3", "시험 준비", "리더", "", "", "시험 확인 기록", "", ""
        ),
    ),
)
state: PreparationState = {
    "request": PreparationRequest(
        "VH-001", date(2027, 3, 2), CareerType.EXPERIENCED, True, "VL-001", "VB-001"
    ),
    "template": template,
    "today": date(2027, 2, 22),
}
result = build_preparation_graph().invoke(state)
assert result["outcome"] == GraphOutcome.DRAFTED
assert len(result["page_drafts"]) == 3
```

## 10. Claude Code 활용 예제

“Spec의 기준일 규칙과 테스트를 대조하고 보류 사유가 빠지는 경로를 확인해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 실행한다.

```bash
uv run --locked pytest -q tests/workflows/preparation_checklist
uv run --locked pytest -q tests/workflows/preparation_checklist --cov=hr_onboarding.workflows.preparation_checklist --cov-report=term-missing
uv run --locked python scripts/verify.py
```

## 12. 개발 완료 기준

가상 입력 인수 조건 PASS, 새 코드 커버리지 80% 이상, verify PASS와 독립 AI·사람 리뷰가 필요하다. 실제 양식 대조 여부는 별도로 기록한다.

## 13. 현재 제약 및 주의 사항

데이터팩 원문·실제 개인정보 사용과 외부 호출은 금지한다. 공휴일·완료 상태·승인·저장은 처리하지 않는다. 호출자가 KST의 `date`를 넘긴다(P3).

PROVISIONAL 상수는 `constants.py`에 모았다. 팀은 [Spec의 P1~P8](../../../../docs/specs/preparation-checklist-builder.md)을 확인한다. 특히 기간형 보류(P1), 월요일 시작(P2), 별도 보류 구간(P4), 날짜만으로 구간 판정(P5·Q14), 주말만 보정(P6), 대상 역할(P8), 확정일 입력(Q20)이 후속 합의 대상이다. `COLLAPSED_SECTIONS`는 표시 방식 A, 조건 값과 한국어 사유 설명도 잠정이다.

그래프의 [G1~G6](../../../../docs/specs/preparation-checklist-graph.md#provisional-가정)은 페이지 블록 구조·호출자 기준 날짜·전체/페이지 보류·승인 연결·가상 참조값·보류 사유 순서를 정의한다. 모두 이 워크플로 전용 잠정 계약이다.

## 14. 관련 문서

[상위 개발 안내](../README.md) · [Spec](../../../../docs/specs/preparation-checklist-builder.md) · [그래프 Spec](../../../../docs/specs/preparation-checklist-graph.md) · [잠정 계약](../../../../docs/contracts/communication-preparation.md) · [테스트 안내](../../../../tests/README.md)
