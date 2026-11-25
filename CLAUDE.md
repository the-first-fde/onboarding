# The First 공통 지침

## 범위와 근거
- 3인 HR onboarding, 제출 2026-12-03 23:59 KST.
- 초기화 명세: [docs/specs/0001-bootstrap.md](docs/specs/0001-bootstrap.md).
- Python 3.12, uv.lock, LangGraph 오케스트레이션, Claude Agent SDK 실행, Markdown 업무 정의, MCP.
- 프론트엔드/FastAPI 없음. 샘플 수령 전 HR Schema/공통 State/업무 규칙/공통 업무 fixtures 확정 금지.
- 확인된 사실과 잠정 가정은 [open questions](docs/open-questions.md)에 구분한다.
- 실제 고객사 데이터와 실제 인증을 사용하지 않는다. 실제 MCP 쓰기는 금지한다.
- 실제 메일과 입사 확정은 사람이 수동 수행한다.

## 작업 방법
- [공통 Handbook](docs/guides/README.md), [CONTRIBUTING](CONTRIBUTING.md)를 사람/Claude가 함께 사용한다.
- 변경 전 기존 파일과 Git 상태를 확인하고 보존한다. 작은 Issue/Spec/PR 단위로 작업한다.
- 명세 → 인수 조건/테스트 → 최소 구현 → 검증 → 독립 AI 리뷰 → 사람 리뷰.
- 영어 식별자, 타입 힌트, 한국어 설명의 Google Style Docstring을 사용한다.
- 실행 검증은 `uv run --locked python scripts/verify.py`.
- PASS/FAIL/NOT RUN을 실제 증거로 구분한다. 초기 커버리지 측정, 이후 80% 목표.
- 개발 agents는 `.claude/agents/`, 업무 agents는 `agents/`. 런타임에 개발 도구 권한을 주지 않는다.

## 승인과 No Silent Issues
- commit/push/merge/remote 변경/Issue·milestone·PR 외부 등록/유료 가입/비밀 등록은 별도 명시 승인 필요.
- 최초 commit도 예외 승인 후 사람이 실행한다. 일반 작업은 feature 브랜치에서 진행한다.
- 자동 commit/push/merge, ECC 전체 설치/자동 갱신/지속 학습을 금지한다.
- 팀 판단/범위 밖/차단 문제를 발견하면 즉시 보고한다. 임의 수정하지 않는다.
- 조회 가능한 기존 Issue에서 중복을 확인하고 공통 양식 초안을 작성해 등록 승인을 요청한다.
- 조회 불가면 중복 확인 NOT RUN으로 표시한다. 안전하고 독립적인 작업은 계속한다.
- 보안 문제는 비밀값/개인정보를 제외해 보고한다. 공개 Issue에 민감 내용을 기록하지 않는다.

## 비밀과 외부 실행
- 실제 환경변수 값/비밀은 Private Git에도 절대 등록하지 않는다.
- 실제 `.env`, 인증 파일, 개인 설정은 생성·열람·출력하지 않는다. `.env.example`만 명세로 사용한다.
- 로그/AI 입력/Issue/PR에 비밀 또는 HR 원본 데이터를 넣지 않는다.
- 공유 불필요 파일은 `.gitignore`, 공통 설정/uv.lock/검토된 가상 fixtures는 추적한다.
- Sonar는 CI 전용이다. 로컬 설치/호출/verify/pre-commit에 추가하지 않는다.
- Sonar 기존 Organization/Project를 재사용한다. 외부 분석 승인 전 활성화/전송하지 않는다.
- 세부 정책: [SECURITY](SECURITY.md), [보안 가이드](docs/guides/security-guide.md).

## 지침 탐색
- 착수 전에 루트 [README](README.md)와 이 파일을 읽고, 작업 경로의 상위·대상 디렉터리에 있는 README.md와 CLAUDE.md를 확인한다. 대상에 별도 문서가 없으면 가장 가까운 상위 안내를 따른다.
- 구현 범위를 정하기 전에 해당 Issue(있다면), Spec, 잠정 데이터 계약을 읽고 내 작업과 인접 모듈의 책임을 확인한다. 개발 안내와 실제 구현이 다르면 두 위치와 영향을 사용자에게 보고한다.
- README는 사람과 AI가 함께 보는 개발 안내다. CLAUDE.md는 AI가 준수할 필수 지침이다. 관련 작업 경로의 지침만 읽는다.
- 구현으로 작업 위치·동작·명령·의존성·테스트 방법이 바뀌면 관련 README를 같은 변경에서 갱신하고 링크와 명령을 검증한다.
- 문서와 코드의 차이 중 팀 판단이 필요한 것은 No Silent Issues에 따라 근거와 영향, 확인할 결정을 공유하고 Issue 등록을 제안한다.
- 각 CLAUDE.md는 200줄 이내, 중복 규칙은 기준 문서에 링크한다.
- ECC 원본은 `third_party/ecc/`, 실행용 수정본은 `.claude/`. 프로젝트 정책이 우선한다.
- hooks/permissions는 보조 장치다. 개인 설정·셸·심볼릭 링크·직접 도구 실행으로 우회 가능하다.
- 모르는 설정을 임의 허용하지 말고 `/permissions`, `/hooks`로 확인한다.
