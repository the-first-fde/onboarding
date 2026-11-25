# 공통 개발 절차 — 사람과 Claude Code

[루트 README](README.md)와 작업 디렉터리의 README는 사람과 AI의 공통 개발 안내다. 공통 절차는 [Handbook](docs/guides/README.md)에 있다. Claude Code는 착수 전에 루트와 작업 경로에 적용되는 README.md·CLAUDE.md를 확인한다. [AI 필수 지침](CLAUDE.md)

## DoR: 시작할 준비

- Issue 초안/기존 중복 확인, 담당자, 작은 범위, Spec 인수 조건이 있다.
- 확인된 사실과 가정, 입력/출력, 승인·보안 경계, 의존성과 차단 사항이 구분된다.
- 담당자와 작업 위치, 인접 모듈과 주고받는 결과를 README 및 Spec에서 확인했다.
- 필요한 업무 계약이 미확정이면 의존 업무 구현을 시작하지 않는다.
- 작업 브랜치와 기존 변경을 확인했다. 실제 외부 실행은 별도 승인을 받는다.

## 구현과 DoD

1. 승인된 작은 범위의 Spec을 검토한다. 필요한 테스트의 RED/GREEN 증거를 기록한다.
2. 영어 식별자/타입 힌트/한국어 Google Docstring으로 최소 구현한다.
3. `uv run --locked python scripts/verify.py`와 변경 검토를 수행한다.
4. 독립 AI 리뷰 + CI + 사람 리뷰를 모두 확보한다. 미실행이면 NOT RUN.
5. 관련 Spec/ADR/계약/환경변수 명세를 갱신한다. 새 주요 개발 디렉터리에는 README를 작성하고 기존 개발 안내가 달라졌다면 같은 변경에서 갱신한다. 상대 경로 링크와 영향을 받는 예제·명령을 실제로 검증하고 변경 경로와 결과를 PR에 적는다. README 항목에 적용할 변경이 없으면 그 근거를 남긴다.
6. 일반 1명, 공통 State/오케스트레이터/보안/승인/MCP 등 고위험 2명 사람 승인을 권장한다.
7. 승인 후 변경이 생기면 영향 부분을 재검토하고 재승인한다. squash merge 추천.

DoD는 관련 검사 PASS, 인수 조건 충족, 문서와 보안 검토, 독립 AI·CI·사람 리뷰,
관련 README의 작성·최신화와 링크·명령 확인, 남은 위험의 공개 및 승인이다. 초기화 smoke PASS는 업무 인수 조건 충족을 의미하지 않는다.

## Git 및 승인

GitHub Flow: main → 작은 feature/bug/task 브랜치 → PR → 리뷰/CI → squash → main.
Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
최초 빈 저장소는 예외 승인을 받아 사람이 초기 commit을 만들고 이후부터 PR 절차를 적용한다.
AI의 자동 commit/push/merge/remote 변경은 금지. 등록·가입·비밀 설정도 별도 승인 필요.
자세한 명령과 충돌/revert 절차는 [Git 안내](docs/guides/git-guide.md).

## No Silent Issues

팀 판단/범위 밖/차단 문제 발견 즉시 사용자에게 사실·영향·필요 결정을 보고한다. 문서와 코드 중 기준을 팀이 결정해야 하면 양쪽 위치와 차이를 기록하고 Issue 등록을 제안한다.
기존 Issue 중복을 읽기 전용 확인하고 공통 Issue 양식 초안 및 등록 승인을 요청한다.
조회할 수 없으면 중복 확인 NOT RUN. 승인 없이 등록하거나 범위 밖 문제를 임의 수정하지 않는다.
안전한 독립 작업은 계속한다. 보안은 민감정보 없이 제한된 팀 채널로 보고한다.

실제 환경변수값/비밀/고객사 원본 데이터는 Git·로그·AI 입력에 넣지 않는다.
공유 불필요 파일은 ignore, 공통 설정/uv.lock/검토된 가상 fixtures는 추적한다.
