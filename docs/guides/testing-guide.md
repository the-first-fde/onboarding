# pytest로 동작을 확인하고 실패를 읽기

**학습 목표**는 테스트가 관찰하는 동작을 설명하고 실패의 원인을 재현하는 것이다. [환경 설치](getting-started.md) 후 [테스트 디렉터리](../../tests/README.md)를 확인한다.

단위 테스트(unit test)는 작은 계산이나 경계 하나, 통합 테스트(integration test)는 여러 모듈의 연결을 확인한다. Fixture는 반복 준비물, Mock은 호출과 결과를 정해 둔 대역, Fake는 실제 시스템 대신 동작하는 단순 구현이다. Coverage(커버리지)는 실행한 코드 범위를 측정한다. Agent Evaluation은 모델 산출물을 기준·대표 사례·실패 비용에 따라 평가한다. 옵션 검사가 통과해도 모델 품질이나 고객사 적합성이 확인된 것은 아니다.

## 실습 · 실패와 통과를 각각 관찰하기

아래 두 테스트를 임시 경로의 `test_guide_demo.py`에 저장한다. 기술 카운터 사용 예제로, 첫 테스트의 기대값을 일부러 틀리게 적었다. 루트에서 `uv run --locked pytest -c pyproject.toml -q` 뒤에 임시 파일 경로를 넣어 실행한다. `-c`는 저장소의 pytest 설정을 적용하고, 파일을 지정하면 해당 파일만 수집한다. `-q`는 출력을 줄인다. 예제 파일은 팀 소스에 넣지 않는다.

```python
import pytest

from hr_onboarding.smoke import run_smoke


@pytest.mark.asyncio
async def test_reads_the_failure() -> None:
    """틀린 기대값이 실패로 표시되는지 확인한다."""
    assert await run_smoke() == 2


@pytest.mark.asyncio
async def test_observes_one_step() -> None:
    """기술 그래프가 카운터를 한 번 증가시키는지 검증한다."""
    assert await run_smoke() == 1
```

1. 1 FAIL·1 PASS와 `assert 1 == 2`를 확인한다. 오류 경로의 위치를 읽어 설정 문제인지 기대값 문제인지 분리한다.
2. 기술 그래프 계약은 0→1이다. 첫 실습 테스트를 제거하거나 기대값을 1로 수정해 다시 실행한다. 실제 개발의 RED/GREEN은 승인된 행동을 실패 테스트로 표현한 뒤 최소 구현을 통과시키는 과정이다. 기존 명세에 근거 없이 테스트를 약하게 만들지 않는다.
3. 실제 테스트 [test_smoke.py](../../tests/test_smoke.py)에서 `AsyncMock`가 MCP 응답과 호출 인자를 검증하는 부분을 찾아본다. [conftest.py](../../tests/conftest.py)는 저장소 테스트의 소켓 연결을 차단한다. 임시 디렉터리의 독립 예제에는 그 fixture가 적용된다고 가정하지 않는다.

```bash
uv run --locked pytest -q tests/test_smoke.py
uv run --locked python scripts/verify.py
```

첫 명령은 기술 테스트를 좁혀 실행하고 둘째는 문서·lint·타입·테스트·비밀 검사를 함께 실행한다. verify는 `coverage.xml`과 로컬 캐시를 생성한다. 실패하면 테스트 이름·traceback·기대값을 먼저 보고, “Network is disabled”가 나오면 접근 경계에 mock을 둔다. 초기 커버리지는 측정값이고 80%는 이후 목표다. 실제 query, 외부 MCP, 고객사 업무 fixtures 및 평가 기준은 승인과 계약 확인 뒤 별도로 검증한다.

**Claude Code 연습** — “README·Spec·테스트를 확인하고 첫 실패의 실제값과 기대값을 풀어 설명해줘. 계약을 바꾸지 않는 수정 계획을 먼저 줘.” 사람은 테스트가 결과를 관찰하는지 확인하고 승인 후 diff와 실패/통과 증거를 본다. 품질 기준이 미정이면 Issue 초안을 제안하도록 한다.

- [ ] 단위·통합·모델 평가의 증거를 구분한다.
- [ ] 하나의 실패를 재현하고 기대값의 근거를 설명한다.

[pytest 시작하기](https://docs.pytest.org/en/stable/getting-started.html) · [Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) · [가상 자료 안내](../../fixtures/README.md)
