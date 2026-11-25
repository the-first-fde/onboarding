# 초기화 결과 — 2026-11-25

## 결과와 작업 보호

지정 경로 `/Users/sleepyowl/Projects/onboarding`에 초기화했다. 다른 경로에 프로젝트를 생성하지 않았다.
임시 원본 검토/작성 도구만 /tmp에 사용했다. 시작 시 .git만 있었고 첫 commit 없는 main이었다.
작업 파일/커밋이 없어 덮어쓰기가 발생하지 않았다. remote 설정은 변경하지 않았다.
commit/push/merge/원격 설정/Issue·PR·milestone 등록/유료 가입/비밀 등록은 수행하지 않았다.
로컬 .git/hooks/pre-commit 및 pre-push만 요청 범위에서 설치했다.
실제 .env/개인 인증 파일은 생성·열람하지 않았고 실제 환경변수값을 보고/기록하지 않았다.

## 실제 생성·수정 파일

공유 파일 전체 목록: [bootstrap-files.txt](bootstrap-files.txt).
기존 작업 파일 수정은 없고 모두 신규 공유 파일이다. 초기화 후 검증·독립 리뷰를 반영해 신규 파일을 보완했다.
로컬 생성물: `.venv/`, `.tools/bin/gitleaks`, `.pytest_cache/`, `.ruff_cache/`, `.coverage`, `coverage.xml`,
Python 캐시 및 위 .git/hooks 두 개. 로컬 생성물은 공유 후보에서 제외된다.

주요 결과는 src 기술 smoke/config, agents Markdown template, 세 담당 Spec/잠정 계약,
공통 Handbook 16종과 목차, 6 ADR, GitHub 양식/CI, 11 Skills/5 개발 agents, hooks/permissions,
ECC 선택 원본 10개+MIT/SHA256/수정 기록, uv.lock/공통 설정/초기화·진단·검증 스크립트다.

## 검증 환경과 실제 결과

macOS Intel, Python **3.12.4**, uv **0.11.8**, Claude Code CLI 버전 **2.1.331** 확인.
핵심: langgraph 1.2.24, claude-agent-sdk 0.2.188, mcp 2.3.0, Pydantic 2.14.4.
pyproject 직접 버전 및 uv.lock으로 전체 전이 의존성 고정. Python 범위 >=3.12,<3.13.
Intel Mac cryptography 설치는 소스 빌드가 필요했고 성공했다. 다른 OS 실제 실행은 미검증이다.

| 명령/검사 | 결과 | 근거/제한 |
|---|---|---|
| `uv lock`, `uv sync --locked`, `uv lock --check` | PASS | 99개 해석, 환경 설치/lock 확인 |
| `uv run --locked python scripts/bootstrap.py` | PASS | lock 설치/Gitleaks 해시 검증/hooks/doctor |
| `uv run --locked python scripts/doctor.py` | PASS | Python/uv/Gitleaks/pre-commit/pre-push/custom hooksPath 없음 |
| `uv run --locked python scripts/verify.py` | PASS | Ruff lint/format, Google docstyle, links/instructions, Pyright, pytest/cov, Gitleaks |
| pytest (verify 내부) | PASS | 32개, 네트워크 socket 차단; HR 업무 검증 아님 |
| coverage (src/hr_onboarding) | 측정 85% | statement+branch, 33 statements/6 branches; pytest에서 CLI entrypoint 미측정 |
| `uv run --locked python -m hr_onboarding` | PASS | Mock graph count: 1, 외부 모델/transport 호출 없음 |
| `uv run --locked pre-commit validate-config` | PASS | 공유 설정 형식 |
| `uv run --locked pre-commit run --all-files` | PASS | always_run shared verify 실제 실행 |
| `uv run --locked pip-audit --local --skip-editable` | PASS | 알려진 취약점 발견 없음; editable 자기 패키지 제외, 시점 한정 DB 조회 |
| ECC 원본 SHA256 | PASS | 11 파일, manifest와 일치 |
| Custom/ECC 파생 Skills 형식 검사 | PASS | 11 SKILL.md |
| CI YAML parse/Action SHA 태그 조회 | PASS | 문법 및 공식 태그 SHA 확인, 원격 Actions 실행은 아님 |
| Gitleaks 합성 문자열 탐지 | PASS | 실제 인증과 무관한 생성 문자열로 종료코드 1 확인, redacted |
| 독립 AI 정적 리뷰 | PASS | 구현자와 별도 agent가 직접 파일 검토, 2건 수정 후 재검토 완료 |
| GitHub 기존 Issue 조회 | PASS | 연결 조회 0건; 등록 전 권한/중복 재확인 필요 |
| 실제 GitHub Actions/Ubuntu CI/required checks | NOT RUN | push/외부 변경 승인 없음 |
| 실제 Claude 인증 세션 hook/permission 통합 | NOT RUN | 비과금 payload 단위 검증만 수행, /hooks·/permissions 수동 확인 필요 |
| 실제 SDK query·MCP transport/쓰기·LLM 평가 | NOT RUN | 인증·고객사·비용 승인 없고 범위 밖 |
| Sonar scan/Quality Gate | NOT RUN | CI만, 기본 비활성, 외부 전송 승인/설정 미확인 |
| 사람 리뷰/첫 commit 예외 승인 | NOT RUN | 사용자/팀 검토 대기 |
| HR Schema/State/규칙/공통 fixtures/업무 통합 | NOT RUN | 샘플 미수령으로 보류 |

초기 coverage는 측정하며 이후 80% 목표다. 85%는 기술 소스 기준으로 업무 완성도나 보안 보증이 아니다.
Gitleaks는 현재 공유 후보 파일 중심 검사이며 이 저장소는 최초 commit 전이라 과거 이력이 없다.
정상 초기화라도 hooks/개인 설정/셸/직접 도구 실행은 우회 가능하다. 완전한 권한 격리로 보고하지 않는다.

## 실패를 통해 확인하고 수정한 사항

- 최초 테스트는 MCP 2.x `isError` 속성 변경으로 1 FAIL이었다. 설치 버전의 `is_error`로 수정 후 PASS.
- Ruff long line/고정 테스트 subprocess 진단 및 초기 보고서 링크를 정리했다. 최종 기본 검사 모두 PASS.
- pytest-asyncio fixture loop scope를 명시해 버전 변경 경고를 해소했다.
- SDK `allowed_tools=[]`만 믿지 않고 tools=[]/setting_sources=[]/skills=[]/strict_mcp_config를 명시했다.
- 독립 리뷰 2건: PATH Python hook → .venv Python 고정, Grep/Glob 민감 경로/루트 전체 검색 차단과 회귀 검증 추가.
- 첫 Gitleaks 합성 probe는 예시 allowlist에 의해 검출되지 않았다. 실제 계정 없는 무작위 합성 probe로 기본 탐지 종료코드 1을 확인했다.

## 결정/가정/남은 차단

확정 정책과 추천은 [범위](project-scope.md), [open questions](open-questions.md), ADR에 구분했다.
이전 분담은 예빈님(계획/진행), 사용자 본인(안내/준비 요청), 정현님(검토/HITL/승인)으로 문서에 반영하되
현재 유효성/공통 모듈 담당/리뷰 대체자는 팀 확인을 남겼다. 각 담당 계약은 미정 필드 없이 질문만 준비했다.

차단: 고객사 비식별 샘플/규칙/보존·삭제, 공통 계약, 실제 LLM 비용·인증/MCP 권한,
Sonar 외부 분석 허용/Private/CI-based analysis/키·토큰, GitHub 플랜/보호/최초 commit 승인,
보안 연락 담당 및 각 팀원 개인 설정 충돌 확인. 초기화와 별도로 사람 결정이 필요하다.
[Issue 초안 3건](issue-drafts/task-team-settings.md)을 준비했으며 아직 등록하지 않았다.

## 팀원 첫 실행과 수동 설정

```bash
cd /Users/sleepyowl/Projects/onboarding
uv run --locked python scripts/bootstrap.py
uv run --locked python scripts/verify.py
uv run --locked python -m hr_onboarding
```

다른 팀원은 본인의 clone 경로에서 실행한다. 실제 .env/API key가 필요 없다.
그 다음 Handbook → 담당 Spec/계약 → DoR 검토 → 승인된 작은 브랜치로 진행한다.
빈 저장소 첫 commit은 명시 예외 승인 후 사람이 수행한다. 현재 초기화 파일은 아직 미추적이다.

GitHub 관리자는 플랜/Private/계정 2FA/labels/Projects/milestone/리뷰·squash 정책을 확인한다.
Free Private 보호 강제 제한은 [GitHub 안내](guides/github-guide.md)에 명시했다.
Sonar는 기존 프로젝트만 사용한다. 외부 분석 허용·Private·CI-based를 확인하고
`SONAR_TOKEN` Secret, `SONAR_ORGANIZATION`/`SONAR_PROJECT_KEY` Variables를 관리자가 등록한다.
승인 후 `SONAR_ENABLED=true`, `EXTERNAL_ANALYSIS_APPROVED=true`와 수동 main 실행 `run_sonar=true`가 필요하다.
기본 PR CI는 인증이 없고 Sonar는 NOT RUN으로 보고한다. 실제 설정/등록/전송은 하지 않았다.

## README 기반 개발 온보딩 보완

[루트 README](../README.md)에 팀원별 출발점과 구현 위치를 안내하고, 주요 작업 디렉터리 11곳에 README를 추가했다. 기존 fixtures 안내도 연결했다. README 최신화와 링크·명령 확인은 [기여 완료 기준](../CONTRIBUTING.md)과 [초기화 인수 조건](specs/0001-bootstrap.md)에 포함된다.

macOS에서 README의 서로 다른 실행 명령 11개가 모두 통과했다. 전체 공통 검사에서 문서 94개, 테스트 32개, 커버리지 85%를 확인했다. 검증 범위는 로컬 기술 예제와 문서다.
