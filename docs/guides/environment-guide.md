# 환경 변수와 GitHub Secrets

**학습 목표**는 프로그램에 전달할 설정과 비밀의 보관 위치를 선택하고, 값 노출 없이 설정을 점검하는 것이다. [환경 설치](getting-started.md)를 마치고 공개 가능한 [.env.example](../../.env.example)과 [config.py](../../src/hr_onboarding/config.py)를 읽는다.

환경 변수(Environment Variable)는 프로그램을 시작할 때 운영체제가 전달하는 이름과 값이다. `.env`는 도구가 선택적으로 읽는 파일이며 환경 변수와 같은 개념이 아니다. `.env.example`에는 공유 가능한 이름과 안전한 예시만 둔다. 실제 `.env`를 생성하거나 읽지 않는다. 현재 Settings는 `ONBOARDING_` 접두사, dotenv 비활성, `mock`만 허용하도록 설정되어 있다.

## 실습 · 현재 명령에 공개 mock 값만 전달하기

```bash
ONBOARDING_MODE=mock uv run --locked python -c 'from hr_onboarding.config import Settings; assert Settings().mode == "mock"; print("mock configuration PASS")'
```

macOS/Linux/WSL2에서 루트에서 실행한다. 앞의 공개 예시 값은 해당 프로세스에서만 유효하다. `-c`는 뒤 문자열을 Python으로 실행한다. 성공 시 `mock configuration PASS`다. `ValidationError`가 나오면 변수 이름·접두사·허용 값·Python 환경을 확인한다. 이 예시는 운영체제 전체의 설정을 바꾸거나 실제 .env를 만들지 않는다. API 키를 같은 명령 형태로 붙이면 셸 이력이나 실행 로그에 남을 수 있다.

## 승인된 CI 설정 절차

1. 비민감 키 이름·옵션은 GitHub **Settings → Secrets and variables → Actions → Variables**, 자격 증명은 같은 위치의 **Secrets**를 사용한다. 일반 PR CI에는 Claude/MCP 인증이 필요 없다.
2. 권한 있는 관리자가 프로젝트 키와 Secret을 승인된 채널에서 등록한다. 워크플로는 필요한 **step**에만 `vars` 또는 `secrets` 참조를 전달한다. 현재 예시는 [CI YAML](../../.github/workflows/ci.yml)에서 변수 이름과 주입 위치로 확인한다. Sonar 활성화 순서는 [품질 가이드](quality-guide.md)에 있다.
3. 값은 출력하지 않고 승인 상태·변수 이름·해당 실행의 결과만 검토한다. 누락 시 이름과 단계만 공유한다. 실제 Secret 등록은 이 실습에서 미실행이다.

협업 동기화용 Secret(`NOTION_SYNC_TOKEN`, `PROJECT_APP_PRIVATE_KEY`)과 Variable 이름은 [GitHub ↔ Notion 연동 가이드](collaboration-integration-guide.md) 9·10절에 있다. HR 업무용 인증과 섞지 않는다.

**좋은 예**는 mock 값과 필요한 변수 이름만 공유한다. **피할 예**는 실제 값이 든 .env를 복제하거나 PR 로그 확인을 위해 값을 출력하는 것이다. Git에는 실제 환경 변수 값과 비밀을 올리지 않는다. 후속 실사용은 개인 보안 저장소나 운영체제 환경을 사용하고 AI에게 값을 주지 않는다.

**Claude Code 연습** — “.env.example과 config.py, CI YAML만 읽고 변수 이름·옵션·사용 단계와 실패 시 확인할 항목을 알려줘. 실행 전에 계획을 보여줘.” 사람이 접근 파일 목록과 로컬 mock 출력을 검토한다. 새 인증이나 공유 경계를 결정해야 하면 Issue 초안을 제안하게 한다.

- [ ] OS 환경 변수, .env, .env.example, Secrets, Variables의 차이를 설명한다.
- [ ] 공개 예시 값만 전달하고 실제 비밀을 출력하지 않았는지 확인한다.

[GitHub Actions Secrets 공식 문서](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) · [Variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables)
