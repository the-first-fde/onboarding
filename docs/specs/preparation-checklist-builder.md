# Spec: 담당별 준비 체크리스트 생성·기준일 계산·구간 나누기

- 상태/담당/관련 Issue/ADR/계약: DRAFT(구현 전) / 종은(제안) / Issue #6(상위 #4) / ADR 없음 / [잠정 계약](../contracts/communication-preparation.md) 출력 「담당별 체크리스트」 · [안내·준비 Spec](communication-preparation.md) 3-2·6절
- 문제와 사용자 가치: 인사 담당자는 입사자마다 양식을 복제해 리더·총무·버디 항목을 손으로 고르고 기준일을 계산한다. 입사자 정보 한 건과 양식 항목으로 담당별 목록과 날짜를 한 번에 만들고, 오늘 기준으로 급한 항목부터 보이게 한다. 다음 Issue(#7)의 워크플로 노드가 이 함수들을 호출한다.

## CONFIRMED 근거

- 담당별 항목 수는 리더 11, 총무 6, 버디 1이다(안내·준비 Spec 3-2절).
- 조건 항목(`경력`, `노트북 지급`)은 해당할 때만 하고 아니면 「해당 없음」이다. D-n·D+n은 입사일 기준이고 주말이면 앞 평일로 당긴다. 「확정+2일」은 합격 확정일 기준이다(데이터팩 `02_온보딩/02_온보딩_체크리스트_양식.md` 3절).
- 양식 CSV 열은 항목ID·단계·기준일·항목·담당·함께·조건·완료 기준·안내 문서·비고·완료·완료일이다(같은 폴더 `.csv` 헤더). 리더·총무·버디 항목의 기준일 표기는 `D-n`, `D+n`, `확정+2일`, `첫 주`, `첫 정기 사무실 출근일`이 있고, 양식 전체에는 `3주 차`도 있다.
- 단계 칸과 기준일 칸이 다른 항목이 있다(같은 파일 4절). 날짜 계산은 기준일 칸만 쓴다.
- 합격 확정일은 입사자 DB에 없다(Q20). 첫 정기 사무실 출근일은 사무실 출근 일정 DB가 필요하다(잠정 계약 「입력: 그 밖」).
- 표시 방식 A(잠정 결정 2026-11-26, Issue #4): 기준일과 함께 한 번에 만들고 `지연 / 이번 주 / 다음 주 / 이후`로 나눈다. 이후는 접는다.

## PROVISIONAL 가정

| ID | 가정 | 상수/위치 | 확인할 곳 |
|---|---|---|---|
| P1 | 기간형 기준일(`첫 주`, `n주 차`)은 날짜 대신 보류 사유를 붙인다. 기간으로 볼지 대표일로 볼지는 미정 | `HoldReason.PERIOD_RULE` | 팀 |
| P2 | 주 시작 요일은 월요일 | `WEEK_START_WEEKDAY` | 팀 |
| P3 | 기준 날짜는 호출자가 KST 날짜로 바꿔 넘긴다. 함수는 `date`만 받는다 | 호출자(#7) | 팀 |
| P4 | 보류 항목과 「해당 없음」 항목은 네 구간과 별도 묶음으로 둔다 | `SectionKind.ON_HOLD`, `SectionKind.NOT_APPLICABLE` | 팀 |
| P5 | 구간은 날짜만으로 나눈다. 완료 여부를 모르므로 「지연」 구간은 「기한이 지난 항목」 뜻이다. 상태 값 `예정`·`지연` 판정과 결과 모델 공유는 Q14 합의 전까지 하지 않는다 | `split_into_sections` | 예빈님·종은(Q14) |
| P6 | 공휴일은 보정하지 않는다. 주말만 앞 평일로 당긴다 | `shift_to_previous_weekday` | 고객사(#5 research) |
| P7 | 해석할 수 없는 기준일 표기는 예외 대신 `UNSUPPORTED_RULE` 보류로 둔다. 한 항목 때문에 목록 전체가 멈추지 않게 한다 | `parse_due_rule` | 리뷰 |
| P8 | 대상 담당은 리더·총무·버디. 인사·입사자 항목은 걸러 낸다 | `TARGET_ROLES` | 안내·준비 Spec 3-2절 |

## 범위 / 제외 범위

- 범위: 입력·결과 모델(불변), 기준일 해석과 날짜 계산, 주말 보정, 조건 판정, 담당별 추출, 구간 나누기, 가상 pytest fixture, 새 디렉터리 README.
- 제외: CSV·노션 읽기와 쓰기, 승인, LangGraph 노드, 진행 상태 저장과 상태 값 판정, LLM 호출, 공휴일, 데이터팩 원문 사용, 공통 Schema·State 확정, 잠정 계약 문서 수정.

## 입력/출력 및 계약 상태

모두 PROVISIONAL이다. 공통 Schema가 아니며 이 모듈 안에서만 쓴다. 모델은 `frozen=True` dataclass, 묶음은 `tuple`.

### 열거형

| 이름 | 값 | 비고 |
|---|---|---|
| `Role` | `LEADER="리더"`, `GENERAL_AFFAIRS="총무"`, `BUDDY="버디"` | 출력 담당. 입력 담당 칸은 문자열 그대로 받는다 |
| `CareerType` | `EXPERIENCED="경력"`, `NEW_GRADUATE="신입"` | |
| `DueRuleKind` | `START_OFFSET`, `CONFIRMATION_OFFSET`, `FIRST_OFFICE_DAY`, `PERIOD`, `UNSUPPORTED` | |
| `HoldReason` | `CONFIRMATION_DATE_MISSING`, `OFFICE_SCHEDULE_MISSING`, `PERIOD_RULE`, `LAPTOP_UNDECIDED`, `UNSUPPORTED_RULE` | 사유별 한국어 설명은 상수 표로 둔다 |
| `Applicability` | `APPLICABLE`, `NOT_APPLICABLE`, `UNDECIDED` | `NOT_APPLICABLE`은 「해당 없음」 |
| `SectionKind` | `OVERDUE="지연"`, `THIS_WEEK="이번 주"`, `NEXT_WEEK="다음 주"`, `LATER="이후"`, `ON_HOLD="보류"`, `NOT_APPLICABLE="해당 없음"` | 출력 순서도 이 순서 |

### 입력 모델

`NewHire` — 입사자 정보 중 이 계산에 필요한 칸만 받는다. 이름·연락처·이메일은 받지 않는다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `hire_id` | `str` | 가상 식별자 |
| `start_date` | `date` | 입사일 |
| `career_type` | `CareerType` | 경력 구분 |
| `laptop_provided` | `bool \| None` | `None`은 미정 |

`ChecklistTemplateItem` — 양식 CSV 한 행. 진행 상태 열(`완료`, `완료일`)은 받지 않는다.

| 필드 | 타입 | CSV 열 |
|---|---|---|
| `item_id` | `str` | 항목ID |
| `stage` | `str` | 단계 |
| `due_rule` | `str` | 기준일(원래 표기) |
| `title` | `str` | 항목 |
| `owner` | `str` | 담당 |
| `collaborator` | `str` | 함께(빈 문자열 가능) |
| `condition` | `str` | 조건(빈 문자열 가능) |
| `completion_criteria` | `str` | 완료 기준 |
| `guide_doc` | `str` | 안내 문서 |
| `note` | `str` | 비고 |

`ChecklistTemplate`: `version: str`, `items: tuple[ChecklistTemplateItem, ...]`.

### 중간·출력 모델

`DueRule`: `kind: DueRuleKind`, `offset_days: int | None`(`START_OFFSET`·`CONFIRMATION_OFFSET`일 때만 값).

`DueDateResolution`: `due_date: date | None`, `weekend_adjusted: bool`, `hold_reason: HoldReason | None`. 불변식: `due_date is None`이면 `hold_reason`이 있다.

`ChecklistEntry` — 담당별 목록의 한 항목.

| 필드 | 타입 | 설명 |
|---|---|---|
| `item_id` | `str` | 체크리스트 ID |
| `role` | `Role` | 담당 |
| `title` | `str` | 항목 |
| `collaborator` | `str` | 함께 |
| `completion_criteria` | `str` | 완료 기준 |
| `due_rule` | `str` | 원래 기준일 표기 |
| `due_date` | `date \| None` | 보정 후 날짜 |
| `weekend_adjusted` | `bool` | 주말이라 당겼는지 |
| `applicability` | `Applicability` | 조건 판정 결과 |
| `hold_reasons` | `tuple[HoldReason, ...]` | 비어 있지 않으면 보류 |

불변식: `due_date is None`이면 `hold_reasons`가 비어 있지 않다. 노트북 미정 항목은 날짜가 있어도 `LAPTOP_UNDECIDED`로 보류한다.

`RoleChecklist`: `role: Role`, `entries: tuple[ChecklistEntry, ...]`(양식 순서).

`PreparationChecklist`: `hire_id: str`, `template_version: str`, `role_checklists: tuple[RoleChecklist, ...]`(리더·총무·버디 순, 항목이 없는 담당도 빈 목록으로 포함).

`ChecklistSection`: `kind: SectionKind`, `entries: tuple[ChecklistEntry, ...]`, `collapsed: bool`.

`SectionedChecklist`: `today: date`, `sections: tuple[ChecklistSection, ...]`(`SectionKind` 순서, 빈 구간 포함).

### 상수 (PROVISIONAL)

| 이름 | 값 | 근거 |
|---|---|---|
| `TARGET_ROLES` | 리더·총무·버디 순서 | P8 |
| `WEEK_START_WEEKDAY` | 0(월요일) | P2 |
| `COLLAPSED_SECTIONS` | `LATER` | 표시 방식 A |
| `CONDITION_CAREER`, `CONDITION_LAPTOP` | 양식 조건 칸 값 | 양식 3절 |
| `HOLD_REASON_LABELS` | `HoldReason` → 짧은 한국어 설명 | 화면 표시용 |

## 함수 (시그니처와 책임)

| 위치 | 시그니처 | 책임 |
|---|---|---|
| `due_date.py` | `parse_due_rule(raw: str) -> DueRule` | 앞뒤 공백을 무시하고 `D-n`·`D+n`·`확정+n일`·`첫 정기 사무실 출근일`·`첫 주`·`n주 차`를 구분한다. 나머지는 `UNSUPPORTED` |
| `due_date.py` | `shift_to_previous_weekday(day: date) -> date` | 토·일이면 직전 금요일, 평일이면 그대로 |
| `due_date.py` | `resolve_due_date(rule: DueRule, start_date: date) -> DueDateResolution` | `START_OFFSET`만 날짜로 바꾸고 주말 보정한다. 나머지는 종류별 보류 사유 |
| `conditions.py` | `evaluate_condition(condition: str, hire: NewHire) -> tuple[Applicability, HoldReason \| None]` | 빈 조건은 해당. `경력`은 경력 구분, `노트북 지급`은 지급 여부로 판정. 미정이면 `UNDECIDED`와 `LAPTOP_UNDECIDED`. 모르는 조건 값은 `ValueError` |
| `builder.py` | `build_preparation_checklist(hire: NewHire, template: ChecklistTemplate) -> PreparationChecklist` | 대상 담당 항목만 골라 기준일·조건을 적용한 담당별 목록을 만든다. 양식 순서를 유지한다. `item_id` 중복은 `ValueError` |
| `sections.py` | `split_into_sections(entries: Sequence[ChecklistEntry], today: date) -> SectionedChecklist` | 아래 규칙으로 나눈다. 구간 안은 `due_date` 오름차순, 같은 날은 입력 순서 |
| `__init__.py` | 공개 이름 재노출 | 호출자(#7)가 쓰는 모델·함수·상수 |

구간 규칙(P2·P4·P5): 이번 주 = `today`가 속한 주(시작 요일 `WEEK_START_WEEKDAY`)의 7일.

| 조건 (위에서부터 처음 맞는 것) | 구간 |
|---|---|
| `applicability == NOT_APPLICABLE` | 해당 없음 |
| `hold_reasons`가 있음 | 보류 |
| `due_date < today` | 지연 |
| `today <= due_date <= 이번 주 끝` | 이번 주 |
| 다음 주 7일 안 | 다음 주 |
| 그 뒤 | 이후(`collapsed=True`) |

## 관찰 가능한 인수 조건

- 담당별 목록의 각 항목에 체크리스트 ID, 기준일 날짜 또는 보류 사유, 완료 기준이 있다.
- 인사·입사자 항목은 목록에 없고, 리더·총무·버디 목록은 양식 순서를 따른다.
- 신입은 `경력` 항목이 「해당 없음」, 경력은 해당이다. 노트북 지급 `True`면 해당, `False`면 「해당 없음」, `None`이면 `LAPTOP_UNDECIDED`로 보류된다.
- 토요일·일요일 기준일이 직전 금요일로 바뀌고 `weekend_adjusted`가 참이다. 평일은 그대로다.
- `확정+2일`, `첫 정기 사무실 출근일`, `첫 주`, `n주 차`는 날짜가 없고 각각 정해진 보류 사유가 붙는다.
- 같은 항목 목록에 `today`만 바꾸면 항목이 지연·이번 주·다음 주·이후 사이를 맞게 옮긴다. 이번 주 경계 전날·첫날·끝날, 다음 주 끝날·그 다음 날을 확인한다.
- 보류·「해당 없음」 항목은 `today`와 무관하게 각각의 묶음에 있다. 이후 구간만 `collapsed`다.
- 입력과 결과 객체는 수정할 수 없다(대입 시 예외).
- 가상 자료에 데이터팩 원문 문장과 실제 개인정보가 없다(리뷰어 대조).

## 정상/오류/권한/승인/중복/복구 시나리오

| 상황 | 동작 |
|---|---|
| 정상 | 담당별 목록과 구간 결과 반환. 외부 호출 없음 |
| 해석 불가 기준일 | 해당 항목만 `UNSUPPORTED_RULE` 보류(P7) |
| 모르는 조건 값 | `ValueError`(양식이 바뀐 것이므로 조용히 넘기지 않는다) |
| `item_id` 중복 | `ValueError` |
| 대상 담당 항목 없음 | 그 담당은 빈 목록 |
| 권한·승인·복구 | 해당 없음. 순수 함수이며 쓰기가 없다. 승인은 #8 |

## 테스트 계획과 미실행 이유

- 위치 `tests/workflows/preparation_checklist/`. `tests/`에 `__init__.py`가 없으므로 테스트 파일 이름은 저장소 전체에서 겹치지 않게 짓는다.
- 가상 fixture(`conftest.py`): 입사자 3건(경력·노트북 지급, 신입·미지급, 경력·노트북 미정)과 리더·총무·버디·인사·입사자 항목이 섞인 가상 양식. CSV 열 구조만 따르고 ID(`VT-nn`)와 문구는 새로 쓴다. 토·일 기준일이 나오는 입사일, 계산 불가 기준일 4종, 조건 항목 2종을 포함한다.
- 단위 테스트: 기준일 해석, 주말 보정, 날짜 계산·보류, 조건 판정, 담당 추출·순서·중복, 구간 경계, 불변성.
- TDD RED/GREEN 증거, 새 코드 커버리지 80% 이상, `uv run --locked python scripts/verify.py` PASS.
- NOT RUN: 실제 양식 v3.2로 리더 11·총무 6·버디 1 확인. 원문을 fixture로 쓸 수 없다. #7 이후 로컬 수동 확인 대상이다.

## 보안/개인정보/외부 실행/비용

입력 모델에 이름·연락처·이메일·처우 칸이 없다. 네트워크·MCP·LLM 호출이 없다. 가상 자료만 저장소에 둔다. 비용 없음.

## 위험/차단/질문

- 가상 자료에 원문 문구가 섞일 위험: 리뷰에서 데이터팩과 대조한다.
- 출력 필드가 잠정 계약 「담당별 체크리스트」 행보다 많다(`hold_reasons`, `applicability`, `weekend_adjusted`). 계약 문서는 Q14 합의 때 함께 고친다.
- 리더·버디 인물이 비어 있을 때 목록 보류(잠정 계약 입력 표)는 담당 역할 기준인 이 모듈 밖에서 #7이 판단한다.
- 팀 확인: P1(기간형), P2·P3(주 시작 요일·기준 시각), P4(보류 위치), P5·Q14(상태 판정 주체·결과 모델 공유), Q20(확정일 입력).

## DoR/DoD와 사람 승인

- DoR: Issue #6 범위 승인(2026-11-26), 표시 방식 A 잠정 결정, 위치 결정. PROVISIONAL 항목은 상수로 분리해 바꿀 수 있게 한다.
- DoD: 인수 조건 테스트 PASS, 커버리지 80% 이상, verify PASS, 새 디렉터리 README, 독립 AI 리뷰, 가상 자료 원문 대조, 사람 리뷰.
