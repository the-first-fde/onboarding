# GitHub 협업과 CI

[프로젝트 시작 안내](../README.md) · [공통 착수·완료 기준](../CONTRIBUTING.md)

## 1. 이 디렉터리의 목적

Issue·PR·리뷰 기록과 GitHub 공통 검사 설정을 관리한다. 로컬 검사 정의는 scripts에 둔다.

## 2. 무엇을 개발해야 하는가?

사람과 Claude Code가 공동 양식을 사용하도록 유지한다. CI에 검사를 추가할 때 로컬 verify와의 일치, 권한, timeout, 워크플로 조건을 확인한다.

## 3. 담당자별 개발 업무

위치와 산출물은 제안이다. 담당 미정 항목은 팀에서 배정한다. 관련 GitHub Issue가 확정되면 번호를 연결한다. 연결된 로컬 Issue 초안은 14절에 있다.

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | Issue/PR 양식과 GitHub Actions | 검토 가능한 협업 양식과 재현 CI | [초기화 Spec](../docs/specs/0001-bootstrap.md) |

## 4. 개발에 필요한 기초 개념

Issue는 일의 단위, PR은 변경 검토 요청, Milestone은 여러 Issue의 목표다. CI는 GitHub의 실행 환경에서 검사를 자동으로 수행한다.

## 5. 파일 및 모듈별 역할

[ISSUE_TEMPLATE](ISSUE_TEMPLATE)과 [PR 양식](pull_request_template.md), [리뷰·마일스톤 양식](templates), [CI](workflows/ci.yml)가 실제 사용 파일이다. [Notion Sync](workflows/notion-sync.yml)는 CI와 분리된 협업 자동화로, Issue 이벤트·15분 예약·수동 실행에서 [동기화 스크립트](../scripts/collaboration/README.md)를 실행한다. 기본 비활성이며 설정은 [운영 가이드](../docs/guides/collaboration-integration-guide.md)를 따른다.

## 6. 입력 및 출력 데이터

입력은 PR diff·Spec·검증 증거와 잠금 환경이다. 출력은 리뷰 판단, CI 검사 상태와 커버리지다. Sonar 출력은 승인된 수동 분석에서만 생긴다.

## 7. 다른 모듈과의 관계

[verify](../scripts/README.md)를 사용한다. 리뷰어는 [기여 절차](../CONTRIBUTING.md)를 확인하고, Sonar 설정은 팀 승인 및 [품질 가이드](../docs/guides/quality-guide.md)를 따른다.

## 8. 단계별 개발 방법

1. 루트와 작업 경로의 README·CLAUDE.md, 관련 Issue·Spec·잠정 계약을 읽고 승인 범위를 확인한다.
2. 어떤 이벤트에서 어떤 단계가 실행되는지 ci.yml에서 확인한다. 협업 양식 변경은 새 규칙의 증거를 어느 칸에 적을지 확인한다.
3. 기존 기술 검증으로 기준을 잡고, 승인된 변경에서 새 동작을 작은 테스트로 만든 뒤 최소 구현한다.
4. 개별 테스트와 공통 verify를 실행한다. 결과·영향·README 변경을 독립 리뷰로 넘긴다.

## 9. 최소 구현 예제

아래는 이 영역의 작업 방식을 보여주는 기술 예제다. 고객사 업무 규칙이나 공통 데이터 계약을 정의하지 않는다.

```text
PR 검증 증거 예: shared verify = PASS · 업무 검증 = NOT RUN(샘플 미수령) · 관련 README와 명령 확인 기록
```

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 CI 또는 PR 양식 변경의 변경 파일·근거·첫 테스트를 제시해줘. 계획 승인을 기다려줘.”
- **코드 설명** “pull_request와 승인된 수동 Sonar 실행의 차이를 코드와 테스트를 근거로 처음 배우는 사람에게 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 승인된 양식 변경과 로컬 확인만 진행하고 실행 명령과 결과를 보여줘.”
- **영향 검토** “/review-changes로 권한·verify·커버리지·팀 리뷰에 미치는 영향에 영향이 있는지 확인하고 근거 파일을 적어줘.”
- **Issue 제안** “서버 보호 설정이나 Sonar 전송 승인 필요가 팀 판단을 요구하면 위치와 영향을 알려준 뒤 기존 Issue를 확인하고 /create-issue 초안을 제안해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 아래 명령을 실행한다. 새 동작의 테스트는 `tests/`에 두고, 문서·설정 변경은 해당 검사와 공통 verify를 사용한다.

```bash
uv run --locked python scripts/verify.py
```

로컬 공통 검사가 PASS여야 한다. GitHub Actions가 실패하면 해당 단계 로그를 열어 설치와 검사 실패를 구분한다. 원격 CI 실행은 별도 증거다. 고객사 자료가 필요한 결과는 승인된 비식별 근거와 계약이 확보된 뒤 별도 인수 조건으로 검증한다.

## 12. 개발 완료 기준

- [ ] 최소 권한·고정 Action SHA·시간 제한을 유지했다.
- [ ] 원격 미실행과 로컬 PASS를 구분하고 README 변경을 PR에 기록했다.
- [ ] 변경된 작업 안내·명령·상대 링크를 같은 변경에서 최신화하고 공통 완료 기준에 기록했다.

## 13. 현재 제약 및 주의 사항

최초 commit·push·merge·외부 Issue 등록은 승인 범위를 따른다. GitHub Free Private 보호 제한이 적용될 수 있으며 Sonar는 기본 비활성이다. 팀 판단이 필요한 차이는 사용자에게 근거와 영향을 공유하고 Issue 등록을 제안한다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [Engineering Handbook](../docs/guides/README.md) · [데이터 확인 Issue 초안](../docs/issue-drafts/research-data-contract.md) · [초기화 Spec](../docs/specs/0001-bootstrap.md) · [팀 운영 Issue 초안](../docs/issue-drafts/task-team-settings.md) · [Sonar Issue 초안](../docs/issue-drafts/task-sonar-approval.md) · [협업 설정](../docs/guides/github-guide.md) · [GitHub Actions 공식 문서](https://docs.github.com/en/actions)
