# Engineering Handbook 감사 및 재검수

## 기존 상태와 적용 범위

작업 시작점은 첫 commit이 없는 main이었다. 제품 구조, 루트·문서 작업 지침, 기여 정책, 실제 스크립트·테스트와 Handbook 17개 원문을 변경 전에 확인했다. 기존 문서는 프로젝트 금지 사항과 핵심 명령을 잘 모아 두었지만, 문서별로 필요한 배경·설치와 사용 단계·실패 진단·AI 증거 검토·학습 확인이 부족했다. 아래 표는 기존 부족점과 실제 보완 내용을 함께 기록한다. README는 담당과 위치, 가이드는 개념·실습·복구, CONTRIBUTING은 협업 기준, CLAUDE.md는 AI 행동, Spec과 ADR은 각각 요구 및 결정 근거를 맡는다.

## 파일별 감사

| 문서 | 기존 문제점 | 보완 및 재검수 근거 | 남은 제약 |
|---|---|---|---|
| [README](guides/README.md) | 링크 목록만 있어 첫 학습·문제별 진입점 부족 | 여섯 학습 경로, 상황별 탐색표, 문서 역할·실습 범위를 확인 | 신규 팀원의 사용성 인터뷰 미실행 |
| [처음 실행](guides/getting-started.md) | 설치 순서는 있었으나 용어·OS·복제 실패 대응 부족 | 설치·진단·mock 재현, WSL2와 Linux 설치 차이·부작용·출력 해석 추가 | 새 OS 설치·원격 clone 미실행 |
| [Git](guides/git-guide.md) | 개념과 상태 모델, 스테이징 실수 대응 부족 | 상태·diff 읽기, 한 변경의 GitHub Flow, 안전한 stage/commit/branch/conflict 대응 | Git 쓰기·원격 흐름은 설명 예시 |
| [GitHub](guides/github-guide.md) | 유형과 절차만 있어 실제 양식 선택과 결정의 예가 부족 | 잠정 계약 기반 research 초안, 라벨·마일스톤·보드·PR·리뷰 연결 | 웹 등록·서버 보호 설정 미실행 |
| [SDD](guides/development-guide.md) | 요구를 실행 가능한 기준으로 바꾸는 예 부족 | 빈 Markdown 오류로 인수 조건을 보여주고 실제 단일 테스트를 연결 | 고객사 업무 인수 보류 |
| [Python](guides/coding-conventions.md) | 코딩 규칙과 한 예제 중심 | 패키지·함수·타입·예외·async, 성공/실패 카운터 예제, Ruff 검증 | 업무 코드 수정 없음 |
| [Claude Code](guides/claude-code-guide.md) | 실행·스킬 목록에서 인간 검토와 권한 판단이 약함 | 컨텍스트·세션·권한 판단과 계획/승인/diff/테스트/Issue 실습, 버전 조회 | 인증 CLI와 슬래시 명령 미실행 |
| [하네스](guides/harness-guide.md) | 구성요소 열거 위주 | 개발/런타임 책임, 실제 settings와 hooks 테스트 기반 판단 실습 | 실제 세션 훅 통합 미실행 |
| [Agent](guides/agent-guide.md) | 옵션 제약은 있었으나 정의·출력·호출 단계 부족 | 임시 Markdown 작성과 로컬 옵션만 검증, SDK와 양식 테스트 | 모델 query·구조화된 실제 모델 응답 미실행 |
| [워크플로우](guides/workflow-guide.md) | 카운터 소개에 그쳐 체크포인트·재개 설명 부족 | 메모리 승인·거부 양쪽 재개와 조건부 분기 검증 | 실제 승인 권한·영속화 미구현 |
| [테스트](guides/testing-guide.md) | 테스트 명령 위주, 실패 결과 읽기·평가 구분 부족 | 임시 pytest에서 의도한 실패와 수정 후 통과 재현, fixture/mock/fake/평가 구분 | 계약·모델 평가 미실행 |
| [리뷰](guides/review-guide.md) | 절차 나열, 입문자가 참여할 업무 판정 사례 부족 | 수동 발송 경계 예시, diff, 독립 AI·사람 판정과 재승인 | 원격 리뷰·병합 미실행 |
| [체크리스트](guides/review-checklist.md) | 질문만 있어 확인 근거와 실패 대응이 없음 | 항목별 증거·미실행·수정 요청·재검토 기준 확인 | 실제 PR 적용 미실행 |
| [품질과 CI](guides/quality-guide.md) | 설정·정책 위주, 실패 단계 추적 설명 부족 | 실제 YAML-로컬 verify 연결, 로그 해석, CI 전용 Sonar 승인 조건 | 원격 CI·Sonar Quality Gate 미실행 |
| [환경 변수](guides/environment-guide.md) | 변수 목록, 운영체제 설정 체험과 실패 진단 부족 | 공개 mock 값으로 프로세스 범위 확인, Secret과 Variables 구분 | 실제 설정·등록 미실행 |
| [보안](guides/security-guide.md) | 비밀 정책은 있으나 프롬프트 인젝션·권한 판단 실습 부족 | 가상 악성 지시와 ignore 경로 점검, 비공개 유출 대응 | 실제 시스템·자격 증명·사고 훈련 미실행 |
| [문제 해결](guides/troubleshooting.md) | 짧은 증상 목록, 원인·복구·상신 구분 부족 | 환경/Git/GitHub/SDK/MCP/CI 진단표와 재현 보고 실습 | 원격·타 OS 문제 재현 미실행 |

원격 작업과 권한 변경은 읽기용 시나리오다. 프로젝트의 비밀, 고객사 자료, 계약·데이터 모델의 미확정 상태, CI 전용 Sonar, Git 승인 절차를 유지했다.

## 실행 근거

| 점검 | 상태 | 실제 결과 |
|---|---|---|
| 문서별 교육 흐름과 상대 링크 | PASS | Handbook 17개와 작업 위치·설정·테스트 수동 대조. 저장소 문서 검사 96개 |
| 공식 참고 URL | PASS | 28개 응답 확인. 리디렉션이 있는 GitHub 링크는 공식 최종 경로 사용 |
| 로컬 명령 | PASS | Markdown의 bash 블록에 있는 서로 다른 명령 23개. 버전·루트·Git 읽기·bootstrap·doctor·mock·ignore·pytest·lint·verify |
| Python 학습 예제 | PASS | 가상 Agent 정의, 카운터 정상/오류, LangGraph의 중단 및 승인/거부 재개, pytest 실패·수정 후 통과 총 4종 |
| 임시 pytest 파일 실행 | PASS | 안내에 적힌 설정 경로로 의도한 실패 1건·성공 1건과 수정 후 성공 2건을 실제 확인 |
| 공통 verify | PASS | Ruff lint/format, 링크·지침, Pyright, pytest 32개, 소스 커버리지 85%, Gitleaks |
| 인증·실서비스·기타 OS | NOT RUN | 실제 Claude 세션, GitHub 쓰기/원격 CI/Sonar, 고객사 자료·MCP, macOS 외 신규 설치는 해당 환경과 승인에 따름 |

검증 환경은 macOS, Python 3.12.4, uv 0.11.8 및 조회한 Claude Code 2.1.331이다. bootstrap은 기존 로컬 학습 환경에서 해시 검증된 Gitleaks와 Git hooks를 준비했다. commit/push/merge는 수행하지 않았다. 첫 검수에서 Claude Code 실습 제목이 다른 가이드처럼 바로 검색되지 않아 명시한 뒤 재검증했다. 인증을 필요로 하는 실행 사례와 실제 고객사 업무 결과는 기술 실습의 통과 근거에 포함하지 않았다.
