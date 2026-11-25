# The First Engineering Handbook

이 Handbook의 목표는 팀원이 기술의 목적을 이해하고, 작은 변경을 검증하고, 다른 사람이나 AI가 만든 결과를 근거로 리뷰할 수 있게 하는 것이다. 처음이라면 아래 경로를 순서대로 따라간다. 이미 환경이 준비됐다면 상황별 표에서 필요한 장을 바로 고른다.

작업 위치와 담당 범위는 [루트 README](../../README.md)와 모듈 README에 있다. 이 Handbook은 기술을 배우고 실제로 적용하는 방법을 설명한다. 공통 협업 기준은 [CONTRIBUTING](../../CONTRIBUTING.md), AI 행동·권한은 [CLAUDE.md](../../CLAUDE.md), 기능과 완료 조건은 [Spec](../specs/template.md), 기술 결정과 이유는 [ADR](../adr/template.md)에 기록한다.

## 입문 학습 경로

1. **환경 준비** — [처음 실행](getting-started.md)으로 설치·진단·mock을 마친다. [환경과 비밀](environment-guide.md)에서 예시 변수와 인증을 구분한다.
2. **Git과 협업** — [Git](git-guide.md)에서 작업 트리와 스테이지를 구분하고 [GitHub](github-guide.md)에서 가상 Issue→PR 흐름을 따라간다. [SDD](development-guide.md)로 인수 조건을 하나 작성한다.
3. **Python과 AI** — [코딩 규칙](coding-conventions.md)의 카운터 예제를 실행한 뒤 [Claude Code](claude-code-guide.md)의 계획·검토 절차와 [개발 하네스](harness-guide.md)의 권한 경계를 읽는다.
4. **Agent와 Workflow** — [Agent](agent-guide.md)에서 가상 에이전트 정의를 읽고 [LangGraph](workflow-guide.md)에서 승인 대기와 재개를 메모리 안에서 관찰한다.
5. **테스트와 리뷰** — [테스트](testing-guide.md)에서 실패를 일부러 만들어 원인을 해석하고, [리뷰](review-guide.md)와 [공통 체크리스트](review-checklist.md)로 산출물을 검토한다. [품질과 CI](quality-guide.md)에서 같은 검사 결과를 찾는다.
6. **보안과 복구** — [보안](security-guide.md)에서 가상 유출 사례와 승인 경계를 검토하고 [문제 해결](troubleshooting.md)로 증상·근거·질문을 정리한다.

## 상황별로 찾기

| 지금 필요한 일 | 열 문서 | 첫 확인 |
|---|---|---|
| 복제 직후 실행 방법이 막힘 | [처음 실행](getting-started.md) | 어느 루트에서 어떤 Python을 쓰는지 |
| 잘못 스테이지했거나 충돌이 남 | [Git](git-guide.md) | 상태에서 충돌과 스테이지를 구분 |
| 계약이 없거나 다른 담당자에게 영향 | [SDD](development-guide.md), [GitHub](github-guide.md) | 사실·가정·팀 결정 분리 |
| AI 코드와 권한 요청 검토 | [Claude Code](claude-code-guide.md), [하네스](harness-guide.md) | 바뀔 파일과 호출 목적 |
| 실제 에이전트 실행 범위 확인 | [Agent](agent-guide.md), [워크플로우](workflow-guide.md) | 가상 결과와 실제 외부 동작 구분 |
| 테스트나 CI에서 실패 | [테스트](testing-guide.md), [품질](quality-guide.md), [문제 해결](troubleshooting.md) | 첫 실패 단계와 정확한 테스트 이름 |
| 비밀 노출 또는 이상한 외부 도구 요청 | [보안](security-guide.md) | 값 없이 비공개 보고 |
| Notion에서 Issue·Project 진행 상태 보기 | [GitHub ↔ Notion 연동](collaboration-integration-guide.md) | dry-run 결과와 활성화 여부 |
| 병합 전에 확인할 사항 | [리뷰](review-guide.md), [체크리스트](review-checklist.md) | 현재 변경 버전의 증거와 사람 승인 |

별도 언급이 없으면 터미널의 현재 위치는 저장소 루트다. Python 블록은 임시 파일 또는 표준입력으로 실행하며 레포에 넣을 필요가 없다. Git·GitHub·Claude 외부 동작을 설명하는 **절차 예시**는 권한과 승인 전에는 읽기만 한다. 고객사 자료 없이 실행하는 모든 실습은 기술 예제다. 실습별 실제 실행 여부는 [Handbook 감사 보고](../handbook-audit.md)에 있다.
