# Spec: (개발 도구) GitHub Issues·Projects → Notion 단방향 동기화

- 상태/담당/관련 Issue/ADR/계약: 구현 완료·실제 연동 NOT RUN / 담당 미정 / [ADR-003](../adr/0003-github-notion-sync.md) / HR 업무 계약과 무관
- 문제와 사용자 가치: 팀원이 Notion에서 개발 Issue와 Project 진행 상태를 확인한다. GitHub이 Single Source of Truth이고 Notion은 읽기용 대시보드다.
- CONFIRMED 근거(2026-11-25 조사):
  - Organization Project는 `the-first-fde` #1 "HR AX" 하나이며 private이다. 연결 Repository는 `the-first-fde/onboarding`이다.
  - Status 옵션은 `Backlog`, `Ready`, `In progress`, `In review`, `Done`이다. Priority는 단일 선택이지만 옵션이 없다. Size는 `XS`~`XL`, Estimate는 숫자, Start date·Target date는 날짜다.
  - Project 내장 workflow 7개가 켜져 있다(Auto-add to project, Item closed 등). 상세 필터와 전이 규칙은 API로 조회할 수 없어 UI 확인이 필요하다.
  - Notion API 최신 버전은 `2026-03-11`이다. Data Source ID와 Database ID는 서로 다르다. rich text는 2000자, 배열은 100개가 한도다. 429는 `Retry-After`를 따른다.
  - Repository는 PUBLIC이다(`gh repo view` 2026-11-25). Issue 0건, 우선순위 Label 없음, 중복 Issue 없음.
- PROVISIONAL 가정: 팀원 3명의 Issue만 동기화한다(허용 목록). 15분 주기가 팀 요구에 충분하다.
- 범위: Issue 생성·수정·담당자·Label·Milestone·Close/Reopen 반영, Project Status·Priority·Size·Estimate·Start/Target date 반영, 단일·전체·dry-run 수동 실행, 15분 예약 전체 동기화, 중복 방지, 재시도, 결과 요약.
- 제외 범위: Notion→GitHub 쓰기, 양방향 동기화, PR DB, 메신저·Notion Inbox 알림, Webhook 서버, HR 데이터, AI 요약·분류, Project 자동 추가(Project 내장 Auto-add 사용).

## 입력/출력 및 계약 상태

| 구분 | 내용 |
|---|---|
| 입력 | Issue 번호 또는 전체. GitHub REST Issue, GraphQL Project item·필드. 이벤트 payload의 제목·본문은 사용하지 않는다. |
| 출력 | Notion 페이지 upsert, GitHub Job Summary(번호·결과 코드만), 종료 코드 0/1/2 |
| 식별자 | `Sync Key` = `owner/repo#<Issue 숫자 ID>`. Issue 번호만으로 식별하지 않는다. |
| GitHub 소유 속성 | [ADR-003](../adr/0003-github-notion-sync.md) 매핑 표. 필수 9개(제목은 title 유형으로 인식), 나머지는 DB에 있을 때만 쓴다. 동기화가 덮어쓴다. |
| 사람 소유 영역 | `Notes` 등 매핑 표에 없는 속성, 본문 토글 밖의 모든 블록. 동기화가 쓰지 않는다. |

## 모듈 책임

| 위치 | 책임 |
|---|---|
| `.github/workflows/notion-sync.yml` | 이벤트, 실행 조건, 권한, App 토큰 발급, 환경 변수 주입, 스크립트 실행 |
| `scripts/collaboration/http_api.py` | `JsonApi.request(method, path, payload, idempotent)`: HTTPS 전용 전송, 429/5xx 재시도, 오류 분류 |
| `scripts/collaboration/github_client.py` | `get_issue`, `list_issues`, `get_project_result`, `load_project_index`: 읽기 전용 조회, PR·Draft 제외, Project 스키마 검사 |
| `scripts/collaboration/notion_client.py` | `get_property_types`, `find_pages`, `list_pages`, `create_page`, `update_page`, `list_children`, `delete_block`, `append_children` |
| `scripts/collaboration/notion_sync.py` | `build_properties`, `body_blocks`, `sync_issue`, `run_issue`, `run_all`, `load_settings`, `main`: 매핑·upsert·보고·CLI |

## 관찰 가능한 인수 조건

- 허용된 작성자의 새 Issue는 Notion 페이지 하나로 생성된다. 같은 Issue를 다시 동기화해도 페이지는 하나다.
- 변경이 없으면 Notion 쓰기 요청이 없다(`Sync Hash`·`Body Hash` 비교). 본문이 같으면 본문 블록을 다시 쓰지 않는다.
- 비교 대상은 GitHub 데이터의 해시다. Notion에서 사람이 바꾼 GitHub 소유 속성이나 지운 본문 토글은 GitHub에서 다음에 바뀔 때 복구된다.
- Issue·Project 필드 변경은 다음 이벤트·예약·수동 실행에서 반영된다.
- Close는 `Issue State=Closed`와 `Close Reason`만 바꾼다. Project Status를 Done으로 바꾸지 않는다. 불일치는 `state_mismatch`로 기록한다.
- Project 조회 실패 시 Project 속성을 보존하고 `Project Sync State=error`, 종료 코드 1을 남긴다. 알 수 없는 Status는 `unmapped`로 기록하고 기존 Project Status를 보존한다.
- `NOTION_SYNC_ENABLED`가 정확히 `true`이고 dry-run이 아닐 때만 쓴다. 허용 목록이 비면 쓰기 설정은 실패한다.
- 사람이 작성한 속성·블록은 본문 갱신 후에도 남는다.

## 정상/오류/권한/승인/중복/복구 시나리오

| 상황 | 동작 |
|---|---|
| 429/529 | `Retry-After`(최대 60초) 또는 backoff로 최대 4회 시도 |
| 읽기 5xx·네트워크 오류 | 지수 backoff 재시도 |
| 쓰기 5xx·네트워크 오류 | 반복하지 않음. 페이지 생성은 Sync Key로 재조회해 있으면 성공, 없으면 `failed`로 남기고 다시 만들지 않음(조회 반영 지연으로 인한 중복 방지). 다음 실행이 복구 |
| 3xx redirect | 따라가지 않고 실패(토큰이 다른 주소로 가는 것 방지). 다른 저장소로 이동한 Issue도 여기에 해당 |
| GitHub 한도 초과(`x-ratelimit-remaining: 0`) | 인증 실패와 구분해 `rate_limited`로 실패 |
| 응답 형태 이상 | traceback 대신 `unexpected_response`로 보고 |
| 401/403 | 즉시 실패, 실행 중단(fatal) |
| Notion 속성 누락·유형 불일치 | 쓰기 전에 fatal |
| 동일 Sync Key 페이지 2개 이상 | `conflict` 보고, 삭제하지 않음 |
| 일부 Issue 실패 | 해당 번호와 오류 코드를 기록, 나머지 계속, 종료 코드 1 |
| GitHub에 없는 Notion 페이지 | orphan으로 보고, 삭제하지 않음 |
| 이벤트 누락·대기 실행 교체 | 15분 예약 전체 동기화가 복구 |

## 테스트 계획과 미실행 이유

- `tests/collaboration/`: 요구사항 표의 시나리오를 transport fake와 in-memory fake로 검증한다. 네트워크는 기존 conftest가 차단한다.
- NOT RUN: 실제 Notion Integration·GitHub App·Actions 원격 실행. 인증 정보와 등록 승인이 없다. 실제 연동 테스트 절차는 [운영 가이드](../../docs/collaboration-integration-guide.md)에 있다.

## 보안/개인정보/외부 실행/비용

Public Repository이므로 외부 사용자도 Issue 이벤트를 만들 수 있다. 작성자 허용 목록(Project·Notion 조회 전에 검사), 기본 비활성, main 코드만 실행, Secret은 main 전용 Environment `notion-sync`에 보관, 프로젝트 의존성 미설치(`uv run --no-project`), redirect 차단, 제목·본문의 셸 미주입, 링크 미생성, 요약에 Issue 내용과 형식이 다른 Sync Key 미포함으로 대응한다. GitHub App은 Issues·Projects 읽기만 받는다. Notion Integration은 대상 DB에만 연결한다. 비용은 GitHub Actions 사용 시간(Public은 무료 범위)이다.

## 위험/차단/질문

- Priority 옵션 미정: 팀 결정 대기.
- Project 내장 workflow의 Status 전이(Item closed → Done 등)는 UI 확인 전 미확인이다.
- Public Repository의 예약 workflow는 60일간 활동이 없으면 GitHub이 비활성화한다.

## DoR/DoD와 사람 승인

보안·권한 변경이므로 사람 리뷰 2명을 권장한다. App 생성, Secret·Variable 등록, Notion DB 생성, 실제 활성화는 각각 사람이 명시 승인 후 수행한다.
