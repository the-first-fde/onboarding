# HR Operations · 개인 FDE 프로젝트
채용 → 입사확정 → 온보딩을 첫 도메인으로 삼는 독립 프로젝트다. 팀은 별도 저장소를 사용한다.
제출 마감: **2026-12-03 23:59 KST**.

## 현재 제공 범위
G0 명세 초안과 G1~G2의 작은 mock 수직 흐름을 제공한다. 승인된 입사확정 이벤트를 저장하면
온보딩 케이스와 outbox가 같은 트랜잭션으로 생성되고, DB worker가 mock 준비 요청을 기록한다.
실제 ATS/Notion/메일·인증·에이전트·RAG·56개 전체 업무 실행은 아직 구현하지 않았다.
React 운영 화면은 mock 이벤트 승인·케이스 조회의 시작점이다. 운영 배포용이 아니다.

## 시작
```sh
uv sync --group dev
uv run pytest
# 터미널 1: 합성 데이터만 사용하는 로컬 API
DEMO_HR_TOKEN=local-demo-only PYTHONPATH=apps/backend uv run uvicorn hr_ops.api:app --host 127.0.0.1 --port 8000
# 터미널 2: worker (단발 실행, 필요할 때 반복)
PYTHONPATH=apps/backend uv run python -m hr_ops.worker
# 터미널 3
cd apps/frontend
npm ci
npm run dev -- --host 127.0.0.1
```
화면에 로컬 demo 토큰을 입력한다. `.env` 파일은 자동으로 읽지 않는다.
DB 기본값은 개발용 SQLite이며, PostgreSQL 검증을 대신하지 않는다.

```sh
# 전체 로컬 compose 환경: DB + migration + API + worker + frontend
# localhost 포트만 노출; demo 자격만 사용
# 실행 전 Docker가 켜져 있어야 한다.
docker compose up --build
```
Compose는 Alembic 초기화를 사용한다. SQLite 자동 테이블 생성은 로컬 테스트 편의 기능이다.
[명세](specs/prd.md) · [아키텍처](specs/architecture.md) · [핵심 계약](specs/contracts/hire-confirmed-event.md) ·
[구현 상태](docs/implementation-status.md) · [운영/복구](docs/operations-guide.md) · [검증 기록](docs/verification.md).

## 근거와 보존
실제 확인한 데이터팩의 경로·절과 Notion 학습 페이지는 [근거 목록](docs/source-register.md)에 기록했다.
원본 데이터팩은 기존 로컬 위치에 보존하고 Git에서 제외했다. 테스트는 합성 식별자만 쓴다.
`.github/`와 `.git/`은 기존 그대로 보존했다. 기존 CI는 이전 구조를 참조하므로 새 구조와 호환되지 않는다.
원격 연결은 보존했으나 push하지 않았고, 새 커밋도 만들지 않았다.
