# 기술 아키텍처 및 구현 경계

팀/Claude Code → 검증·리뷰된 Python → LangGraph → Claude Agent SDK → Markdown 업무 정의 → MCP.
LangGraph가 제어권을 가지며 결정적 규칙은 Python으로 구현한다. 외부 쓰기는 향후 별도 승인 경계 필요.

현재 구현은 비동기 카운터 그래프, SDK 옵션 생성, Markdown 파일 읽기, MCP 응답 타입 mock뿐이다.
실제 SDK query/Claude CLI 시작/MCP transport/서버/승인 워크플로우는 구현하지 않았다.
개발 `.claude/`와 업무 `agents/`는 권한/자료를 분리한다. runtime은 개발 Skills/Shell/GitHub 권한을 받지 않는다.
영속화/체크포인트/스케줄러/공통 HR State는 샘플 및 담당 합의 이후 ADR로 결정한다.
