# 개발 하네스에서 Skills와 Hooks 사용하기

**학습 목표**는 에이전트가 일을 반복할 수 있도록 돕는 장치와 사람이 직접 판단할 경계를 확인하는 것이다. Harness Engineering은 맥락, 도구, 권한, 검사, 피드백을 한 작업 환경으로 설계하는 일이다. 같은 검증을 쉽게 재현하고 실수의 범위를 줄이기 위해 사용한다.

| 요소 | The First에서 하는 일 |
|---|---|
| 개발 하네스 | [.claude](../../.claude/README.md), 프로젝트 지침, 검증으로 팀의 개발 작업을 지원 |
| 런타임 하네스 | [업무 Markdown](../../agents/README.md), 그래프와 SDK, 외부 도구 경계로 제품 실행을 구성 |
| ECC | 선별한 upstream Skills 및 개발용 역할. [SHA·MIT·수정 기록](../../third_party/ecc/SOURCE.md)에서 출처 확인 |
| Skills / Subagents | Skill은 반복 절차, 읽기 전용 개발 subagent는 계획·리뷰 역할. 검증 실행 결과는 주 세션에서 제공 |
| Hooks / Permissions | hook은 도구 전후 점검, permission은 허용·질문·차단 기준 |

## 실습 · main 편집 요청의 판단 읽기

[bootstrap](getting-started.md)으로 준비된 `.venv/bin/python`이 hook에 필요하다. 실패 시 차단하는 `onFailure=block`을 적용하려면 Claude Code 2.1.295 이상이 필요하다. [settings.json](../../.claude/settings.json)에서 PreToolUse→protect_files 및 PostToolUse→after_edit 연결을 찾아본다. 첫 hook은 민감 경로, main 편집과 MCP 요청 등에서 판단하고, 둘째 hook은 대상 Python 편집 뒤 Ruff를 실행한다.

```bash
uv run --locked pytest -q tests/test_hooks.py
uv run --locked python scripts/doctor.py
```

루트에서 가상 요청으로 동작을 확인한다. `-q`는 결과를 간단히 출력하며 doctor는 pre-commit/pre-push 설치와 별도 hooksPath를 진단한다. 두 Git hook은 공통 verify를 호출하고 복제만으로 설치되지 않는다. 실패하면 traceback과 설정의 경로를 읽고 `.venv` 경로와 hook 입력을 확인한다. 실제 비밀 파일을 열어 시험할 필요가 없다.

**Claude Code 연습** — “작업 안내와 설정을 읽고 가상 main 편집이 왜 차단되는지 설명해줘. /plan-task로 권한 변경 없이 확인할 테스트를 먼저 보여줘.” 사람은 실행 전 도구 범위를 확인한 뒤 diff와 단위 테스트 결과를 대조한다. 개발 시 /implement-task, 별도 리뷰에는 /review-changes, 초안에는 /prepare-pr를 사용한다. 개인 설정과 팀 정책이 충돌하면 근거를 보고하고 Issue 초안을 제안한다.

좋은 검증은 가상 payload와 현재 설정을 확인한다. 피할 검증은 실제 .env 열기, 무제한 도구 허용, 보호를 우회해 성공으로 표시하는 방식이다. 실제 세션의 `/hooks`·`/permissions`와 단위 테스트는 서로 다른 증거다. 직접 셸이나 개인 설정은 hook 이외의 경로가 될 수 있다. ECC 전체 설치, 자동 갱신·지속 학습, 자동 Git 변경은 팀 범위에 없다.

- [ ] 개발 subagent와 업무 런타임의 권한 차이를 설명한다.
- [ ] 가상 hook 실패를 찾아 설정·경로·개인 설정 중 무엇을 확인할지 말한다.

[Claude Code Hooks](https://code.claude.com/docs/en/hooks) · [권한](https://code.claude.com/docs/en/permissions)
