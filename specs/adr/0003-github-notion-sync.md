# ADR-003: GitHub Issues·Projects → Notion 단방향 동기화

- 상태: 제안(사람 리뷰 대기). 구 번호 `docs/adr/0007`에서 옮겼다
- 날짜/담당/승인자: 2026-11-25 / 담당 미정 / 승인 대기
- 확인된 사실/출처: [Spec](../features/github-notion-sync.md) CONFIRMED 근거. Notion [versioning](https://developers.notion.com/reference/versioning), [request limits](https://developers.notion.com/reference/request-limits), [2025-09-03 upgrade guide](https://developers.notion.com/docs/upgrade-guide-2025-09-03). GitHub [create-github-app-token](https://github.com/actions/create-github-app-token) v3.3.0 `action.yml`.

## 결정

| 항목 | 결정 | 판단 근거 |
|---|---|---|
| 실행 구조 | GitHub Actions + Python 표준 라이브러리 스크립트 | 서버 없이 동작한다. 의존성을 추가하지 않는다. Mock 테스트를 할 수 있다. |
| 책임 분리 | workflow = 이벤트·권한·주입·실행, Python = API·매핑·upsert·오류 처리 | 로직을 테스트 가능한 코드로 둔다. |
| 코드 위치 | `scripts/collaboration/` | HR 런타임 `src/hr_onboarding`와 분리한다. |
| GitHub 인증 | Organization 소유 GitHub App 하나(Issues read, Organization Projects read) | 기본 `GITHUB_TOKEN`은 Organization Project를 읽을 수 없다. 개인 계정에 묶이지 않고, 작업별 단기 토큰을 쓴다. |
| Project API | GraphQL | Issue 하나의 `projectItems`와 필드 값을 한 번에 조회할 수 있다. REST Projects API는 비교 검증 전이라 쓰지 않는다. |
| Notion API | `Notion-Version: 2026-03-11`, Data Source ID 사용 | 최신 버전을 명시적으로 고정한다. |
| 식별 | `Sync Key` = `owner/repo#<Issue 숫자 ID>` | Repository 이동이나 번호 재사용과 무관하게 페이지를 식별한다. |
| 변경 감지 | 속성 SHA-256은 `Sync Hash`, 본문 블록 SHA-256은 `Body Hash`에 저장 | 같으면 API를 호출하지 않는다. 속성만 바뀌면 본문 블록을 다시 쓰지 않아 일괄 변경 때 요청 수가 폭증하지 않는다. |
| 본문 | 생성 시 페이지 맨 앞에 만든 토글 하나만 동기화하고 내용은 빈 줄 기준 문단으로 쓴다 | Markdown 해석·링크 생성을 하지 않는다. 사람이 쓴 블록은 토글 밖에서 보존된다. |
| Project Status 유형 | Notion **Select** | API로 비울 수 있고 옵션을 미리 만들 필요가 없다. 보드 그룹화가 가능하다. 허용 옵션은 코드에서 검증한다. |
| Secret 보관 | main 브랜치 전용 Environment `notion-sync` | job `if:`는 같은 파일을 고치면 우회되므로 브랜치 제한을 GitHub 설정으로 둔다. |
| 실행 환경 | `uv run --no-project`(의존성 미설치) | 표준 라이브러리만 쓴다. Secret이 있는 프로세스에 HR 런타임 의존성을 올리지 않는다. |
| 동시성 | concurrency group 하나, `cancel-in-progress: false` | 실행 중 쓰기를 중단하지 않는다. 대기 실행이 교체돼도 예약 실행이 복구한다. |

## Notion 속성 매핑

필수 9개가 없으면 쓰기 전에 멈춘다. 선택 속성은 DB에 있을 때만 쓴다. 선택 속성을 추가하면 보낼 속성이 바뀌어 해시가 달라지므로, 다음 실행에서 기존 페이지도 채워진다.

| 구분 | Notion 속성 | 유형 | 출처 |
|---|---|---|---|
| 필수 | (이름 무관) | title | Issue 제목 |
| 필수(내부) | Sync Key / Sync Hash / Body Hash / Repository | rich_text | 식별·변경 감지·전체 조회 필터 |
| 필수 | GitHub URL / Issue State / Project Status / Assignees | url / select / select / rich_text | Issue·Project |
| 선택 | Issue Number / Labels / Milestone / Close Reason / Created At / Updated At | number / multi_select / rich_text / select / date / date | Issue |
| 선택 | Size / Estimate / Start Date / Target Date / Track / Feature ID | select / number / date / date / select / rich_text | Project |
| 선택 | Priority / Issue Type / Parent Issue / Sub-issues Progress / Blocked By | select / select / rich_text / rich_text / rich_text | Issue(GraphQL `issueFieldValues`·`issueType`·`parent`·`subIssuesSummary`·`blockedBy`). F-059에서 Priority 원본을 Project field에서 Organization Issue Field로 바꿨다 |
| 선택(진단) | Project Sync State / Issue Meta Sync State / Synced At | select / select / date | 동기화 메타데이터 |
| 사람 소유 | Notes 등 그 밖의 속성 | 자유 | 동기화하지 않음 |

Issue ID 속성은 Sync Key와 중복되어 두지 않는다.

## 가정/단점/위험/재검토 조건

- 원래 명세의 Project Status 유형(Status)과 다르다. 팀이 Status 유형을 원하면 옵션 사전 생성과 비우기 불가 제약을 감수하고 재검토한다.
- 본문 갱신은 토글 하위 블록을 하나씩 삭제하므로 긴 본문은 API 호출이 많다(최대 91개).
- 사람이 토글 제목을 바꾸거나 지우면 다음 본문 변경 때 페이지 끝에 새 토글이 추가된다. 이전 토글은 수동으로 지운다.
- 페이지 생성 응답이 유실되고 재조회에도 보이지 않으면 `failed`로 남긴다. 다음 실행에서 조회 반영이 늦어지면 드물게 중복이 생길 수 있고, 이때는 `conflict`로 보고되어 사람이 정리한다.
- `issues.deleted`·`issues.transferred`는 처리하지 않는다. 전체 동기화에서 orphan으로만 보고한다.
- Status 옵션이 추가되면 `KNOWN_STATUSES`를 갱신할 때까지 `unmapped`로 보고하고 종료 코드 1을 남긴다.

## 검증/관련 Spec/Issue

`tests/collaboration/` Mock 테스트. 실제 연동은 NOT RUN. [Spec](../features/github-notion-sync.md).
