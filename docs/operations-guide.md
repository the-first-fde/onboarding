# 운영과 복구
로컬 합성 데이터 전용이다. README 시작 명령과 docs/verification.md의 실제 결과를 함께 본다.

## 환경
실제 .env/키/토큰을 commit하거나 출력하지 않는다. demo 토큰은 운영 인증이 아니다.
실연동 adapter는 차단되어 있다. 서버와 frontend는 localhost에만 바인딩한다.
Compose의 demo DB 계정은 합성 시연 전용이며 회사 데이터 적재는 금지한다.

## migration/worker
PostgreSQL은 `uv run alembic upgrade head`로 초기화한다 (DATABASE_URL 필요).
worker는 `PYTHONPATH=apps/backend uv run python -m hr_ops.worker` 단발 처리다.
Compose는 --loop worker를 사용한다. mock worker receipt와 status는 한 DB 트랜잭션이다.
DB 중단이면 커밋되지 않은 상태는 롤백된다. DB 복구 후 worker를 재시작한다.
외부 실행/재시도/backoff/DLQ는 아직 미구현이다. 미확인 외부 결과를 성공으로 바꾸지 않는다.

## 백업과 되돌리기
기존 파일은 저장소 옆 `onboarding-backup-20261127T142435Z/previous/`에 이동 보존했다 (디렉터리 권한 700).
백업 README.txt, git-status.txt, working.patch, index.txt, head.txt를 기준으로 복구한다.
먼저 새 작업 파일을 별도 디렉터리로 보관하고 previous/의 숨김 항목을 포함해 원위치로 이동한다.
.git/.github/retained.json에 적힌 원본·비밀 파일을 덮어쓰지 않는다. 기존 .venv도 previous/.venv에 보존했고 새 환경은 별도로 설치했다. git reset/clean을 사용하지 않는다.
백업에는 로컬 설정 등 민감한 파일이 있을 수 있으므로 Git/외부 서비스로 업로드하지 않는다.
백업은 동기화 저장소/공유 디렉터리가 아닌 로컬 경로다. 별도 장기 보관은 사용자 정책에 따른다.

## 기존 CI
.github/ 전체는 보존했다. ci.yml은 이전 scripts/verify.py와 팀 설정을 참조한다.
notion-sync.yml도 이전 협업 스크립트를 참조하므로 현재 구조에서 작동하지 않는다.
이전 scripts를 성공 stub으로 대체하지 않았다. 사용자의 .github 보존 요구로 CI 수정은 남겨 둔다.
기존 Git hooks도 보존되어 이전 스크립트에 의존할 수 있다. commit 전에 별도 검토가 필요하다.
원격 origin은 팀 저장소 그대로이며 이 재구성 작업은 push하지 않는다.

루트 AGENTS.md는 이전 .git/info/exclude에서 무시되던 파일이다. .git을 수정하지 않고 새 .gitignore의 명시적 예외로 추적 후보에 포함했다. 실제 staging/commit은 하지 않았다.
