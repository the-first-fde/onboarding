# Constitution v0.1
상태: 이번 요청에 따른 초기 기준. 사람의 최종 검토와 feature별 수용 검증은 별도다.

1. 근거 우선: 회사 업무 규칙은 확인된 파일·절·판·시점에 연결한다. 근거 없는 완료·기한·권한을 추정하지 않는다.
2. 사람의 판단: 채용 결정과 입사확정은 HR/리더의 일이다. 최종합격 통보를 입사확정으로 변환하지 않는다.
3. 최소 정보: 온보딩 handoff allowlist만 허용한다. 연봉·처우·면접 점수·레퍼런스 원문은 배제한다.
4. 결정론: 상태·기한·조건·정책·증거 검증·재실행은 Python이 통제하고 LLM은 분석/초안을 제안한다.
5. 승인: 실행 제안은 payload hash, actor, case, scope, expiry에 묶는다. 변경 시 승인을 무효화한다.
6. 격리: tenant/case/role/as-of를 조회 전 강제한다. 로그·벡터 검색·대화 기록에도 같은 경계를 적용한다.
7. 증거: occurred/observed/verified/completed 시각을 분리한다. 체크 표시만으로 업무가 끝났다고 단정하지 않는다.
8. 재현성: 이벤트·정책 버전·합성 fixtures로 Replay한다. 당시 알 수 없던 미래 증거는 제공하지 않는다.
9. 내구성: 상태·outbox·감사 로그는 한 DB 트랜잭션이다. 외부 실행은 최소 1회 전달 + 수신처 idempotency로 다룬다.
10. 기술: Python/FastAPI/Pydantic/SQLAlchemy/Alembic, React/TypeScript/Tailwind, PostgreSQL/pgvector, Docker Compose.
11. 단순화: Claude Agent SDK 단일 agent와 domain skills를 사용한다. LangChain은 RAG만, Cloudflare/LangGraph/OpenAI Agents SDK는 초기 제외다.
12. 검증: EARS 조건별 정상·거부·중복·실패 복구를 확인한다. 목표 수치와 측정 결과, scaffold와 구현을 분리한다.

SDD: Constitution → PRD → Feature → Plan → Implementation → Verification.
1+1+1+1+1은 Feature·Spec·Conversation·Plan·Commit의 추적 단위이며 이번 변경은 재구성 기초 작업이다.
commit·push·PR 생성은 CLAUDE.md의 개발 순서를 따르고, 머지는 사람이 PR 리뷰 후 수행한다. 소프트웨어 의존성은 잠금 파일로 고정하고 추가 이유를 ADR에 남긴다.
