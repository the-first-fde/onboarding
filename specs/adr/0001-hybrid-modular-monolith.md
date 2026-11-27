# ADR-001 · 결정론적 코어와 단일 agent
상태: 사용자 요청으로 채택 (2026-11-27).
결정: FastAPI/Python + React/TypeScript/Tailwind + PostgreSQL/pgvector.
SQLAlchemy 2.x는 transaction/제약, Alembic은 schema version, Pydantic은 계약 검증,
pytest는 실패·중복·재시작 검증, httpx는 API 시험, psycopg는 DB 접속, uvicorn은 로컬 API 서버 역할이다.
LLM 제안은 Claude Agent SDK 단일 agent+skills, LangChain은 RAG에 한정한다.
Cloudflare/LangGraph/OpenAI Agents SDK는 도입하지 않는다.
결과: agent가 없어도 승인→업무 생성→mock 실행은 재현 가능하다. 초기에 분산 orchestration은 필요 없다.
선택적 SDK/RAG 의존성은 설치·인증·버전 검증 전까지 미사용이다.
