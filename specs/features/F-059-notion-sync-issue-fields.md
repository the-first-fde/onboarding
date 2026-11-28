# F-059. Notion Sync: Organization Issue Field Priority와 계층 필드 동기화

## Metadata
- Feature ID: F-059
- GitHub Issue: #90 `[FEAT-059] Notion Sync: Organization Issue Field Priority와 계층 필드 동기화`
- Parent Epic: #22 `[EPIC-01] Project Foundation & SDD`
- Priority: P1
- Milestone: M0 · Project Foundation
- Track: DevOps

## Objective
GitHub → Notion 단방향 동기화(`scripts/collaboration`)가 Priority를 Organization Issue Field에서 읽어 Notion에 쓰고, Issue Type·Feature ID·Track·Parent Issue·Sub-issues Progress·Blocked By를 추가로 동기화한다.

## Why
Notion Priority가 항상 비어 있다. 동기화가 옵션이 없는 Project custom field `Priority`(값 0/74)를 읽고, 실제 SSOT인 Organization Issue Field `Priority`(값 75/75, 2026-11-28 조회)는 조회하지 않기 때문이다. Notion만 보는 사람이 우선순위·계층·선행 관계를 알 수 없다.

## Requirements
- THE SYSTEM SHALL Priority를 Organization Issue Field `Priority`에서만 읽고 Project custom field `Priority`는 읽지 않는다.
- THE SYSTEM SHALL Issue Type, Parent Issue, Sub-issues Progress, Blocked By를 GitHub GraphQL `Issue`에서, Track·Feature ID를 Project `HR AX` field에서 읽는다.
- THE SYSTEM SHALL 새 Notion 속성을 DB에 있을 때만 쓴다(선택 속성). DB에 없어도 동기화가 실패하지 않는다.
- THE SYSTEM SHALL 표준 라이브러리만 쓰고, 전체 동기화에서 Issue 메타데이터를 페이지(100건)당 GraphQL 1회로 조회한다.
- THE SYSTEM SHALL Issue 제목·본문에서 Feature ID 등 메타데이터를 추출하지 않는다(신뢰하지 않는 입력).

## Acceptance Criteria
- F-059-AC-01: WHEN Issue를 동기화하면 THE SYSTEM SHALL Organization Issue Field `Priority` 값(P0/P1/P2)을 Notion `Priority`(select)에 쓴다.
- F-059-AC-02: IF Issue 메타데이터 조회가 실패하거나(HTTP·GraphQL 오류, 부분 오류, 응답 형태 오류, 목록 잘림) THEN THE SYSTEM SHALL Priority·Issue Type·Parent Issue·Sub-issues Progress·Blocked By를 보내지 않아 기존 Notion 값을 보존하고, 실행 결과를 실패(exit 1)로 보고한다.
- F-059-AC-03: IF Priority 값이 P0/P1/P2가 아니면 THEN THE SYSTEM SHALL Notion `Priority`를 보내지 않고 나머지 메타데이터는 쓴다.
- F-059-AC-04: WHEN 값이 GitHub에 없으면(Priority 미설정, Parent 없음 등) THE SYSTEM SHALL 해당 Notion 속성을 빈 값으로 쓴다. 조회 실패와 구분한다.
- F-059-AC-05: WHERE Notion DB에 속성이 있으면 THE SYSTEM SHALL Issue Type·Feature ID·Track·Parent Issue·Sub-issues Progress·Blocked By를 동기화한다.
- F-059-AC-06: WHEN 같은 입력으로 다시 동기화하면 THE SYSTEM SHALL 페이지를 바꾸지 않고(UNCHANGED), 기존 페이지가 있으면 새 페이지를 만들지 않는다.
- F-059-AC-07: WHEN 변경 배포 후 전체 동기화를 실행하면 THE SYSTEM SHALL 새 속성 값이 비어 있던 기존 페이지를 갱신(backfill)한다.

## Do Not Touch
- `.github/` workflow와 GitHub App 권한, GitHub·Notion 설정과 Notion DB 스키마
- Project Status 이름과 `KNOWN_STATUSES`, Sync Key 형식, 본문 토글 동작
- HR 런타임(`apps/`)

## Out of Scope
- Notion → GitHub 역방향 동기화, Notion 속성 자동 생성
- Organization Issue Field `Effort` 등 다른 Issue Field
- Project custom field `Priority`를 관리 기준으로 쓰는 것

## Dependencies
- 선행 Feature: 없음. 기존 동기화(`specs/features/github-notion-sync.md`, ADR-003) 위에서 변경한다.
- 외부 조건: 실제 동기화 검증에는 GitHub App 토큰의 `issueFieldValues` 읽기 권한 확인(dry-run)과 Notion DB 속성 추가가 필요하다(사람 승인).

## Verification
| AC | 검증 방법 | 기대 결과 |
|---|---|---|
| F-059-AC-01 | unit(GraphQL 응답 fixture → Notion 속성) | P0/P1/P2가 `Priority` select로 나온다 |
| F-059-AC-02 | unit(오류·부분 오류·잘림 fixture) | 메타데이터 속성이 빠지고 exit 1 |
| F-059-AC-03 | unit | `Priority`만 빠진다 |
| F-059-AC-04 | unit | 빈 값으로 나온다 |
| F-059-AC-05 | unit(DB 스키마 유무 2가지) | 있으면 쓰고 없으면 빠진다 |
| F-059-AC-06 | integration(FakeNotion 2회 실행) | 2회째 UNCHANGED, 페이지 1개 |
| F-059-AC-07 | integration(새 속성 없는 기존 페이지) | UPDATED로 채워진다 |
| 실제 연동 | workflow_dispatch dry-run → 단일 Issue → 전체 | 사람 승인 후 실행, 결과 별도 기록 |

## Open Questions
- GitHub App 설치 토큰의 `Issue.issueFieldValues` 읽기에 "Issues: read" 외 권한이 필요한지 공식 문서에 명시가 없다. dry-run으로 확인한다.
- Notion DB의 현재 `Priority` 속성 이름·유형·옵션은 로컬에서 확인하지 못했다.

## References
- 기존 동기화 Spec: `specs/features/github-notion-sync.md`, `specs/adr/0003-github-notion-sync.md`, `docs/collaboration-integration-guide.md`
- GitHub Docs: [REST issue field values](https://docs.github.com/en/rest/issues/issue-field-values), [GraphQL Issues](https://docs.github.com/en/graphql/reference/issues)
