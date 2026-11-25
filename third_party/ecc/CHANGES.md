# ECC 파생본 변경 기록 — 2026-11-25

| 원본 | 유지한 목적 | 프로젝트 변경 |
|---|---|---|
| python-patterns | 가독성, 타입, 명시적 오류 처리 | Python 3.12/uv/Ruff/한국어 Google Docstring에 한정; 장문 예제 제거 |
| python-testing | pytest fixtures/parametrize/async mock | 웹 API·DB 예제 제외; 실제 인증 없는 smoke; 업무 fixtures 보류 |
| tdd-workflow | RED/GREEN/refactor 및 실제 검증 증거 | 자동 staging/checkpoint commit 지시 제거; 명령 로그/PR로 증거; bootstrap은 기술 smoke |
| verification-loop | lint/type/test/security/diff 결과 | npm/build/grep 비밀 검색 제거; 동일 scripts/verify.py; 미실행 별도 보고 |
| security-review | 최소 권한/입력 검증/비밀 보호 | 웹/결제/DB 조치 제외; HR/MCP/외부 전송 승인 및 No Silent Issues |
| planner | 근거/작은 단계/의존성/위험 | 읽기 전용; 미수령 계약 확정 금지; 특정 유료 모델 강제 제거 |
| code-reviewer | 실제 diff 및 주변 맥락/증거 중심 판단 | 읽기 전용; 최초 미추적 파일도 포함; 원본 변경을 직접 수정하지 않음 |
| python-reviewer | 타입/예외/async/경로/주입 검토 | black/mypy/pylint 자동 추가 제거; Ruff/Pyright; 프레임워크 예제 제거 |
| tdd-guide | 테스트 먼저/경계/오류/독립성 | 읽기 전용 가이드; npm/Playwright/DB/자동 평가 강제 제거 |
| security-reviewer | 증거 중심 취약점/권한/유출 확인 | 읽기 전용; 실제 비밀 탐색·값 출력/외부 테스트 금지; 민감정보 제외 보고 |

모든 활성 파생본: 루트 정책 우선, 자동 Git 변경/외부 등록/지속 학습 금지.
초기 80% 강제 대신 측정 후 목표, runtime 권한 분리. 출처는 MIT 고지를 보존한다.
원본이 언급한 다른 Skills/agents/install scripts는 자동 설치하지 않는다.
