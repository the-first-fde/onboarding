# 검증

[루트 지침](../CLAUDE.md)을 먼저 준수한다.

고객사 데이터나 업무 테스트 fixtures를 만들어 계약을 확정하지 않는다. socket 연결은 기본 차단한다. SDK query와 실제 MCP는 호출하지 않는다. 기술 smoke PASS를 업무 유효성으로 보고하지 않는다. 네트워크/실제 인증 검증은 NOT RUN으로 기록한다.
