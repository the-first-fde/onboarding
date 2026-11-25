# 처음 실행하기

**학습 목표**는 터미널에서 올바른 저장소와 Python 환경을 찾고, 다른 팀원과 같은 의존성으로 첫 검사를 마치는 것이다.

터미널(Terminal)은 명령을 입력하는 창이다. Git은 변경을 기록하며, clone은 GitHub 저장소를 내 컴퓨터로 복제한다. Python은 프로그램을 실행하고, uv는 필요한 Python과 라이브러리(의존성)를 관리한다. 가상 환경 `.venv`는 이 저장소의 라이브러리를 다른 프로젝트와 분리한다. `uv.lock`에 설치 버전을 남기면 내 맥과 CI에서 같은 코드를 비교할 수 있다.

## 사전 준비와 복제

| OS | 시작하는 곳 | 준비 |
|---|---|---|
| macOS | Terminal | Git 설치 또는 승인된 Homebrew 환경에서 Git·uv 설치 |
| Linux | 배포판 터미널 | 배포판의 Git 패키지와 uv 공식 설치 방법 사용 |
| Windows | WSL2의 Linux 터미널 | WSL2 안에 Git과 uv 설치. 아래 명령과 hook 경로는 Linux 쪽에서 실행 |

OS별 설치 방법은 [uv 공식 설치](https://docs.astral.sh/uv/getting-started/installation/)와 [Microsoft WSL 설치](https://learn.microsoft.com/en-us/windows/wsl/install)를 따른다. 설치 후 새 터미널을 열어 도구가 경로에 잡히는지 확인한다. GitHub는 개인 계정과 2FA를 사용한다.

팀이 첫 버전을 공유한 뒤 GitHub의 **Code**에서 승인된 복제 주소를 복사한다. 복제본을 둘 상위 디렉터리에서 `git clone` 뒤에 그 주소를 넣어 실행하고, 생성된 저장소 디렉터리로 이동한다. 복제는 승인된 원격으로 읽기 통신을 하고 로컬 파일을 만든다. 공유 브랜치가 아직 없거나 접근 권한이 없으면 팀에서 먼저 확인한다. 이미 받은 프로젝트에서는 다시 clone할 필요가 없다.

## 실습 · 새 팀원의 첫 테스트

```bash
pwd
git rev-parse --show-toplevel
git --version
uv --version
uv run --locked python scripts/bootstrap.py
uv run --locked python scripts/doctor.py
uv run --locked python -m hr_onboarding
uv run --locked pytest -q tests/test_smoke.py
```

1. 첫 두 줄은 현재 위치와 Git 루트다. 서로 다르면 루트에서 다시 시작한다. 버전 명령은 설치 유무만 확인한다.
2. bootstrap은 `--locked` 상태로 의존성을 맞추고 해시를 확인해 Gitleaks를 설치한다. `.venv`, `.tools`, 로컬 pre-commit 및 pre-push hook을 준비하므로 쓰기 권한과 다운로드가 필요하다. hook은 커밋·푸시 시 검사할 로컬 프로그램이다.
3. doctor는 두 hook, Python 3.12, uv, Gitleaks와 별도 hook 경로 여부를 확인한다. 모두 PASS여야 한다.
4. `python -m`은 패키지 진입점을 실행한다. `Mock graph count: 1; HR functionality deferred`가 출력된다. pytest의 `-q`는 출력을 줄이고 지정한 기술 테스트만 실행한다.

**좋은 대응**은 lock 불일치가 나면 pyproject·lock 변경 여부와 오류를 공유하는 것이다. **피할 대응**은 오류가 보이지 않게 lock을 임의 갱신하거나 API 키를 넣는 것이다. Git 루트를 찾지 못하면 위치, 도구를 찾지 못하면 새 터미널과 설치, hook 오류면 권한과 별도 hooksPath를 차례로 확인한다. [문제 해결](troubleshooting.md)

**Claude Code 연습** — “루트·작업 안내와 설치 스크립트를 읽고, 현재 위치와 첫 검사 순서를 알려줘. 설치가 필요한 항목과 생성 경로를 보여줘.” 사람이 다운로드와 변경 파일을 확인한 뒤 허용한다. 실행 후 doctor의 항목별 결과, mock 출력, `git status`를 직접 대조한다. 공용 환경 정책이 필요하면 Issue 초안을 제안하도록 한다.

- [ ] Git 루트, 터미널 위치, 가상 환경의 의미를 설명할 수 있다.
- [ ] doctor와 mock 테스트를 직접 실행하고 실패 위치를 설명할 수 있다.

[Git 복제 공식 문서](https://git-scm.com/docs/git-clone) · [스크립트 안내](../../scripts/README.md)
