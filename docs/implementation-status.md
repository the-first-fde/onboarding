# 구현 상태
| 구성 | 상태 | 한계 |
|---|---|---|
| Constitution/PRD/Architecture/18 features/plans/ADR | 초안 | G0 사람 검토 미완료 |
| HireConfirmedEvent Pydantic allowlist | 구현 | 합성 ID만, 실원천 adapter 없음 |
| HR demo 승인 API와 audit hash | 구현 | SSO/RBAC/승인 만료·취소 없음 |
| case + ON-01~03 + outbox transaction | 구현 | ON-04~56 생성/기한 엔진 없음 |
| DB mock worker receipt | 구현 | 단일 worker, 실제 외부 실행 없음 |
| ON-01~56 catalog | 정의 | 역사적 판/모호한 기한 미확정 |
| React/Tailwind console | 초기 구현 | demo 토큰, 3 업무 조회/승인만 |
| PostgreSQL/pgvector + Alembic + Compose | scaffold | 실제 검증 결과는 verification 참조 |
| Claude SDK/skills/hooks/budget/정식 승인 | 설계·경계 문서 | 호출 안 함 |
| Wiki/RAG/context isolation | 설계 문서 | 색인·검색·모델 연결 안 함 |
| Replay/Evals | 작은 합성 입력/pytest + 시나리오 명세 | 전체 데이터팩 평가 안 함 |
| 수습평가/1on1/오프보딩 | 후속 | 초기 범위 제외 |
