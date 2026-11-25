# 업무 Agent 정의와 SDK 경계

**학습 목표**는 Markdown 정의·실행 옵션·모델 결과를 구별하고, 모델 비용 없이 최소 구조를 확인하는 것이다. [환경 설치](getting-started.md)로 SDK와 타입을 설치하고 [업무 양식](../../agents/template.md)을 읽는다.

Agent는 목표에 맞춰 입력을 처리하는 실행 단위다. Instructions는 역할과 제약, Tools는 외부 작업을 요청하는 함수 또는 도구, Structured Output(구조화 출력)은 다음 코드가 검증하고 처리할 수 있는 정해진 형태다. 모델이 그럴듯한 문자열을 돌려주는 것과 스키마 검증 통과는 다르다. 팀은 사람이 읽을 업무 정의를 Markdown으로 관리하고 Python SDK에서 실행 경계를 구성한다.

## 실습 · 가상 카운터 요약 역할

1. 임시 메모에 역할 “기술 카운터 한 줄 요약”, 입력 “가상 정수”, 출력 “가상 요약”, 도구 “없음”을 작성한다. 실제 메일·입사 처리·업무 상태는 이 예제와 관계없다.
2. 실제 [smoke.py](../../src/hr_onboarding/smoke.py)가 Markdown을 읽고 옵션을 어떻게 만드는지 본다. 지금 SDK는 옵션만 구성한다. 아래 예제는 임시 디렉터리에 가상 Markdown을 만들고 검사한 뒤 지운다.
3. 루트에서 예제와 아래 테스트를 실행한다. 결과를 만들 SDK query나 Claude CLI 프로세스는 시작하지 않는다. 향후 승인된 구현에서는 정의 읽기→옵션 구성→모델 호출→구조 검증→그래프 반환 순서를 명세에서 검토한다.

```python
from pathlib import Path
from tempfile import TemporaryDirectory

from hr_onboarding.smoke import offline_options, read_template


def inspect_definition(path: Path) -> str:
    """가상 업무 정의와 실행 옵션의 도구 경계를 확인한다.

    Args:
        path: 실습 Markdown 파일.

    Returns:
        읽은 정의 텍스트.
    """
    options = offline_options()
    assert options.tools == [] and options.mcp_servers == {}
    return read_template(path)


with TemporaryDirectory() as directory:
    target = Path(directory) / "counter.md"
    target.write_text("# 가상 카운터 요약\n도구 없음\n", encoding="utf-8")
    assert "도구 없음" in inspect_definition(target)
```

```bash
uv run --locked pytest -q tests/test_smoke.py::test_sdk_options_do_not_enable_tools tests/test_smoke.py::test_runtime_template_is_readable
```

루트에서 `::`로 선택한 두 테스트가 통과해야 한다. 실패 시 SDK 버전, Markdown 확장자, 파일 경로와 도구 옵션을 확인한다. `tools=[]`, `mcp_servers={}`, `setting_sources=[]`, `skills=[]`와 `strict_mcp_config=True`를 코드와 대조한다. `allowed_tools=[]` 하나만 보고 기본 도구가 모두 제거됐다고 판단하면 안 된다. 좋은 결과는 도구 없는 옵션과 텍스트 읽기 증거다. 모델이 올바른 업무 산출물을 만들었다는 주장은 별도 평가가 필요하다.

**Claude Code 연습** — “업무 양식·담당 Spec·SDK 코드를 읽고 각 옵션의 효과와 현재 Git 상태를 설명해줘. 임시 mock만 검증하는 계획을 먼저 보여줘.” 사람은 파일 접근, 호출·비용 여부, diff, 두 테스트를 확인한다. 모델 사용이나 출력 계약의 기준이 필요하면 Issue 초안을 제안하게 한다.

- [ ] Agent, 도구, 출력, SDK 호출과 옵션 생성의 차이를 설명한다.
- [ ] 두 로컬 테스트 결과와 후속 실제 실행 조건을 구분한다.

[Claude Agent SDK Python](https://code.claude.com/docs/en/agent-sdk/python) · [SDK 모듈 안내](../../src/hr_onboarding/agents/README.md)
