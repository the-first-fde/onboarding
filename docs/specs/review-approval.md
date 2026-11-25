# 담당 업무 Spec: 산출물 검토·HITL·승인 상태 관리

- 담당: 검토·승인 담당 (업무 분할 「4. 사람의 검토 및 승인 (HITL)」, 2026-11-25 확인)
- 상태: PROVISIONAL — 데이터팩 근거로 잠정 계약 작성, 팀 합의 항목은 계약 문서에 NEEDS_CLARIFICATION으로 표시
- 관련 잠정 데이터 요구: [계약 초안](../contracts/review-approval.md)
- 확인된 사실: 계약 문서 「확인된 사실」 참조. 업무 분할 8번(Review Agent)은 구현하지 않는다.
- 업무 목표: 산출물 검토·수정 요청 처리·HITL·승인 상태 관리
- 잠정 가정: 계약 문서 A1~A5 (확정 정책 아님)
- 확인할 질문: 계약 문서 「다른 담당자와 충돌/공통화가 필요한 사항」 참조
- 제외: 실제 외부 실행/실제 고객사 데이터/확정 공통 Schema·State·업무 규칙·공통 fixtures/Claude Agent SDK 호출/영속 checkpointer
- 인수 조건 (PROVISIONAL, 테스트로 검증):
  - 초안 등록 시 차이 요약을 붙여 검토대기로 올린다. 리더 제공 내용이면 출처 확인을 표시한다.
  - 인사 담당자만 검토 결정을 한다. 전이표에 없는 전이는 거부한다.
  - 승인 뒤 내용이 바뀌면 재승인을 받는다. 실행 뒤 내용이 바뀌면 대기열에 되돌린다.
  - 외부 실행 게이트는 대기열에 저장된 항목만 보고, 승인완료·같은 내용·미실행일 때만 통과한다.
  - 메일 발송·입사 확정·합격/불합격·정규 전환 결정은 항상 사람에게 넘긴다.
  - 사람 결정은 LangGraph interrupt로 기다리고, 보류면 다시 기다린다.
- 구현: [review_approval.py](../../src/hr_onboarding/workflows/review_approval.py), [업무 정의](../../agents/review-approval.md)
- 현재 검증: 기술 테스트 PASS (`tests/test_review_approval.py`, 가상 데이터). 업무 계약은 팀 합의 전이라 NOT RUN
- 다음 단계: 계약 공유 → 안내·준비 / 계획·진행 담당과 인터페이스 합의 → 독립·사람 리뷰
