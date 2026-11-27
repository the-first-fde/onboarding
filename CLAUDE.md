# Claude Code 개발 안내
@AGENTS.md
@specs/constitution.md

## 역할
- Claude: 요구사항 분석, 기획, 명세(Feature)·설계(Plan·ADR·계약), 리뷰, 검증, 커밋·PR 생성
- Codex(`AGENTS.md`의 "Codex 구현 규칙"): 구현과 테스트 코드 작성. 기본 `gpt-6.1-terra` medium, 전환 조건 발생 시 `gpt-6.1-sol` medium
- 사람: GitHub PR 리뷰와 머지. 개발 루프 안에서는 아래 "사람 개입 지점"에서만 멈춘다

Claude는 `apps/`·`tests/`·`migrations/`·`workflows/`·`mcp_servers/`의 코드를 직접 작성하거나 고치지 않는다. 사소한 수정도 Codex에 넘긴다.
Claude가 직접 수정하는 범위는 `specs/`, `docs/`, `policies/`, `knowledge/`(raw 제외), `CLAUDE.md`, `AGENTS.md`, `.claude/`다.

## 작업 단위
구현은 1 기능 = 1 명세 = 1 채팅 = 1 계획 = 1 커밋으로 진행한다. 브랜치와 PR도 기능마다 하나다.

| 단위 | 대응 |
|---|---|
| 기능 | `F-NNN` 하나 |
| 명세 | `specs/features/F-NNN.md` |
| 채팅 | Claude 세션 하나. 새 기능은 새 세션에서 시작한다. Codex는 같은 기능 안에서 `resume --last`로 한 세션을 이어 쓴다 |
| 계획 | `specs/plans/F-NNN.md` |
| 커밋 | PR을 만들 때 기능 브랜치의 커밋은 하나다. 리뷰·CI 수정 커밋은 PR에 추가하고 squash merge로 `main`에는 커밋 하나만 남긴다 |
| 브랜치·PR | `feat/F-NNN-<slug>` 하나, PR 하나 |

- 대화 중에 다른 기능 요청이나 범위 밖 변경이 나오면 현재 기능에 섞지 않는다. 새 Feature 초안이나 Open Questions로 남기고 새 세션에서 진행한다
- 한 기능이 너무 커서 커밋 하나로 리뷰하기 어려우면 구현 전에 Feature를 나눈다
- 지침·설정 변경(`chore/`)과 문서 변경(`docs/`)도 같은 원칙을 따른다

## 기능 개발 순서
1. Branch: 최신 `main`에서 `feat/F-NNN-<slug>`를 만든다. 지침·설정은 `chore/<slug>`, 문서만은 `docs/<slug>`
2. Analysis: PRD·constitution·관련 계약·`docs/source-register.md` 근거를 확인한다. 근거 없는 업무 규칙은 Feature의 Open Questions에 남긴다
3. Spec: `specs/features/F-NNN.md`에 목적·EARS 완료 조건·건드리지 말 것·선행 조건을 쓴다
4. Plan: `specs/plans/TEMPLATE.md`를 복사해 `specs/plans/F-NNN.md`를 쓴다. 시그니처·책임·Scope 파일·AC별 테스트 케이스만 적고 구현 코드는 쓰지 않는다. 아키텍처 변경·의존성 추가는 같은 브랜치에 ADR(Proposed)을 함께 쓴다
5. Handoff: Plan 상태를 `Ready`로 바꾸고 묻지 않고 Codex를 실행한다
6. Review: Plan의 Implementation Log와 `git diff main...HEAD`를 읽고, AC 충족·Scope 준수·constitution 위반(allowlist, 합격≠입사확정, 결정론, 격리)을 검토한다. 필요 시 `ecc:python-reviewer`·`ecc:security-reviewer`를 쓴다
7. Fix loop: 지적 사항은 `codex exec resume --last`로 전달한다. 최대 3회 왕복 후에도 남으면 PR 본문 "남은 문제"에 적는다
8. Verify: 직접 검증 명령을 실행하고 결과를 `docs/verification.md`에 PASS/FAIL/NOT RUN으로 기록한다
9. Ship: 커밋 1개 → `git push -u origin <branch>` → `gh pr create`. 본문은 `.github/pull_request_template.md` 형식으로 쓰고 Open Questions·가정·NOT RUN 항목을 숨기지 않는다

이 프로젝트에서는 위 9단계의 커밋·push·PR 생성을 사용자 확인 없이 수행한다(전역 지침의 "요청 시에만 커밋/push"를 이 저장소에 한해 대체한다). 머지는 하지 않는다.

## Codex 핸드오프
- 실행: `codex exec -m gpt-6.1-terra -c model_reasoning_effort=medium -s workspace-write --add-dir ~/.cache/uv -C <repo> "<프롬프트>" < /dev/null`
  - `--add-dir ~/.cache/uv`: 샌드박스가 uv 캐시 쓰기를 막아 `uv run`이 실패하는 것을 피한다
  - `< /dev/null`: 백그라운드 실행 시 stdin 대기("Reading additional input from stdin...")로 멈추는 것을 피한다
- 프롬프트: "`AGENTS.md`를 따르고 `specs/plans/F-NNN.md`와 연결된 Feature만 기준으로 구현하라"만 쓴다. 명세 내용을 복사하지 않는다
- 실행 전 현재 브랜치가 Plan의 Branch와 같은지 확인한다
- 재개: `codex exec resume --last -m <모델> -c model_reasoning_effort=medium -c sandbox_mode="workspace-write" -c 'sandbox_workspace_write.writable_roots=["<uv 캐시 절대 경로>"]' "<지적 사항>" < /dev/null`
  - `resume`은 `-s`·`--add-dir`·`-C`를 받지 않으므로 저장소 디렉터리에서 실행한다
- Log에 전환 조건이 기록되면 `-m gpt-6.1-sol`로 같은 Plan을 다시 실행하고 전환 시점·사유를 Log에 남긴다
- Codex가 Log에 질문을 남기고 멈추면, 명세로 답할 수 있는 것은 Claude가 Plan을 보강해 재개하고, 회사 규칙 판단이 필요한 것만 사람 개입 지점으로 올린다

## 사람 개입 지점
아래에 해당할 때만 멈추고 사용자에게 묻는다. 그 외에는 판단 근거를 Plan·PR에 남기고 진행한다.
- 실제 HR 원본·`.env`·비밀키·실제 외부 시스템(ATS/Notion/메일/Slack 등)에 접근하거나 전송해야 할 때
- 업무 규칙 근거가 없어 결과 동작이 갈리는 결정(추정으로 구현하지 않는다)
- `main` 직접 변경, force push, 머지, 브랜치·태그 삭제, 원격 저장소 설정 변경
- 현재 Feature 범위를 벗어나는 변경이나 constitution 자체의 변경
- 권한 거부·sandbox 차단을 우회해야만 진행 가능한 경우(우회하지 않고 필요한 규칙 문자열을 안내한다)

## 제품 런타임 경계
개발용 Claude Code와 제품 내부 Claude Agent SDK 런타임을 분리한다.
현재 SDK·MCP·RAG는 설계/경계만 있으며 실행 구현을 가장하지 않는다.
SDK를 연결할 때는 single agent + domain skills, 구조화 출력, 도구 allowlist,
PreToolUse 권한 검사, PostToolUse 결과 검증, 서버 승인 게이트 및 비용 한도를 함께 구현한다.
현재 mock 모드 외 실행은 금지되어 있다. Hook만으로 권한을 보장할 수 없다.

## Hook·권한
- ECC hook 중 알림·제안성 hook은 `.claude/settings.json`의 `ECC_DISABLED_HOOKS`로 끈다. 차단성 안전 hook(`pre:bash:block-no-verify`, `pre:bash:commit-quality`, `pre:config-protection`)은 유지한다
- hook이 차단하면 우회(`--no-verify`, 설정 완화)하지 않고 원인을 고친다. 반복적으로 개발을 막는 hook은 끌 ID와 사유를 사용자에게 제안한다

## 검증 명령
- `uv run pytest`
- `npm run build` (`apps/frontend`)
