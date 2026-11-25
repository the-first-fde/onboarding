# 문제를 재현하고 안전하게 복구하기

**학습 목표**는 한 오류에서 증상, 원인 후보, 확인할 증거, 수정, 팀 결정을 구분하는 것이다. 복구 전에 [환경 준비](getting-started.md) 결과와 현재 변경 목록을 확인한다. 오류 메시지는 원인 후보이며 명령 위치와 첫 실패 조건을 함께 보면 근거가 된다.

## 기본 진단 순서

```bash
pwd
git status --short --branch
uv run --locked python --version
uv run --locked python scripts/doctor.py
```

루트에서 위치, 브랜치와 변경, 실제 Python 버전, 설치 상태를 차례로 읽는다. `--version`은 버전을, `--locked`는 lock 유지 여부를 확인한다. uv가 처음 환경을 준비하면 필요한 다운로드가 발생할 수 있다. 예상은 Python 3.12와 doctor PASS다. 앞 단계가 실패하면 다음 단계의 출력부터 해석하지 말고 원인을 먼저 좁힌다.

| 증상 | 가능한 원인과 진단 | 해결과 팀 확인 조건 |
|---|---|---|
| `uv: command not found` | 새 터미널에서도 버전이 안 나오면 설치/PATH 확인 | OS별 설치 후 버전 확인. 회사 설치 권한은 팀에 확인 |
| Python 버전·lock 오류 | doctor 버전과 pyproject/lock 변경을 대조 | 3.12 환경을 준비. lock 임의 갱신 전에 담당자 확인 |
| 패키지 설치 오류 | 네트워크·플랫폼·첫 실패 패키지 확인 | OS와 실패 도구를 보고. 해시 불일치 우회 금지 |
| hook FAIL | hook 설치 메시지와 별도 hooksPath 확인 | bootstrap 재실행은 기존 경로 충돌 확인 뒤 진행. 공통 hook 경로 변경은 팀 결정 |
| Git 변경 누락·충돌 | status의 미추적/스테이지/충돌을 구분 | [Git 복구 안내](git-guide.md)에 따라 보존. force/reset으로 덮지 않음 |
| GitHub 접근·CI 오류 | 계정·저장소·커밋·첫 실패 Step을 대조 | 기준 run과 권한 확인. 정책 수정은 관리자에게 요청 |
| Claude Code 편집 차단 | 작업 브랜치, 대상 경로와 hooks/permissions 확인 | 승인된 브랜치 또는 루트 사용. 우회 모드 금지. 개인 설정 충돌 보고 |
| SDK 옵션/Markdown 오류 | SDK import·잠금 버전·경로·확장자 확인 | [Agent 실습](agent-guide.md)의 읽기/옵션 검사로 좁힘. 실제 query로 바꾸지 않음 |
| MCP mock 실패 | 가상 반환 타입과 await/호출 인자 확인 | `is_error` 등 설치 버전의 타입을 확인. 실제 도구 연결로 대체하지 않음 |
| 테스트 FAIL 또는 수집 오류 | 테스트 이름·traceback·기대와 실제 값 확인 | [pytest 실습](testing-guide.md)처럼 한 테스트로 좁혀 재현 |
| Sonar NOT RUN | 기본 비활성 또는 승인 조건 미충족 | 설정 전 정상일 수 있다. 실제 실패라면 [승인 조건](quality-guide.md) 확인 |

## 실습 · 실패를 팀에 전달하기

예를 들어 SDK 단일 테스트가 import 오류로 실패했다면 먼저 설치·잠금 버전·실행 위치가 맞는지 확인하고, 같은 명령에서 실패가 반복되는지 본다. 상태와 첫 오류(비밀 제외), OS·도구 버전, 예상과 실제, 이미 시도한 확인, 다음에 필요한 결정을 기록한다. “전체가 안 돼서 다시 설치했다”는 재현에 정보가 부족하다. “루트에서 SDK 옵션 검사 1건이 import 단계에서 실패했고, doctor의 Python 항목은 PASS였다”처럼 관찰을 적는다.

**Claude Code 연습** — “README·지침·관련 검사와 현재 상태를 읽고 영향이 가장 작은 확인 순서를 제안해줘. 수정 전에 변경 파일과 복구 범위를 보여줘.” 사람이 첫 오류와 diff를 대조하고 같은 명령의 전후 결과를 비교한다. 팀 공통 환경·권한 결정이면 기존 Issue를 확인하고 초안을 제안하게 한다.

- [ ] 증상·원인 가설·확인 증거·다음 행동을 한 줄씩 기록한다.
- [ ] 기존 작업과 비밀을 보호한 상태로 팀에 보고한다.

[uv 프로젝트 환경](https://docs.astral.sh/uv/concepts/projects/sync/) · [pytest 사용법](https://docs.pytest.org/en/stable/how-to/usage.html) · [공통 검사](quality-guide.md)
