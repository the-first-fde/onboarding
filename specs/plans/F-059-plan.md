# F-059 Plan · Notion Sync Issue Field·계층 필드
상태: Implemented

## Metadata
- Feature ID: F-059
- GitHub Issue: #90
- Feature Spec: ../features/F-059-notion-sync-issue-fields.md
- Branch: fix/F-059-notion-sync-issue-fields

## Goal
Notion Priority가 Organization Issue Field 값으로 채워지고, Issue Type·Feature ID·Track·Parent·Sub-issues·Blocked By가 Notion에 보인다. 조회 실패 시 기존 값이 보존된다.

## Scope
Codex가 수정할 수 있는 파일. 이 목록 밖은 수정하지 않는다(문서는 Claude가 갱신한다).
- scripts/collaboration/github_client.py
- scripts/collaboration/notion_sync.py
- tests/collaboration/fakes.py
- tests/collaboration/test_github_client.py
- tests/collaboration/test_notion_sync.py

## Design
### github_client.py
| 대상 | 시그니처 | 책임 |
|---|---|---|
| `PROJECT_FIELD_MAP` | 상수 | `Priority` 제거. `Track`(`SINGLE_SELECT`, `track`), `Feature ID`(`TEXT`, `feature_id`) 추가 |
| `_FIELD_VALUE_FRAGMENT` | 상수 | `ProjectV2ItemFieldTextValue { text field { name } }` 추가 |
| `ProjectFields` | frozen dataclass | `priority` 제거, `track: str \| None`, `feature_id: str \| None` 추가 |
| `parse_field_values` | `(nodes) -> ProjectResult` | text value도 처리 |
| `KNOWN_PRIORITIES` | `frozenset({"P0","P1","P2"})` | Priority 허용 값 |
| `ISSUE_FIELD_PRIORITY` | `"Priority"` | Organization Issue Field 이름 |
| `IssueMetaLookup` | StrEnum `OK`, `ERROR` | 메타데이터 조회 결과 종류 |
| `IssueMeta` | frozen dataclass | `issue_type`, `priority`, `priority_known: bool`, `parent: int \| None`, `sub_issues_total: int`, `sub_issues_completed: int`, `blocked_by: tuple[int, ...]` |
| `IssueMetaResult` | frozen dataclass | `lookup`, `meta`. `META_ERROR` 상수 제공 |
| `ISSUE_META_FRAGMENT` | GraphQL fragment | `id`, `issueType{name}`, `parent{number}`, `subIssuesSummary{total completed}`, `blockedBy(first: 50){totalCount nodes{number}}`, `issueFieldValues(first: 20){nodes{__typename ... on IssueFieldSingleSelectValue{name field{... on IssueFieldSingleSelect{name}}}}}` |
| `parse_issue_meta` | `(node: dict) -> IssueMetaResult` | Priority 값이 `KNOWN_PRIORITIES` 밖이면 `priority=None, priority_known=False`. `blockedBy.totalCount`가 nodes 수보다 크면(잘림) ERROR. `blocked_by`는 정렬 |
| `GitHubClient.get_issue_meta` | `(issue: IssueSnapshot) -> IssueMetaResult` | `repository.issue(number)` 1회 조회. 모든 오류는 `META_ERROR` |
| `GitHubClient.load_issue_meta_index` | `() -> dict[str, IssueMetaResult] \| None` | `repository.issues(first: 100, after, states: [OPEN, CLOSED])` 페이지 조회, node ID별 결과. `MAX_PAGES` 상한. 실패하면 None |
| `_query` | 기존 | 메타데이터 조회는 `project_number` 없이도 동작해야 한다. Project 전용 검사는 Project 조회 경로에만 둔다 |

GraphQL 응답에 `errors`가 있으면(data가 함께 와도) 해당 조회 전체를 실패로 본다.

### notion_sync.py
| 대상 | 시그니처 | 책임 |
|---|---|---|
| `OPTIONAL_PROPERTIES` | 상수 | 추가: `Issue Type`(select), `Feature ID`(rich_text), `Track`(select), `Parent Issue`(rich_text), `Sub-issues Progress`(rich_text), `Blocked By`(rich_text), `Issue Meta Sync State`(select). `Priority`(select) 유지 |
| `build_properties` | `(issue, project, meta: IssueMetaResult) -> dict` | Project ERROR면 Project 속성(Status·Size·Estimate·Dates·Track·Feature ID)을 뺀다(기존 동작). meta ERROR면 Priority·Issue Type·Parent Issue·Sub-issues Progress·Blocked By를 뺀다. `priority_known=False`면 Priority만 뺀다. `Issue Meta Sync State`에 lookup 값 |
| 값 형식 | — | Parent `#26`, Sub-issues `완료/전체`(전체 0이면 빈 값), Blocked By `#43, #44`(빈 tuple이면 빈 값) |
| `IssueResult` | dataclass | `meta: IssueMetaLookup \| None` 추가 |
| `SyncReport.exit_code` / `to_markdown` | 기존 | meta ERROR도 exit 1, 요약에 `meta=` 표시 |
| `sync_issue` / `_safe_sync` | 기존 + `meta` 인자 | 메타데이터를 속성·해시에 포함 |
| `run_issue` | 기존 | 허용 작성자 확인 후 `get_issue_meta` 호출 |
| `run_all` | 기존 | `load_issue_meta_index` 1회. None이면 모든 Issue를 `META_ERROR`, 색인에 없으면 `META_ERROR` |

### fakes.py
- `FakeGitHub`에 `set_meta(number, lookup=OK, **fields)`, `get_issue_meta`, `load_issue_meta_index`(실패 모드 포함) 추가
- `FakeNotion` 스키마에 새 선택 속성을 넣고 빼는 방법 제공

## Steps
1. AC별 테스트를 먼저 작성하고 실패를 확인한다.
2. github_client: Project 필드 맵 변경, Issue 메타데이터 조회 추가.
3. notion_sync: 속성 매핑·보존 규칙·보고 변경.
4. 전체 테스트 실행.

## Security and Privacy
- 토큰 권한·범위는 바꾸지 않는다. Issue 제목·본문을 파싱하지 않는다.
- 공개 로그(Job Summary)에는 Issue 번호·결과 코드만 남긴다(기존 원칙).

## Test Plan
| AC | 케이스 | 입력(합성) | 기대 | 검증 방법 |
|---|---|---|---|---|
| F-059-AC-01 | P0/P1/P2 | issueFieldValues fixture | `Priority` select 값 | unit |
| F-059-AC-01 | Project Priority 무시 | Project에 Priority 값이 있는 fixture | 결과에 반영되지 않음 | unit |
| F-059-AC-02 | HTTP 오류, GraphQL `errors`, 부분 오류, 형태 오류, blockedBy 잘림 | fake transport | 메타 속성 없음, Issue Meta Sync State=error, exit 1 | unit |
| F-059-AC-02 | 전체 색인 실패 | load_issue_meta_index None | 모든 Issue 메타 속성 보존 | integration |
| F-059-AC-03 | `P3` 같은 범위 밖 값 | fixture | Priority만 빠짐 | unit |
| F-059-AC-04 | 미설정·parent 없음·sub-issue 0·blockedBy 0 | fixture | 빈 값 | unit |
| F-059-AC-05 | DB 스키마에 속성 있음/없음 | FakeNotion | 있으면 씀, 없으면 빠짐, 실패 없음 | unit |
| F-059-AC-06 | 2회 실행 | FakeNotion | 2회째 UNCHANGED, 페이지 1개 | integration |
| F-059-AC-07 | 새 속성 없는 기존 해시 페이지 | FakeNotion | UPDATED | integration |
| 회귀 | Track·Feature ID text value | Project fixture | 매핑됨 | unit |

## Failure and Recovery
- 메타데이터 조회 실패는 해당 속성만 보존하고 다음 실행(15분 주기)이 다시 맞춘다. 해시는 쓰기가 끝난 뒤 저장하는 기존 순서를 유지한다.

## Out of Scope
- `.github`, Notion DB 스키마, 문서 갱신(Claude 담당), Effort 필드

## Risks and Open Questions
- App 토큰 권한: dry-run에서 403이면 `.github` 권한 변경이 필요하다(별도 승인).
- `_check_schema`가 Project `Priority` 필드를 더 요구하지 않으므로, Project에 `Track`(SINGLE_SELECT)·`Feature ID`(TEXT)가 없으면 Project 조회가 ERROR가 된다(현재는 둘 다 있음).

## Approval
- 승인자: 저장소 소유자 / 2026-11-28 / 대화에서 원인 분석·구현 계획 승인 후 "EPIC-01 아래에 Task 이슈 만들고 진행" 지시. 실제 GitHub·Notion 동기화 실행은 별도 승인.

## Change Log
- 2026-11-28 (Codex 질문 답변): 기존 테스트 중 Project `Priority`를 원본으로 검증하는 부분(`test_issue_project_fields_are_parsed`, `test_scheduled_sync_reflects_project_only_changes`, `test_unknown_status_is_reported_and_existing_status_kept` 등)은 F-059 요구사항이 원본을 바꾸므로 수정 대상이다. 약화가 아니라 원본 교체로 본다. 규칙: Priority 단언은 Organization Issue Field(meta) 원본으로 옮기고, 같은 테스트의 다른 단언(Status·Size·Estimate·Dates·보존·보고)은 그대로 유지한다. Project 값 변경만으로 갱신되는 시나리오는 Priority 대신 Track 또는 Size로 검증한다. 테스트를 삭제하지 않는다. 변경한 테스트 이름과 이유를 Implementation Log에 남긴다.

## Implementation Log
Codex가 작성한다: 변경 파일, 실행 명령과 PASS/FAIL, 질문, 모델 전환 기록.

- 중단: 기존 테스트가 Project `Priority`를 읽고 Notion에 반영해야 한다고 검증하지만, F-059 AC-01과 Plan은 Project `Priority`를 무시하고 `ProjectFields.priority`를 제거하도록 요구한다. 예: `test_issue_project_fields_are_parsed`, `test_scheduled_sync_reflects_project_only_changes`, `test_unknown_status_is_reported_and_existing_status_kept`.
- 질문: 기존 테스트를 약화하거나 삭제하지 않는 규칙과 충돌하는 이 기존 Priority 검증을 F-059의 Organization Issue Field 검증으로 변경해도 되는가?
- 변경 파일: 이 Plan의 Implementation Log만 변경. 구현 및 테스트 수정 없음.
- 확인 명령: `git status --short --branch`, `cat specs/constitution.md`, `cat specs/plans/F-059-plan.md`, `cat specs/features/F-059-notion-sync-issue-fields.md`, 관련 코드·테스트 확인: PASS. `uv run pytest`: NOT RUN (명세와 기존 테스트 충돌로 구현 전 중단). 프론트엔드 빌드: NOT RUN (프론트엔드 변경 없음).

- 재개: Change Log의 답변에 따라 기존 Priority 검증의 원본을 교체했다. `test_issue_project_fields_are_parsed`는 Project Priority 대신 Track·Feature ID를 검증하고, `test_scheduled_sync_reflects_project_only_changes`는 Priority 대신 Track을 검증한다. `test_project_failure_preserves_existing_project_values`, `test_unknown_status_is_reported_and_existing_status_kept`의 Priority 입력은 Issue 메타데이터로 옮겼으며 나머지 단언은 유지했다. `test_project_error_omits_project_properties`는 독립적인 Issue 메타데이터 Priority를 Project 속성 목록에서 제외했다.
- 변경 파일: `scripts/collaboration/github_client.py`, `scripts/collaboration/notion_sync.py`, `tests/collaboration/fakes.py`, `tests/collaboration/test_github_client.py`, `tests/collaboration/test_notion_sync.py`, 이 Implementation Log.
- 검증: 구현 전 `uv run pytest tests/collaboration/test_github_client.py tests/collaboration/test_notion_sync.py -q` FAIL (신규 동작 미구현 확인); 구현 후 같은 명령 PASS (82개); 최종 `uv run pytest -q` PASS (128개, 기존 Starlette deprecation warning 1개); `git diff --check` PASS. 프론트엔드 빌드 NOT RUN (프론트엔드 변경 없음). 실제 외부 연동 NOT RUN (Plan에서 별도 승인 요구).
- 남은 질문: 구현 관련 없음. GitHub App 권한과 실제 Notion 속성은 Feature의 외부 조건으로 남음.

- 스타일 리뷰 반영: Scope 5개 파일의 줄 길이와 최상위 정의 간격을 정리하고, Issue 메타데이터 docstring·검증 helper·여러 줄 GraphQL 쿼리와 보존 규칙 설명을 추가했다. 동작 변경 없음.
- 검증: `uv run pytest -q` PASS (128개, Starlette deprecation warning 1개). Scope 파일별 100자 초과 줄 수: `github_client.py` 0, `notion_sync.py` 0, `fakes.py` 0, `test_github_client.py` 0, `test_notion_sync.py` 0. `git diff --check` PASS. `uv run ruff --version` NOT RUN (ruff 실행 파일이 설치되지 않음; 설정이나 의존성 변경 없음).
