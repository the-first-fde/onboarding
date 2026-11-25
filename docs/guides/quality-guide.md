# GitHub Actions와 품질 검사 읽기

**학습 목표**는 로컬 실패와 원격 CI 실패를 구별하고, 어느 검사 단계가 왜 실패했는지 판단하는 것이다. CI(Continuous Integration)는 함께 검토할 변경에 같은 검사를 반복해 실행하는 방식이다. GitHub Actions는 이벤트가 발생하면 Runner(실행 환경)에서 Job의 Step을 차례로 실행한다.

| 검사 | 읽어야 하는 결과 |
|---|---|
| Ruff lint / format | 규칙 위반 파일·행 및 Markdown 코드 블록의 서식 |
| Pyright | 기대 타입과 전달한 타입 또는 반환값 |
| pytest | 기대 동작, 실제 값, 실패 테스트 |
| Coverage | 실행된 코드 범위. `coverage.xml`을 생성하며 초기 수치 측정 뒤 80%가 목표 |
| Gitleaks / 문서 검사 | 마스킹된 잠재 비밀 경고, 깨진 링크 또는 지침 누락 |
| SonarQube Cloud | 승인된 CI 정적 분석 및 Quality Gate(프로젝트 품질 기준) 결과 |

## 실습 · Verify에서 실패 위치 찾기

[환경 설치](getting-started.md) 뒤 루트에서 아래 명령으로 공통 기준선을 실행한다. `--locked`는 의존성 잠금 파일 변경을 막고, verify는 각 검사 종료코드를 모아 하나라도 실패하면 실패를 전달한다. 테스트 캐시와 coverage XML이 생성된다. 로컬 분석 명령에 Sonar는 포함되지 않는다.

```bash
uv run --locked python scripts/verify.py
```

1. [CI 설정](../../.github/workflows/ci.yml)에서 PR/main push → 잠금 환경 설치 → Gitleaks 준비 → 공통 verify 순서를 읽는다. 읽기 권한, 고정 Actions SHA, 시간 제한, 동시 실행 취소 및 checkout 자격 유지 비활성도 확인한다.
2. 실제 GitHub 실행이 있다면 **Actions → CI → 해당 커밋의 run → verify job**을 찾는다. 실패한 Step의 첫 오류를 보고 설치·타입·테스트·문서 실패를 구분한다. PR의 커밋과 실행 커밋이 같아야 한다. 원격 실행을 하지 않았다면 NOT RUN이다.
3. 포맷 오류를 예로 들면 해당 문서 블록을 찾고 작업 범위에서 고친 뒤 동일 명령을 실행한다. 이전 커밋의 녹색 표시나 로컬 PASS를 현재 원격 상태로 표시하지 않는다. 실패 로그에 비밀이 보이면 복사하지 말고 사고 절차를 따른다.

## SonarQube Cloud는 승인된 CI에서만

기존 Organization/Project의 외부 분석 허용, Private, CI-based analysis를 확인한다. Automatic analysis가 중복 실행되는지 관리자에게 확인한다. **승인된 main에서 수동 CI**를 실행할 때만 `run_sonar=true`, `SONAR_ENABLED=true`, `EXTERNAL_ANALYSIS_APPROVED=true` 조건을 모두 확인한다. GitHub 관리자 설정은 `SONAR_ORGANIZATION`, `SONAR_PROJECT_KEY`를 Variables, 최소 권한 `SONAR_TOKEN`을 Secret에 둔다. [환경 설정 안내](environment-guide.md)

일반 PR/main push에 분석을 보내지 않으며 기본 상태는 NOT RUN이다. 승인 후 스캔은 기존 CI의 `coverage.xml`을 사용하고 코드 범위는 src/tests로 제한한다. Quality Gate 대기와 결과는 원격에서 확인한다. 프로젝트 생성·설정 변경·분석 전송은 이 실습에서 미실행이다. 키 누락이나 조건 불일치로 FAIL이면 값을 출력하거나 우회하지 말고 승인과 변수 이름을 확인한다.

**Claude Code 연습** — “CI YAML과 verify를 읽고 어떤 단계가 실패했는지 계획부터 설명해줘. 로컬 재현만 제안하고 원격 설정은 건드리지 마.” 사람은 실패 행, 테스트 종료코드, diff, 해당 커밋을 대조한다. 서버 설정이나 전송 정책이 필요하면 Issue 초안을 제안하게 한다.

- [ ] CI 단계와 로컬 명령을 서로 연결한다.
- [ ] Sonar 미실행과 Quality Gate PASS를 구분한다.

[GitHub Actions 공식 문서](https://docs.github.com/en/actions) · [Sonar 공식 Action](https://github.com/SonarSource/sonarqube-scan-action)
