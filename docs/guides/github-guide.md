# GitHub에서 Issue부터 PR까지

**학습 목표**는 팀의 결정과 구현 증거를 한 변경에 연결하고, 현재 작업 밖의 문제를 숨기지 않고 공유하는 것이다. 승인된 저장소를 볼 수 있는 개인 계정을 준비한다. 아래 실습은 로컬 양식으로 따라갈 수 있다.

Issue는 문제·결정을 추적하는 카드, Label은 유형이나 위험을 나타내는 표식, Milestone은 제출 목표와 날짜, Projects는 여러 카드의 흐름과 차단을 보는 보드다. PR(Pull Request)은 변경 검토 요청이고 Review는 승인·변경 요청 및 근거다. 서로 연결하면 “왜 바뀌었고 누가 확인했는가”를 나중에도 찾을 수 있다.

## 실습 · 준비 요청의 입력이 미정인 경우

1. 관련 [Spec](../specs/communication-preparation.md), [잠정 계약](../contracts/communication-preparation.md), [연구 Issue 초안](../issue-drafts/research-data-contract.md)을 확인한다. 팀 판단이 필요하면 즉시 근거와 영향부터 공유한다. 권한 있는 계정으로 Issues에서 제목과 상태를 열린 항목과 닫힌 항목 모두 검색한다. 중복이면 기존 카드에 연결할 내용을 제안한다. 접근 불가면 조회를 NOT RUN으로 남긴다.
2. [.github 공통 양식](../../.github/ISSUE_TEMPLATE)을 골라 로컬로 초안을 쓴다. 새 동작은 feature, 재현 가능한 오류는 bug, 동작 유지 개선은 refactor, 불확실성은 research, 운영 작업은 task다. 아래는 등록 전 초안의 핵심 부분이다.

```text
종류: research
제목: 준비 요청의 전달 대상과 근거 확인
근거: 안내 준비 잠정 계약에 대상과 승인 근거가 미정
영향: 실제 요청 생성 규칙과 업무 테스트가 차단됨
인수 조건: 담당자가 확인된 근거와 남은 질문을 잠정 계약에 기록
제안 표시: needs-decision, status:blocked
```

3. 명시 승인 뒤 등록하고, 관리자가 제공한 라벨과 제출 Milestone(2026-12-03 23:59 KST)을 연결한다. 보드에서 Ready·In Progress·Review·Done과 Blocked를 구분한다. 마일스톤은 [팀 양식](../../.github/templates/milestone.md)을 쓴다. 라벨은 양식에서 자동으로 지정되지 않는다.
4. 근거가 확보된 범위만 브랜치로 옮긴다. [PR 양식](../../.github/pull_request_template.md)에 Issue·Spec·README 변경과 실제 검증을 연결한다. 리뷰어가 [리뷰 양식](../../.github/templates/review.md)에 결정과 증거를 기록한다.

웹에서 작성한 초안은 제출 버튼을 누를 때 외부에 공개 범위가 생긴다. 관리·등록·댓글·병합은 승인 범위를 확인한다. 변경이 안 보이면 대상 원격과 계정 권한을 확인하고, Issues 검색 누락은 레포 필터와 open/closed 범위를 확인한다. 보호 브랜치를 강제할 수 없는 GitHub Free 조직의 Private 저장소에서도 팀 리뷰 절차는 적용된다. 현재 원격 정책이 구성됐다고 가정하지 않는다.

**좋은 예**는 결정할 질문, 담당자, 차단된 일과 계속 가능한 기술 확인을 분리한다. **피할 예**는 범위 밖 변경을 섞고 공개 Issue에 실제 고객사 자료를 붙이는 것이다.

**Claude Code 연습** — “관련 README·Spec·계약을 확인해 중복 후보와 research Issue 초안만 만들어줘. 당장 계속할 수 있는 검증도 표시해줘.” 사람이 검색 범위와 근거, 개인정보 없는 설명을 확인하고 등록 여부를 결정한다. PR 초안도 diff와 실제 실행 증거를 직접 대조한다.

- [ ] Issue·Label·Milestone·Projects·PR·Review의 관계를 설명한다.
- [ ] 팀 결정이 필요한 문제를 양식에 적고 등록 전 확인한다.

Issue와 Project 상태는 Notion에도 한 방향으로 복사할 수 있다. 기준은 계속 GitHub이며 설정·운영은 [GitHub ↔ Notion 연동 가이드](collaboration-integration-guide.md)를 따른다.

[GitHub Issues 공식 문서](https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/about-issues) · [보호 브랜치 적용 범위](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
