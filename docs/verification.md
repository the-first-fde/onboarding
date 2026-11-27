# 검증 기록 · 2026-11-27 KST
## 실제 수행한 검사
| 검사 | 결과 | 범위 |
|---|---|---|
| 실제 저장소에서 uv sync --frozen --offline --group dev | PASS | uv.lock, Python 3.12.4, 새 .venv |
| 실제 저장소에서 uv run --frozen pytest -q | PASS | 16 passed, 4.80s |
| npm ci --offline / npm run build | PASS | 실제 frontend 경로, TypeScript + Vite 빌드 |
| Alembic upgrade head + alembic check | PASS | 별도 임시 SQLite DB; schema 차이 없음 |
| docker compose config --quiet | PASS | 설정 문법/서비스 의존성만 |
| PostgreSQL/pgvector/Compose 실행 | NOT RUN | Docker daemon/socket 없음 |
| 브라우저 전체 E2E | NOT RUN | 화면 빌드와 API 테스트까지만 |
| 실제 Claude SDK/MCP/외부 API/RAG/전체 56업무 eval | NOT RUN | 현재 미구현 |

테스트는 인증 없는 생성 차단, 민감/비허용 필드와 원문 반사 차단, 합격 통보 거부,
입사확정 승인과 null 허용, ON-01~03 확정+2일, 중복/충돌, case/event/outbox/audit 원자성,
worker 재시작/중복 방지/receipt 실패 롤백, real adapter 차단, 56 업무 정의와 합성 replay 시점을 검사했다.
HTTP TestClient 의존성에서 httpx 사용 관련 deprecation warning 1건이 있었다. 테스트 실패는 아니다.
SQLite 테스트는 PostgreSQL 동시성/격리 검증을 대신하지 않는다.

## 보존 확인
- .github/의 상대 경로+SHA-256+심볼릭 링크 대상 manifest가 변경 전과 동일했다.
- Git HEAD / 현재 브랜치 / index 엔트리 / remote가 변경 전과 동일했다.
- commit/stage/push/force push/remote 수정 없음. 기존 파일과 환경은 저장소 옆 비공개 백업으로 이동 보존했다.
- 기존 원본 데이터팩 폴더·zip은 원위치에 남겼고 새 .gitignore에서 제외됨을 확인했다.
- AGENTS.md는 새 .gitignore 예외로 이전 local exclude를 상쇄한다. .git/info/exclude 자체는 보존했다.

## 남은 제한
G0 문서는 초안이며 조직별 승인자·일반 기한 규칙·정식 연동 계약은 미확정이다.
G1~G2는 합성 데이터용 초기 수직 흐름만 구현했다. 56개 전체 업무 생성, 정책 소급 migration,
증거 진단·정식 RBAC·장기 승인·SDK·Wiki/RAG는 미완료다.
보존한 .github의 이전 CI/Notion sync 및 Git hooks는 이전 경로를 참조하므로 새 구조와 호환되지 않을 수 있다.
