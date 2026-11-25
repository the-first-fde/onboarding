# README 개발 온보딩 검수

## 기존 문서에서 확인한 문제

루트 문서는 설치·아키텍처·담당 위치를 안내했지만 고객 문제, 기술 선택 이유, 담당별 산출물과 협의 사항, 복제 후 착수 절차, Claude Code/ECC, GitHub 협업, 검증 및 보안 흐름이 별도 섹션으로 충분히 설명되지 않았다. 하위 README는 6~17줄의 개요 위주로 입출력·담당자·절차·예제·실패 대응·완료 조건을 찾기 어려웠다. Handbook 목차는 공통 문서를 찾는 데 적합해 탐색용 문서로 유지했다.

작업 전 Git은 첫 commit이 없는 main이었으며 초기화 파일은 미추적 상태였다. 실제 디렉터리와 공개 가능한 저장소 파일만 기준으로 적용했다.

## 파일별 검수 결과

**구성**은 14개 필수 항목과 설명 수준을 확인한다. **착수**는 담당·개발 위치·입출력·의존성·개념·절차를 확인한다. **예제**는 기술 예제와 Claude Code 요청을 확인한다. **검증**은 실행·실패 대응·완료 기준·미결정 가정·상대 링크를 확인한다. 루트는 루트 전용 양식으로 확인한다.

| README | 구성·설명 | 담당·착수 | 예제·Claude 요청 | 검증·완료·제약·링크 | 재검수 근거 |
|---|---|---|---|---|---|
| [루트](../README.md) | 14/14 | 3인별 Spec·계약·산출물·협의 | 목표 흐름과 5개 요청 | 설치·공통 검증·보안과 한계 | 환경 설치, 진단, mock CLI, verify |
| [업무 Markdown](../agents/README.md) | 14/14 | 3인 역할별 작성 | Python 양식 읽기·5개 요청 | 양식 검증과 수동 발송 경계 | Markdown 단일 테스트 |
| [Python 소스](../src/README.md) | 14/14 | 3인 기능별 배치 | 타입·docstring 예제·5개 요청 | 배치와 인터페이스 기준 | smoke 테스트 |
| [패키지](../src/hr_onboarding/README.md) | 14/14 | 공통 담당 미정·모듈별 위치 | Python 실행·5개 요청 | 진입점과 인증 없는 실행 | mock CLI |
| [워크플로우](../src/hr_onboarding/workflows/README.md) | 14/14 | 계획·검토·초안 경계 | 카운터 그래프·5개 요청 | 상태·승인 미확정 및 검증 기준 | 그래프 단일 테스트 |
| [SDK 연결](../src/hr_onboarding/agents/README.md) | 14/14 | 3인 입출력과 연결 위치 | 안전 옵션·5개 요청 | SDK 실행 보류와 권한 조건 | 옵션 단일 테스트 |
| [MCP](../src/hr_onboarding/integrations/README.md) | 14/14 | 공통 담당 미정·경계 | 가상 응답·5개 요청 | 쓰기 금지와 승인 조건 | MCP mock 단일 테스트 |
| [테스트](../tests/README.md) | 14/14 | 3인 검증 대상 | assert 예제·5개 요청 | 기록·실패 대응·업무 검증 보류 | smoke, hook, verify |
| [fixtures](../fixtures/README.md) | 14/14 | 3인 가상 자료 필요성 | 가상 카운터·5개 요청 | 개인정보 금지와 계약 보류 | 가상 카운터 단일 테스트 |
| [스크립트](../scripts/README.md) | 14/14 | 공통 담당 미정·도구 책임 | 종료코드 사례·5개 요청 | 진단·검사 기준·실패 대응 | 문서 검사, doctor, verify |
| [문서](README.md) | 14/14 | 3인 Spec 및 계약 | 질문 기록 사례·5개 요청 | 근거 상태·링크 | 문서 검사 |
| [Claude Code](../.claude/README.md) | 14/14 | 공통 담당 미정·역할 구분 | hook 사례·5개 요청 | 가상 권한 검증과 실제 적용 한계 | hook 테스트 |
| [GitHub](../.github/README.md) | 14/14 | 공통 담당 미정·CI 책임 | PR 증거 사례·5개 요청 | 원격 CI와 로컬 결과 구분 | verify |
| [Handbook 목차](guides/README.md) | 목차 역할 유지 | 루트와 가이드로 연결 | 상세 절차로 이동 | 적용 대상 양식 제외 | 상대 링크 검사 |
| schemas · services · storage · scheduler | 적용 제외 | 디렉터리 없음 | 합의 후 배치 | 현재 생성하지 않음 | 저장소 구조 확인 |

구성 확인은 제목 존재 여부와 각 섹션에 실제 작업을 시작할 수 있는 근거·실행 방법이 있는지를 함께 확인했다. Python에 적용되는 코드 예제에는 타입 힌트와 한국어 Google Style Docstring을 사용했다. 문서·PR·hook·스크립트 안내는 각 영역의 작업 결과와 확인 절차를 예시로 사용했다.

## 반영 범위와 검증 상태

루트와 작업 디렉터리 README, Handbook 목차, 루트 Claude 지침, 5개 작업 Skills, 기여 기준, PR 양식, 초기화 Spec 및 담당자 문서의 분담 표현을 맞췄다. 작업 Skills는 plan-task, implement-task, review-changes, prepare-pr, create-issue다. 담당자 표기는 범위 문서와 안내 Spec·잠정 계약을 맞췄으며 수정 요청 범위를 검토 Spec에 반영했다.

실제 Claude 인증 세션·원격 GitHub Actions·Sonar·실제 MCP 호출과 고객사 업무 검증은 별도 상태다. 고객사 샘플과 계약이 없으므로 제안 경로 및 산출물의 모양은 업무 계약으로 사용하지 않는다.

## 실제 검증 결과

| 검사 | 결과 | 확인한 범위 |
|---|---|---|
| README 전체 인벤토리 및 필수 항목 | PASS | 14개 검토. 적용 대상 13개에서 14개 항목과 본문 확인, Handbook 목차 1개 별도 |
| 상대 링크와 개발 위치 | PASS | README 전체 로컬 링크 대상, 기존 문서 검사 95개, 4개 미사용 디렉터리 제외 |
| 공식 기술 문서 링크 | PASS | 새로 연결한 공식 문서 URL 11개 응답 확인 |
| README에 적힌 로컬 명령 | PASS | 서로 다른 명령 11개. 환경 설치, 진단, mock CLI, 개별 pytest 및 공통 검사 |
| README Python 코드 예제 | PASS | 9개 블록을 실제 가상 환경에서 각각 실행 |
| 공통 verify | PASS | Ruff lint·format, 문서, Pyright, pytest 32개, 초기 소스 커버리지 85%, Gitleaks |
| 실제 Claude Code 프롬프트·권한 / 원격 CI·Sonar / 고객사 업무 | NOT RUN | 로컬 기술 검증 범위. Mermaid의 GitHub 화면 표시 역시 미확인 |

첫 공통 검사에서 문서 코드 블록의 빈 줄 서식이 Ruff 기준과 달라 FAIL이었다. 예제만 Ruff로 정리한 뒤 예제 실행과 공통 검사에서 PASS를 확인했다. 고객사 문제는 프로젝트가 해결하려는 배경으로 설명했고 실제 사례나 계약을 추가하지 않았다.
