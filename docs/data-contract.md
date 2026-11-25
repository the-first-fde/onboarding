# 데이터 계약 — DEFERRED

2026-11-25 고객사 가명·가공 데이터팩(`FF_HR과제_데이터팩_*/`, 기준일 2026-11-23)을 받았다. 이 데이터팩은 로컬 참조 전용이며 gitignore 대상이다. 저장소 문서에는 경로와 절 번호로만 인용하고 원문·인물명을 복사하지 않는다.

확정된 HR Schema, 공통 State, 공통 업무 fixtures는 아직 없다.
담당자별 잠정 입력·출력·근거·질문은 [계약 양식](contracts/template.md)으로 기록한다. 데이터팩을 근거로 쓴 계약은 다음과 같다.

| 담당 업무 | 계약 | 상태 |
|---|---|---|
| 온보딩 계획·진행 | [onboarding-planning](contracts/onboarding-planning.md) | NEEDS_CLARIFICATION |
| 안내 메일·준비 요청 | [communication-preparation](contracts/communication-preparation.md) | PROVISIONAL |
| 검토·HITL·승인 | [review-approval](contracts/review-approval.md) | NEEDS_CLARIFICATION |

공통화 후보 (3인 조정 필요):
- 입사자 정보: 데이터팩 `02_온보딩/01_노션DB_구조.md` 0절
- 체크리스트 항목: `02_온보딩/02_온보딩_체크리스트_양식.csv`
- 민감도 기준: `00_공통/05_AI_사용_보안_가이드.md` 2부

개인별 탐색 스키마를 공통 확정 계약처럼 배포하지 않는다.
충돌을 조정한 뒤 버전, 호환성, 마이그레이션을 합의한다. 테스트에는 데이터팩 원문이 아니라 검토된 가상 fixture를 쓴다.
