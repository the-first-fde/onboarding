# 확인할 사항과 차단 요인

| ID | 상태 | 내용 | 결정 주체 / 해제 조건 |
|---|---|---|---|
| Q01 | BLOCKED | 샘플/업무 규칙/HR 계약/공통 fixtures | 고객사·팀: 비식별 샘플 및 정책 확인 |
| Q02 | NEEDS_CLARIFICATION | 이전 대화의 3인 업무 분담 재확인/공통 모듈 소유자 | 팀: 기록된 분담 확인 및 공통 담당·리뷰 대체자 지정 |
| Q03 | NEEDS_CLARIFICATION | GitHub 플랜/Private/리뷰 강제 여부 | 관리자: Free Private 제약 확인, 필요 시 Team 검토 |
| Q04 | BLOCKED | Sonar 외부 분석 허용/Private/CI-based analysis/키 | 고객사·관리자: 설정과 전송 승인 |
| Q05 | NEEDS_CLARIFICATION | 실제 LLM 인증/모델/비용 한도 | 팀: 개인 인증과 예산 합의 |
| Q06 | DEFERRED | 실제 MCP 연동·권한·쓰기 경계 | 고객사·팀: 별도 Spec/승인 |
| Q07 | DEFERRED | State 영속화/재시도/멱등성/스케줄 | 팀: 업무 계약 후 ADR |
| Q08 | NEEDS_CLARIFICATION | 데이터 보존/삭제/소유권/공개 정책 | 고객사·교육 과정 확인 |
| Q09 | NEEDS_CLARIFICATION | 최초 commit 예외 승인/제출 버전 태그 | 팀 리더: 리뷰 후 명시 승인 |
| Q10 | NEEDS_CLARIFICATION | 보안 연락 담당/비공개 신고 채널 | 팀: 지정 전 공개 상세 금지 |
| Q11 | NEEDS_CLARIFICATION | Claude Code 개인 설정 충돌/CLI 실제 hook 동작 | 각 팀원: /hooks·/permissions 및 안전한 대화형 확인 |

초기화 작업은 위의 업무/외부 연동 결정을 대신하지 않는다. 실제 Issue 등록은 미승인 상태로 수행하지 않았다.
등록 전 기존 Issue를 중복 조회한다. 2026-11-25 연결 GitHub에서 `repo:the-first-fde/onboarding is:issue` 조회 결과 0건.
등록 전 접근 권한 범위와 중복을 다시 확인한다. [등록 초안](issue-drafts/task-team-settings.md) 등 3건을 준비했다.
팀 판단이 필요한 새 문제를 발견하면 즉시 알리고 .github Issue 양식으로 초안을 제시한다.
