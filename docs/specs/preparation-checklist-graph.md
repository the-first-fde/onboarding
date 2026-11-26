# Spec: 3-2 준비 체크리스트 LangGraph 워크플로 (입력 → 생성 → 구간 → 노션 페이지 초안)

- 상태/담당/관련 Issue/ADR/계약: DRAFT(구현됨, 사람 리뷰 전) / 종은(제안) / Issue #7(상위 #4, 선행 #6 = PR #9) / ADR 없음 / [잠정 계약](../contracts/communication-preparation.md) 「입력: 입사자 DB 한 행」·「출력: 담당별 체크리스트」 · [안내·준비 Spec](communication-preparation.md) 3-2·4절 · [#6 Spec](preparation-checklist-builder.md)
- 문제와 사용자 가치: #6은 담당별 목록과 구간을 만드는 순수 함수만 제공한다. 인사 담당자가 입사자 한 건을 넣으면 입력 확인부터 리더·총무·버디별 노션 페이지 초안까지 한 번에 나오는 실행 흐름이 필요하다. 필수 입력이 비면 엉터리 초안 대신 보류 사유를 남긴다. 이 그래프 끝에 승인 게이트와 노션 mock 쓰기(#8)가 붙는다.

## CONFIRMED 근거

- 현재 그래프는 기술 검증용 `src/hr_onboarding/smoke.py`(START → increment → END) 하나뿐이다.
- 워크플로 코드는 `src/hr_onboarding/workflows/`에 두고, 여러 파일이 필요하면 워크플로별 디렉터리를 만든다(2026-11-26 결정, Issue #7).
- #6 공개 API: `build_preparation_checklist(hire, template)`, `split_into_sections(entries, today)`, 모델 `NewHire`·`ChecklistTemplate`·`PreparationChecklist`·`SectionedChecklist`, 상수 `HOLD_REASON_LABELS`(`preparation_checklist/__init__.py`). 모르는 조건 값과 `item_id` 중복은 `ValueError`다.
- #6 `NewHire`에는 리더·버디 칸이 없다. 리더·버디 인물 누락 판단은 #7 몫이다(#6 Spec 「위험/차단/질문」).
- 입력 누락 처리(잠정 계약 입력 표): 입사일 필수(모든 기준일 계산), 경력 구분 필수, 리더 필수(없으면 3-2 보류), 버디는 D-14 전에 비어 있을 수 있고 없으면 버디 목록 보류, 노트북 지급 여부는 비어 있을 수 있다(#6이 항목 단위 보류로 처리).
- 3-2 승인 지점: 인사 담당자 승인 전 노션 쓰기 차단, `request_review()` 경유(안내·준비 Spec 4절). 승인 서브그래프는 PR #3(미merge)에 있고 #8은 BLOCKED다.
- 표시 방식 A: `지연 / 이번 주 / 다음 주 / 이후` + 보류·해당 없음 묶음, 이후만 접는다(Issue #4, #6 `COLLAPSED_SECTIONS`).
- 영속화·재시도·스케줄은 Q07 DEFERRED다.

## PROVISIONAL 가정

| ID | 가정 | 상수/위치 | 확인할 곳 |
|---|---|---|---|
| G1 | 노션 초안은 담당별 한 페이지. 페이지 본문은 #6 구간 순서의 구간 블록 6개이고, 항목은 할 일(to_do) 블록, 항목 세부(기준일·보류 사유·완료 기준·함께)는 그 아래 문단 블록이다. 접힌 구간은 토글 블록, 나머지 구간은 제목 블록으로 표현한다. 빈 구간도 블록을 남긴다. 노션 API 형식이 아니라 그 전 단계의 중립 데이터다 | `notion_draft.py`, `NotionBlockType` | 팀·#8(mock 쓰기 노드) |
| G2 | 기준 날짜 `today`는 호출자가 KST 날짜(`date`)로 바꿔 State 입력으로 넣는다. 그래프 안에서 시계를 읽지 않는다(테스트 재현성). 없으면 입력 보류 | `PreparationState.today` | 팀(#6 P3 연장) |
| G3 | 리더가 비면 전체 보류(초안 없음). 버디가 비면 버디 페이지만 보류하고 리더·총무 페이지는 만든다. 총무(경영지원)는 고정 역할이라 인물 입력을 받지 않는다 | `validate_request` | 팀·잠정 계약 입력 표 |
| G4 | 승인 연결: 이 그래프는 `draft_pages` 뒤 END로 끝난다. #8은 그 사이에 검토·승인 서브그래프를 넣고, 페이지 초안 하나를 PR #3 `Draft` 하나(`related_checklist_ids` = 페이지의 `item_ids`)로 넘기는 방식을 가정한다. State 필드 이름과 변환 위치는 #8에서 PR #3 merge 뒤 확정한다. 이번에는 checkpointer·interrupt·스텁을 두지 않는다 | `build_preparation_graph` | 정현님(PR #3)·#8 |
| G5 | 리더·버디는 이름 대신 가상 참조값(`leader_ref`, `buddy_ref`)으로 받는다. 값의 존재 여부만 보고 페이지에 넣지 않는다 | `PreparationRequest` | 팀(Q18 이름 처리와 함께) |
| G6 | 입력 보류 사유는 순서가 고정된 열거형 목록이다. 여러 개가 비면 모두 남긴다 | `InputHoldReason` | 리뷰 |

## 범위 / 제외 범위

- 범위: 흐름 전용 State와 입력 모델, 입력 검증, 노드 4개와 조건 분기, 그래프 조립, 노션 페이지 초안 데이터 구조와 생성 함수, 가상 pytest fixture·테스트, `workflows/README.md` 3·5·11절 갱신, `preparation_checklist/README.md` 갱신.
- 제외: 노션·MCP 호출, 승인·interrupt·checkpointer, 공통 State·오케스트레이터, 일정 실행·영속화(Q07), LLM·SDK 호출, CSV 읽기, 입사자 DB 연결, #6 계산 규칙 변경, 잠정 계약 문서 수정, 데이터팩 원문 사용.

## 입력/출력 및 계약 상태

모두 PROVISIONAL이며 이 워크플로 안에서만 쓴다. 모델은 `frozen=True` dataclass, 묶음은 `tuple`. #6 모델은 그대로 재사용한다.

### 열거형

| 이름 | 값 | 비고 |
|---|---|---|
| `InputHoldReason` | `HIRE_ID_MISSING`, `START_DATE_MISSING`, `CAREER_TYPE_MISSING`, `LEADER_MISSING`, `TEMPLATE_MISSING`, `TODAY_MISSING`, `BUDDY_MISSING` | 앞 여섯 개는 전체 보류, `BUDDY_MISSING`은 페이지 보류(G3). 출력 순서도 이 순서 |
| `GraphOutcome` | `DRAFTED`, `ON_HOLD` | `ON_HOLD`는 전체 보류 |
| `NotionBlockType` | `HEADING="heading"`, `TOGGLE="toggle"`, `TO_DO="to_do"`, `PARAGRAPH="paragraph"` | G1 |

### 입력 모델

`PreparationRequest` — 입사자 한 건. 비어 있을 수 있는 칸은 `None`(문자열은 공백만 있어도 비어 있음으로 본다).

| 필드 | 타입 | 필수 | 누락 시 |
|---|---|---|---|
| `hire_id` | `str` | 예 | `HIRE_ID_MISSING` |
| `start_date` | `date \| None` | 예 | `START_DATE_MISSING` |
| `career_type` | `CareerType \| None` | 예 | `CAREER_TYPE_MISSING` |
| `laptop_provided` | `bool \| None` | 아니오 | #6 항목 단위 `LAPTOP_UNDECIDED` |
| `leader_ref` | `str \| None` | 예 | `LEADER_MISSING`(전체 보류) |
| `buddy_ref` | `str \| None` | 아니오 | `BUDDY_MISSING`(버디 페이지 보류) |

이름·연락처·이메일·처우 칸은 받지 않는다.

### 중간·출력 모델

`PageHold`: `role: Role`, `reasons: tuple[InputHoldReason, ...]`.

`RequestValidation`: `hire: NewHire | None`, `hold_reasons: tuple[InputHoldReason, ...]`(전체 보류 사유), `page_holds: tuple[PageHold, ...]`. 불변식: `hire is None` ⇔ `hold_reasons`가 비어 있지 않다.

`RoleSections`: `role: Role`, `item_ids: tuple[str, ...]`(그 담당 #6 `RoleChecklist.entries`의 양식 순서 ID), `sectioned: SectionedChecklist`. `split_into_sections`가 구간 안을 날짜순으로 재정렬하므로 양식 순서는 `item_ids`로 따로 넘긴다.

`InputHoldReason`과 `RoleSections`는 여러 모듈(`constants.py`·`request.py`, `graph.py`·`notion_draft.py`)이 함께 참조하므로 #6 `models.py`에 둔다(기존 모델 변경 없이 추가만).

`NotionBlock`: `block_type: NotionBlockType`, `text: str`, `children: tuple[NotionBlock, ...]`(기본 빈 묶음).

`NotionPageDraft` — 담당 한 명의 페이지 초안. 쓰기 없음.

| 필드 | 타입 | 설명 |
|---|---|---|
| `hire_id` | `str` | 가상 식별자 |
| `role` | `Role` | 담당 |
| `title` | `str` | 페이지 제목. `hire_id`와 담당을 포함하고 이름은 넣지 않는다 |
| `template_version` | `str` | 양식 판 |
| `today` | `date` | 구간 기준 날짜 |
| `item_ids` | `tuple[str, ...]` | 페이지에 들어간 체크리스트 ID(양식 순서, #8 `related_checklist_ids` 후보) |
| `blocks` | `tuple[NotionBlock, ...]` | 구간 블록 6개(`SectionKind` 순서) |

구간 블록(G1): `text`는 구간 이름과 항목 수, `collapsed`이면 `TOGGLE`, 아니면 `HEADING`. 자식은 항목별 `TO_DO`(체크리스트 ID와 항목 이름). `TO_DO`의 자식 `PARAGRAPH`에 기준일 날짜(주말 보정 표시) 또는 보류 사유 설명(`HOLD_REASON_LABELS`), 「해당 없음」 표시, 완료 기준, 함께(비어 있지 않을 때)를 담는다. 완료 체크 상태는 담지 않는다(진행 상태는 계획·진행 담당).

### State (`PreparationState`, `TypedDict`, `total=False`, 입력 3개는 `Required`)

| 필드 | 타입 | 쓰는 노드 | 설명 |
|---|---|---|---|
| `request` | `PreparationRequest` | 입력 | |
| `template` | `ChecklistTemplate \| None` | 입력 | |
| `today` | `date \| None` | 입력 | KST 날짜(G2) |
| `hire` | `NewHire` | `validate_input` | 검증 통과 시만 |
| `input_hold_reasons` | `tuple[InputHoldReason, ...]` | `validate_input` | 통과 시 빈 묶음 |
| `page_holds` | `tuple[PageHold, ...]` | `validate_input` | |
| `outcome` | `GraphOutcome` | `validate_input`(보류), `draft_pages`(완료) | |
| `checklist` | `PreparationChecklist` | `build_checklist` | |
| `role_sections` | `tuple[RoleSections, ...]` | `split_sections` | 리더·총무·버디 순, 보류 담당 포함 |
| `page_drafts` | `tuple[NotionPageDraft, ...]` | `draft_pages` | 페이지 보류 담당 제외 |

전체 보류로 끝나면 `checklist`, `role_sections`, `page_drafts`는 State에 없다.

노드 반환 타입 `PreparationUpdate`(`TypedDict`, `total=False`)는 입력 3개를 뺀 State 필드를 모두 선택 키로 가진다. LangGraph는 스키마에 없는 키를 조용히 버리므로, 노드가 부분 갱신을 반환할 때 키 오타를 정적 검사로 잡기 위해 둔다.

### 상수 (PROVISIONAL, `constants.py`)

| 이름 | 값 | 근거 |
|---|---|---|
| `INPUT_HOLD_REASON_LABELS` | `InputHoldReason` → 짧은 한국어 설명(읽기 전용 매핑) | 화면 표시용 |
| `PAGE_HOLD_REASONS` | `BUDDY_MISSING` → `Role.BUDDY` | G3 |

## 노드·함수 (시그니처와 책임)

| 위치 | 시그니처 | 책임 |
|---|---|---|
| `request.py` | `validate_request(request: PreparationRequest, template: ChecklistTemplate \| None, today: date \| None) -> RequestValidation` | 필수 칸 누락을 `InputHoldReason` 순서로 모두 모은다. 통과하면 `NewHire`를 만들고, 버디 누락은 `page_holds`로 둔다. 외부 호출 없음 |
| `notion_draft.py` | `build_notion_page_draft(hire_id: str, template_version: str, role_sections: RoleSections) -> NotionPageDraft` | 한 담당의 구간 결과를 G1 블록 구조로 바꾼다. 순수 함수 |
| `graph.py` | `validate_input(state: PreparationState) -> PreparationUpdate` | `validate_request` 호출. 보류면 `outcome=ON_HOLD`, 사유, `page_holds`를 반환(전체 보류여도 `page_holds`를 채운다) |
| `graph.py` | `route_after_validation(state: PreparationState) -> str` | 전체 보류면 END, 아니면 `build_checklist` |
| `graph.py` | `build_checklist(state: PreparationState) -> PreparationUpdate` | #6 `build_preparation_checklist` 호출 |
| `graph.py` | `split_sections(state: PreparationState) -> PreparationUpdate` | 담당마다 #6 `split_into_sections(entries, today)`를 호출하고 양식 순서 `item_ids`와 함께 `RoleSections`로 담는다 |
| `graph.py` | `draft_pages(state: PreparationState) -> PreparationUpdate` | `page_holds`에 없는 담당만 페이지 초안을 만들고 `outcome=DRAFTED` |
| `graph.py` | `build_preparation_graph() -> CompiledStateGraph` | START → `validate_input` →(조건)→ `build_checklist` → `split_sections` → `draft_pages` → END. checkpointer 없음(G4) |
| `__init__.py` | 공개 이름 재노출 | 새 모델·함수·상수 추가 |

노드 이름 문자열은 위 함수 이름과 같게 한다(#8이 `draft_pages` 뒤에 붙인다).

## 관찰 가능한 인수 조건

- 필수 입력이 모두 있는 가상 입력으로 그래프를 실행하면 `outcome=DRAFTED`이고 리더·총무·버디 페이지 초안 3개가 이 순서로 나온다.
- 각 페이지에 구간 블록 6개가 `지연 / 이번 주 / 다음 주 / 이후 / 보류 / 해당 없음` 순서로 있고, 이후만 `TOGGLE`, 나머지는 `HEADING`이다. 빈 구간도 있다.
- 각 항목 블록에 체크리스트 ID, 기준일 날짜 또는 보류 사유 설명, 완료 기준이 있다. 페이지 `item_ids`가 그 담당 #6 목록과 같다.
- 페이지의 구간별 항목이 같은 입력·`today`로 #6 함수를 직접 부른 결과와 같다(그래프가 계산 규칙을 바꾸지 않는다).
- 입사일·경력 구분·리더·양식·`today`·`hire_id` 중 하나라도 없으면 `outcome=ON_HOLD`, 해당 사유가 `input_hold_reasons`에 있고, `checklist`·`role_sections`·`page_drafts`가 없다. 여러 개가 비면 사유가 모두 순서대로 있다.
- 버디만 없으면 `outcome=DRAFTED`, 리더·총무 페이지만 있고 `page_holds`에 버디·`BUDDY_MISSING`이 있다.
- 노트북 지급 여부가 없으면 전체 보류가 아니고, 해당 항목만 보류 구간에 있다.
- 페이지 제목·블록에 `leader_ref`·`buddy_ref` 값이 나오지 않는다.
- 네트워크 차단 상태(`tests/conftest.py`)에서 통과한다. 모델은 대입 시 예외.
- `uv run --locked python scripts/verify.py` PASS, 새 코드 커버리지 80% 이상.

## 정상/오류/권한/승인/중복/복구 시나리오

| 상황 | 동작 |
|---|---|
| 정상 | 담당별 페이지 초안 반환. 외부 호출 없음 |
| 필수 입력 누락 | 초안 없이 보류 사유와 함께 END |
| 버디 누락 | 버디 페이지만 보류(G3) |
| 양식 오류(모르는 조건, `item_id` 중복) | #6 `ValueError`가 그래프 밖으로 전파된다. 입력 누락이 아니라 양식 결함이므로 조용히 보류하지 않는다 |
| 승인·권한 | 해당 없음. 쓰기가 없다. 승인은 #8 |
| 중복 실행·복구 | 같은 입력이면 같은 결과(순수). 영속화·재시도는 Q07 |

## 테스트 계획과 미실행 이유

- 위치 `tests/workflows/preparation_checklist/`. 파일 이름은 저장소 전체에서 겹치지 않게 `test_preparation_request.py`, `test_preparation_notion_draft.py`, `test_preparation_graph.py`.
- 가상 fixture는 기존 `conftest.py`에 추가한다: 필수 칸이 모두 있는 `PreparationRequest`, 버디 없는 요청, 노트북 미정 요청, 고정 `today`. 양식은 기존 `template` fixture를 재사용한다. 참조값은 `VL-001` 같은 가상 값.
- 단위: 입력 검증(칸별 누락, 공백 문자열, 복수 누락 순서, 버디 페이지 보류), 페이지 초안(구간 블록 순서·종류, 항목 세부, 빈 구간, 참조값 미노출).
- 그래프: 정상 3페이지, 전체 보류 분기(키 부재), 버디 보류, #6 직접 호출 결과와 일치, `ValueError` 전파.
- TDD RED/GREEN 증거, 커버리지, verify PASS.
- NOT RUN: 실제 양식 v3.2·입사자 DB로 실행, 노션 렌더링 확인, 승인 연결(#8, PR #3 merge 대기).

## 보안/개인정보/외부 실행/비용

입력에 이름·연락처·이메일·처우가 없고 리더·버디는 참조값으로만 받아 출력에 넣지 않는다. 네트워크·MCP·LLM 호출이 없다. 가상 자료만 저장소에 둔다. 비용 없음.

## 위험/차단/질문

- PR #3이 `workflows/README.md` 5·11절을 고친다. 먼저 merge되는 쪽 뒤에서 충돌을 정리한다.
- #6(PR #9)이 리뷰 중 바뀌면 이 브랜치를 rebase하고 호출부를 맞춘다.
- G4는 PR #3 `ArtifactType`에 담당별 체크리스트 값이 어떻게 있는지에 달려 있다. #8에서 확인한다.
- 팀 확인: G1(페이지 구조), G2(기준 날짜 주체), G3(리더·버디 누락 범위), G4(승인 연결), G5(참조값).

## DoR/DoD와 사람 승인

- DoR: Issue #7 범위 승인(2026-11-26), 위치 결정, #6 구현(PR #9) 존재. PROVISIONAL 항목은 상수·함수 경계로 분리한다.
- DoD: 인수 조건 테스트 PASS, 커버리지 80% 이상, verify PASS, README 갱신과 링크 검사, 독립 AI 리뷰, 사람 리뷰.
