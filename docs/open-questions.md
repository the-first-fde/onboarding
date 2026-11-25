# 확인할 사항과 차단 요인

| ID | 상태 | 내용 | 결정 주체 / 해제 조건 |
|---|---|---|---|
| Q01 | NEEDS_CLARIFICATION | 샘플/업무 규칙/HR 계약/공통 fixtures — 2026-11-25 가명·가공 데이터팩 수령(로컬 전용), 담당자별 검토 중 | 팀: 데이터팩 근거로 계약 작성 후 3인 조정 |
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
| Q12 | NEEDS_CLARIFICATION | 안내 메일 승인 지점(3-1)에서 리더 확인 범위: 메일 전체인지, 리더 제공 내용(ON-34)만인지 | 팀: [안내·준비 Spec](specs/communication-preparation.md) 권장안 검토 |
| Q13 | NEEDS_CLARIFICATION | 준비 요청 승인 지점(3-3)의 승인자: 인사 담당자인지, 요청 수신 담당자인지 | 팀: [안내·준비 Spec](specs/communication-preparation.md) 권장안 검토 |
| Q14 | NEEDS_CLARIFICATION | 온보딩 체크리스트 경계: 입사자별 인스턴스와 진행 상태는 계획·진행, 담당별 목록 추출은 안내·준비로 나눌지 | 예빈님·종은: 두 Spec의 입출력 합의 |
| Q15 | NEEDS_CLARIFICATION | 수습 안내 메일 M1~M13(데이터팩 `03_수습평가`)의 담당 | 팀: 분담 확인 또는 범위 제외 결정 |
| Q16 | NEEDS_CLARIFICATION | 리더 체크리스트 항목이 늦을 때 리마인드 초안을 만들지 | 팀: 안내·준비 범위 결정 |
| Q17 | NEEDS_CLARIFICATION | 데이터팩에서 참조만 하고 보내지 않은 파일(구성원명단 CSV, 신규입사자 안내자료, 사내규정) 요청 여부 | 팀 → 고객사: 필요하면 회신 요청 |
| Q18 | NEEDS_CLARIFICATION | 메일 초안 생성 때 입사자 이름을 AI에 넣을지, 자리표시자로 두고 발송 때 채울지 | 팀: 보안 가이드 2부 기준으로 결정 |
| Q19 | NEEDS_CLARIFICATION | 메일 1 이력서 줄("채용 절차 밖 합류자")을 판단할 입력 칸 | 팀·고객사: 입사 경로로 충분한지 확인 |
| Q20 | NEEDS_CLARIFICATION | 「확정+2일」 기준인 합격 확정일이 입사자 DB에 없음 | 팀: 채용 핸드오프에서 받을지 결정 |

초기화 작업은 위의 업무/외부 연동 결정을 대신하지 않는다. 실제 Issue 등록은 미승인 상태로 수행하지 않았다.
등록 전 기존 Issue를 중복 조회한다. 2026-11-25 연결 GitHub에서 `repo:the-first-fde/onboarding is:issue` 조회 결과 0건.
등록 전 접근 권한 범위와 중복을 다시 확인한다. [등록 초안](issue-drafts/task-team-settings.md) 등 3건을 준비했다.
팀 판단이 필요한 새 문제를 발견하면 즉시 알리고 .github Issue 양식으로 초안을 제시한다.
