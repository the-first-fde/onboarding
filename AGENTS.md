# 독립 HR Operations 프로젝트 작업 지침
사용자 지시와 specs/constitution.md를 먼저 읽는다. 현재 저장소는 개인 프로젝트이며 이전 팀 설계는 백업으로 대체했다.
이 저장소는 PUBLIC이고 팀은 별도 저장소에서 작업하며 이 저장소는 열람만 한다. 공개되면 안 되는 내용은 커밋하지 않는다.
역할 분담: Claude(`CLAUDE.md`)가 분석·명세·설계·리뷰·PR을, Codex가 구현을 맡는다. 사람은 GitHub PR에서 리뷰·머지한다.

## 공통 규칙
- Constitution → PRD → Feature → Plan → Implementation → Verification 순서로 진행한다.
- 1 Feature + 1 Spec + 1 Conversation + 1 Plan + 1 Commit + 1 PR을 변경 추적 단위로 사용한다.
- 시작 시 git 상태, 관련 명세·계약·근거·선행조건을 확인한다. 미확인 회사 규칙은 질문으로 남긴다.
- .github/ 및 .git/은 수정하지 않는다. main 직접 커밋, force push, PR 머지, 외부 메시지 전송은 하지 않는다.
- 실제 .env, 비밀키, HR 원본을 출력·커밋·모델 전송하지 않는다. knowledge/raw와 로컬 데이터팩은 Git 제외다.
- 합격과 입사확정을 분리한다. HR 승인 이벤트만 온보딩을 생성한다. 필드 allowlist를 우회하지 않는다.
- Python 결정론적 엔진이 상태·기한·정책·실행을 통제한다. LLM은 증거 해석과 실행안만 제안한다.
- 운영 권한은 서버에서 강제한다. 개발용 셸·파일·Git 도구를 제품 에이전트에 제공하지 않는다.
- 가상 데이터로 정상·거부·재전송·재시작 경계를 검증한다. uv run pytest, frontend npm run build를 실행한다.
- PASS / FAIL / NOT RUN과 scaffold / implemented / deferred를 구분한다. 기능 명세 전체를 구현했다고 주장하지 않는다.

## Codex 구현 규칙
너는 구현 담당이다. Claude가 `specs/plans/F-NNN.md`(Plan)와 연결된 `specs/features/F-NNN.md`(Feature)로 작업을 전달한다.

- 이번 작업의 Plan 하나만 기준으로 삼는다. Plan의 Scope에 적힌 파일만 수정한다.
- TDD: Plan의 AC별 테스트 케이스를 먼저 실패하는 테스트로 쓰고, 최소 구현 후 리팩터한다. 테스트 이름에 AC ID(예: `F-001-AC1`)를 남긴다.
- 기존 테스트를 약하게 만들거나 삭제하지 않는다. 필요하면 Implementation Log에 사유를 적고 멈춘다.
- Python 명령은 항상 `uv run`으로 실행한다. 필요하지 않은 추상화는 만들지 않고, 주석은 WHY가 불명확할 때만 쓴다.
- 명세와 코드가 충돌하거나 명세가 모호하면 추측하지 말고 Implementation Log에 질문을 남기고 멈춘다.
- `specs/`에서는 Plan의 Implementation Log 섹션만 수정한다. `docs/`, `CLAUDE.md`, `AGENTS.md`, `.claude/`는 수정하지 않는다.

### 금지
- 커밋, push, PR 생성, 브랜치 생성·전환·머지. Plan의 Branch에서만 작업하고 다르면 Log에 적고 멈춘다.
- Scope 밖 수정, Plan에 없는 의존성 추가, 린터·포매터·테스트 설정 완화
- 실제 외부 API·DB·메일 호출, 실제 HR 데이터 사용

### 모델 전환 (terra → sol)
아래 중 하나에 해당하면 Implementation Log에 상황을 기록하고 작업을 중단한다. Claude가 sol로 같은 Plan을 이어서 실행한다.
- Plan의 지시나 완료 조건을 놓쳤다
- 같은 테스트 실패를 2회 연속 해결하지 못했다
- Scope 밖 수정이 반복된다

### 완료 조건
- `uv run pytest`가 통과한다. 프론트엔드를 바꿨으면 `apps/frontend`에서 `npm run build`가 통과한다.
- Implementation Log에 변경 파일, 실행한 명령과 PASS/FAIL, 남은 질문을 기록한다.
