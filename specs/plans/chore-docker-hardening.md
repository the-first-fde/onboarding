# chore 계획 · Dockerfile 보안 hardening
상태: Reviewed
Branch: chore/claude-codex-workflow
Feature: 없음(PR #20 SonarCloud Quality Gate "Security Rating on New Code" D 해소)

## Scope
Codex가 수정할 수 있는 파일. 이 목록 밖은 수정하지 않는다.
- apps/backend/Dockerfile
- apps/frontend/Dockerfile

## 설계
| 대상 | SonarCloud 지적 | 변경 책임 |
|---|---|---|
| backend L4 | S8544 잠금 없는 의존성, S8541 `--only-binary`/`--no-build` 누락 | `pip install uv`를 제거하고 버전 고정 이미지에서 uv 바이너리를 복사한다(`ghcr.io/astral-sh/uv:0.11.8`, CI와 같은 버전). `uv sync --frozen --no-dev --no-build` |
| backend L1 | S6471 root 기본 사용자 | 전용 비root 사용자를 만들고 `/app` 소유권을 준 뒤 `USER`로 전환한다. 런타임 uv 캐시 경로는 쓰기 가능한 위치로 둔다 |
| frontend L4 | S6505 `--ignore-scripts` 누락 | `npm ci --ignore-scripts` |
| frontend L5 | S6470 재귀 COPY | `COPY . .` 대신 `index.html`, `tsconfig.json`, `vite.config.ts`, `src/`만 명시 복사 |
| frontend L1 | S6471 root 기본 사용자 | 이미지 내장 `node` 사용자로 실행하고 작업 디렉터리·복사 파일 소유권을 `node`에 준다 |

CMD, 노출 포트, compose 서비스 동작(migrate/api/worker/frontend)은 바꾸지 않는다.

## 테스트 케이스
| AC | 케이스 | 입력 | 기대 |
|---|---|---|---|
| 회귀 | 백엔드 테스트 | `uv run pytest` | 기존과 같이 PASS |
| 회귀 | 프론트 빌드 | `apps/frontend`에서 `npm ci --ignore-scripts && npm run build` | PASS |
| 정적 | Dockerfile 확인 | 각 Dockerfile | `USER` 지정, `COPY . .` 없음, `pip install` 없음 |

Docker daemon이 없으면 `docker build`는 NOT RUN으로 기록한다.

## 제외와 가정
- 이미지 digest 고정은 이번 범위가 아니다
- frontend 컨테이너는 개발 서버(vite dev) 용도 그대로 둔다

## Implementation Log
Codex가 작성한다: 변경 파일, 실행 명령과 PASS/FAIL, 질문, 모델 전환 기록.

- 변경 파일: `apps/backend/Dockerfile`, `apps/frontend/Dockerfile`; 이 Implementation Log 기록.
- 정적 확인: `USER` 지정, `COPY . .` 및 `pip install` 부재 검사 — 변경 전 FAIL, 변경 후 PASS.
- `uv run pytest` — PASS (118 passed, 경고 1건).
- `cd apps/frontend && npm ci --ignore-scripts && npm run build` — PASS.
- `docker info` — FAIL (Docker daemon에 연결할 수 없음); `docker build` 및 컨테이너 동작 검증 — NOT RUN.
- 질문: 없음. 모델 전환: 없음.
