# Spec 0001: 개발 기반 초기화

- 상태: CONFIRMED 범위, 구현/검증 결과는 [보고서](../bootstrap-report.md) 참조.
- 근거: 2026-11-25 사용자 명세 및 참조 대화 `6b06253a-257c-83ec-b672-273251b301e6`.
- 목적: 초보자 포함 3인이 동일 환경과 안전한 협업 절차로 개별 개발을 시작한다.

## 인수 조건

- 지정 경로 기존 파일·Git을 확인/보존하고 다른 경로에 프로젝트를 만들지 않는다.
- Python 3.12 호환 설치와 uv.lock 재현, API key 없는 기술 smoke를 제공한다.
- LangGraph async 노드, SDK 옵션/import, Markdown, MCP mock을 검증한다.
- Handbook/GitHub 양식/계층 지침/선택 ECC 출처·SHA·라이선스/Custom Skills를 제공한다.
- [루트 README](../../README.md)에서 목적·아키텍처·담당별 개발 위치·구현 순서·완료 기준을 찾을 수 있어야 한다. 주요 개발 디렉터리 README에는 예제·실행과 테스트 방법·의존성을 안내한다.
- Claude Code 착수 전 루트 및 작업 경로의 README·CLAUDE.md 확인, 구현 변경 시 README 최신화, 팀 판단이 필요한 문서·코드 불일치의 Issue 제안 절차를 [완료 기준](../../CONTRIBUTING.md)에 반영한다.
- 루트와 적용 대상 README의 14개 필수 항목, 상대 경로, 실행 명령·기술 예제를 파일별로 검증하고 [문서 검수](../readme-audit.md)에 기록한다. Handbook과 Spec에는 각 문서의 상세 근거를 유지한다.
- Gitleaks/pre-commit 설치·진단, 동일 verify, 최소 권한/고정 SHA/timeout/concurrency CI를 제공한다.
- Sonar는 CI만, 기존 project/coverage.xml 연결, 명시 승인·활성화 및 미설정 보고를 제공한다.
- 실제 결과와 NOT RUN, 초기 coverage, 남은 질문/결정/가정/팀원 시작 방법을 보고한다.

## 제외 및 실패 경계

실제 업무 기능/확정 HR Schema/State/규칙/업무 fixtures/프론트엔드/FastAPI 구현 제외.
실제 .env 생성·열람/비밀 등록/고객사 데이터/실제 LLM·MCP·Sonar 전송/자동 Git 변경 금지.
commit/push/merge/remote/Issue·PR·milestone 등록/유료 가입은 별도 승인 전 수행하지 않는다.
CI 원격 실행과 Claude Code 인증 세션을 통한 통합 검증은 접근/승인 없으면 NOT RUN.
