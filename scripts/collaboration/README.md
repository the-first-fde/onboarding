# 협업 자동화: GitHub → Notion 동기화

[프로젝트 시작 안내](../../README.md) · [작업 지침](../../AGENTS.md) · [운영 가이드](../../docs/collaboration-integration-guide.md)

## 1. 이 디렉터리의 목적

GitHub Issue와 GitHub Project "HR AX"의 진행 상태를 Notion 데이터베이스에 한 방향으로 복사한다. 팀 협업용 도구이며 HR 에이전트 런타임(`src/hr_onboarding`)이나 고객사 데이터와 무관하다.

## 2. 무엇을 개발해야 하는가?

구현은 끝났다. 유지보수 대상은 Project 필드·옵션 변경 반영, Notion 속성 변경 반영, API 버전 갱신이다. 새 기능은 [Spec](../../specs/features/github-notion-sync.md) 범위를 먼저 고친 뒤 추가한다.

## 3. 담당자별 개발 업무

| 담당 | 업무와 개발 대상 | 예상 산출물 | Spec |
|---|---|---|---|
| 공통 담당 미정 | 동기화 스크립트·workflow 유지 | 필드 매핑 갱신, 테스트 | [동기화 Spec](../../specs/features/github-notion-sync.md) |

## 4. 개발에 필요한 기초 개념

- **단방향 동기화**: GitHub 값을 Notion에 덮어쓴다. Notion에서 바꾼 GitHub 소유 속성은 다음 변경 때 GitHub 값으로 돌아간다.
- **upsert**: 페이지가 없으면 만들고 있으면 갱신한다. `Sync Key`로 같은 Issue의 페이지를 찾는다.
- **멱등성**: 여러 번 실행해도 결과가 같다. `Sync Hash`가 같으면 아무것도 쓰지 않는다.
- **dry-run**: 읽기만 하고 무엇을 만들거나 바꿀지 보고한다.

## 5. 파일 및 모듈별 역할

| 파일 | 역할 |
|---|---|
| [http_api.py](http_api.py) | HTTPS JSON 요청, 429/5xx 재시도, 오류 분류(`AuthError`, `ApiError`, `UncertainWriteError`) |
| [github_client.py](github_client.py) | Issue REST 조회, Project GraphQL 조회, 필드 매핑 표 `PROJECT_FIELD_MAP`, 허용 Status `KNOWN_STATUSES` |
| [notion_client.py](notion_client.py) | Data Source 스키마·페이지·블록 API, `NOTION_VERSION` |
| [notion_sync.py](notion_sync.py) | Notion 속성 매핑(`REQUIRED_PROPERTIES` 필수, `OPTIONAL_PROPERTIES` 있을 때만), 본문 변환, upsert, 설정 검증, CLI |
| [../../.github/workflows/notion-sync.yml](../../.github/workflows/notion-sync.yml) | 언제 실행할지, 어떤 권한과 인증을 줄지 |

## 6. 입력 및 출력 데이터

입력은 환경 변수와 `--issue N` 또는 `--all`, 선택 `--dry-run`이다. 출력은 Notion 페이지와 Job Summary(Issue 번호·결과 코드만)다. 종료 코드는 0(성공), 1(일부 실패·충돌·Project 조회 문제), 2(설정 오류)다.

## 7. 다른 모듈과의 관계

HR 런타임 코드와 import 관계가 없다. 공통 검증(`scripts/verify.py`)이 이 코드를 Ruff·Pyright·pytest·Gitleaks 대상으로 포함한다. 기본 coverage 지표는 HR 런타임 기준이며 이 코드는 포함하지 않는다. Sonar는 `sonar.sources`로 정적 분석하고 `sonar.coverage.exclusions`로 coverage에서 뺀다.

## 8. 단계별 개발 방법

1. [Spec](../../specs/features/github-notion-sync.md)과 [ADR-003](../../specs/adr/0003-github-notion-sync.md)에서 바꿀 매핑이나 동작을 확인한다.
2. `tests/collaboration/`에 실패하는 테스트를 먼저 추가한다.
3. 위 표의 해당 파일만 고친다. 예: Project에 Status 옵션 추가 → `KNOWN_STATUSES`. Notion 속성 추가 → 보통 `OPTIONAL_PROPERTIES`와 `build_properties`.
4. 아래 검증을 실행하고, 실제 Notion에서 dry-run으로 확인한다.

## 9. 최소 구현 예제

Notion에 쓰지 않는 dry-run 결과 확인 예다. 네트워크 없이 실행된다.

```bash
PYTHONPATH=scripts uv run --locked python -c 'from collaboration.notion_sync import SyncReport; print(SyncReport(dry_run=True).to_markdown())'
```

`## Notion sync: dry-run (no Notion writes)`와 결과 개수 줄이 출력된다.

## 10. Claude Code 활용 예제

- **계획** “/plan-task로 Project에 `Blocked` Status를 추가할 때 바꿀 파일과 첫 테스트를 제시해줘.”
- **코드 설명** “notion_sync.sync_issue가 중복 생성을 막는 방법을 테스트 근거로 설명해줘.”
- **구현과 테스트** “/implement-task로 승인된 매핑 변경만 진행하고 tests/collaboration 결과를 보여줘.”
- **영향 검토** “/security-review로 workflow 권한과 Secret 주입 위치를 검토해줘.”

## 11. 테스트 및 검증 방법

저장소 루트에서 실행한다. 실제 인증 정보는 필요 없다.

```bash
uv run --locked pytest tests/collaboration -q
uv run --locked pytest tests/collaboration -q --cov=collaboration --cov-report=term-missing
uv run --locked python scripts/verify.py
```

두 번째 명령은 이 코드의 coverage를 따로 보여준다. 공통 verify의 coverage에는 포함되지 않는다.

모든 테스트가 PASS여야 한다. 실패하면 첫 실패 테스트 이름으로 시나리오를 찾는다. 실제 API 연동은 [운영 가이드](../../docs/collaboration-integration-guide.md) 14절에서 따로 검증한다.

## 12. 개발 완료 기준

- [ ] 매핑 변경이 Spec·ADR 표와 일치한다.
- [ ] Mock 테스트와 공통 verify가 PASS다.
- [ ] 실제 연동 검증 여부를 PASS/NOT RUN으로 구분해 PR에 적었다.

## 13. 현재 제약 및 주의 사항

Notion→GitHub 쓰기와 Issue 삭제·이동 처리는 없다. 본문 토글 밖의 블록과 `Notes` 등 매핑 밖 속성은 건드리지 않는다. 실제 토큰은 셸 이력·로그에 남기지 말고 GitHub Secrets에만 둔다.

## 14. 관련 문서

[작업 경로의 Claude 지침](CLAUDE.md) · [운영 가이드](../../docs/collaboration-integration-guide.md) · [Spec](../../specs/features/github-notion-sync.md) · [ADR-003](../../specs/adr/0003-github-notion-sync.md) · [Notion API](https://developers.notion.com/reference/intro) · [GitHub Projects API](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
