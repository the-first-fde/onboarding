# Python 코드를 읽고 설명하기

**학습 목표**는 작은 Python 함수의 입력·출력·실패를 읽고, AI가 만든 코드를 테스트로 확인하는 것이다. [환경 설치](getting-started.md) 이후 실행한다.

모듈(module)은 Python 파일이고 패키지(package)는 모듈을 묶은 이름이다. 함수는 한 동작, 클래스는 객체의 상태와 동작을 묶는다. 예를 들어 [smoke.py](../../src/hr_onboarding/smoke.py)는 기술 함수를, [config.py](../../src/hr_onboarding/config.py)의 Settings 클래스는 로컬 설정을 정의한다. 타입 힌트는 코드 읽기와 Pyright 점검에 도움을 주지만 그 자체로 외부 입력을 검증하지 않는다. Docstring은 함수가 보장하는 동작·인자·반환·예외를 설명한다.

## 실습 · 카운터의 계약 읽기

작은 계산은 먼저 동기 함수로 이해한다. 아래 코드를 임시 파일에 복사하고 루트에서 `uv run --locked python` 뒤에 그 파일 경로를 넣거나 표준입력으로 실행한다. 출력 1과 의도한 예외를 확인한다. 업무 데이터와 무관한 기술 예제다.

```python
def increment_count(count: int) -> int:
    """기술 카운터를 증가시킨다.

    Args:
        count: 음수가 아닌 카운터.

    Returns:
        하나 증가한 카운터.

    Raises:
        ValueError: 카운터가 음수일 때.
    """
    if count < 0:
        raise ValueError("count must be nonnegative")
    return count + 1


print(increment_count(0))
try:
    increment_count(-1)
except ValueError as exc:
    print(exc)
```

잘 작성된 예는 입력이 잘못됐을 때 구체적인 예외로 실패한다. 개선할 예는 `except Exception: pass`로 실패를 숨겨 호출자가 정상 결과로 오해하게 만드는 것이다. 함수·변수는 snake_case, 클래스는 PascalCase, 식별자는 영어, 공개 동작 설명은 한국어 Google Style Docstring을 사용한다. 타입은 서명에, 의미는 Args/Returns/Raises에 둔다.

`async def`는 호출 시 코루틴을 만들고 `await`는 결과를 기다린다. 그래프의 `ainvoke`와 비동기 노드는 대기 작업을 조합할 때 쓴다. 동기 함수에 무조건 async를 붙이면 호출 방식만 복잡해진다. “coroutine was never awaited”가 나오면 호출자가 await하는 위치와 실행 환경을 확인한다. 네트워크 호출로 바꾸지 않고 [그래프 실습](workflow-guide.md)에서 확인할 수 있다.

```bash
uv run --locked ruff check .
uv run --locked ruff format --check .
```

루트에서 각각 lint(코드 규칙)와 포맷을 검사한다. `.`는 현재 경로, `--check`는 수정 없이 확인한다. 첫 오류의 파일/행/코드를 읽는다. 문서 속 Python 블록도 포맷 대상이다. 포맷 도구를 수정 모드로 쓰면 파일이 바뀌므로 승인된 파일만 지정하고 diff를 확인한다.

**Claude Code 연습** — “작업 README·지침과 함수 테스트를 읽고 인자·반환·예외를 설명해줘. 현재 동작을 바꾸는 부분은 계획에서 먼저 표시해줘.” 사람이 가지별 입력을 넣어 본 뒤 승인한다. 변경 후 diff와 테스트 결과를 확인하고 용어·공통 타입 합의가 필요하면 Issue를 제안하도록 한다.

- [ ] 모듈과 클래스를 찾고 함수 서명과 Docstring만으로 호출 방법을 설명한다.
- [ ] 성공 출력과 실패 경로를 직접 확인하고, await가 필요한 위치를 말한다.

[Python 모듈](https://docs.python.org/3.12/tutorial/modules.html) · [비동기 함수](https://docs.python.org/3.12/library/asyncio-task.html) · [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
