# ADR 0002: 개발과 런타임 분리

- 날짜: 2026-11-25
- 상태: 사용자 확정 정책 반영, 추천/미확인은 본문 구분
- 근거: 초기화 Spec 0001 및 사용자 지시

확정: LangGraph 제어/SDK 실행/Markdown/MCP, 프론트엔드·FastAPI 제외. 초기 구현은 기술 smoke뿐. 개발용 .claude와 runtime agents를 분리하며 공통 HR 계약/영속화는 보류한다.
