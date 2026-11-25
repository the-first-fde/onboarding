# LangGraph와 사람 승인

**학습 목표**는 업무 단계가 값을 주고받고 승인 대기 후 재개되는 원리를 확인하는 것이다. [설치](getting-started.md) 뒤 [기술 카운터 소스](../../src/hr_onboarding/smoke.py)를 읽는다. 제품에서 실행 순서가 보이면 단계별 오류와 승인 경계를 테스트하기 쉽다.

State는 단계가 공유하는 값, Node는 한 단계, Edge는 다음 단계의 연결, Conditional Edge는 결과에 따라 목적지를 고르는 연결이다. Checkpoint는 재개에 필요한 실행 기록이고, Interrupt는 사람 입력을 기다리는 일시 중지다. thread ID는 어떤 실행 기록을 이어갈지 구분한다. 메모리 저장은 프로세스 종료 뒤 남지 않으며 현재 제품의 저장 방식을 정하지 않는다.

## 실습 · 기술 카운터와 가상 승인 대기

1. 카운터의 START → increment → END 순서를 찾고 아래 테스트로 0에서 1이 되는지 확인한다.
2. 다음 Python 예제를 잠금 환경에서 실행한다. interrupt에서 대기했다가 같은 thread ID로 재개한다. 승인일 때만 다음 노드의 **가상 결과**가 기록된다. 외부 시스템과 연결하지 않는다.
3. 재개 입력을 False로 바꿔 실행하는 경우 승인 노드 결과가 없어야 한다. 실행 중 같은 ID를 다른 작업에 재사용하지 않는다. 실제 업무 승인 규칙은 고객사와 사람의 확인을 기다린다.

```python
from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class DemoState(TypedDict, total=False):
    """기술 실습용 상태 값을 담는다."""

    approved: bool
    preview: str


def wait_for_review(state: DemoState) -> DemoState:
    """가상의 사람 판단을 기다린다.

    Args:
        state: 실습 상태.

    Returns:
        재개 시 전달받은 실습 승인 여부.
    """
    return {"approved": interrupt("가상 승인 여부를 입력하세요") is True}


def route(state: DemoState) -> str:
    """가상 승인 상태로 다음 노드 이름을 정한다.

    Args:
        state: 판단이 기록된 실습 상태.

    Returns:
        승인 경로 또는 종료 경로 이름.
    """
    return "preview" if state.get("approved") else "stop"


def make_preview(state: DemoState) -> DemoState:
    """외부 변경 없이 가상 결과를 만든다.

    Args:
        state: 승인 후의 실습 상태.

    Returns:
        외부 전송이 없는 로컬 결과.
    """
    return {"preview": "local only"}


builder = StateGraph(DemoState)
builder.add_node("review", wait_for_review)
builder.add_node("preview", make_preview)
builder.add_edge(START, "review")
builder.add_conditional_edges("review", route, {"preview": "preview", "stop": END})
builder.add_edge("preview", END)
graph = builder.compile(checkpointer=InMemorySaver())

for choice in (True, False):
    config = {"configurable": {"thread_id": f"demo-{choice}"}}
    paused = graph.invoke({"approved": False}, config=config)
    assert "__interrupt__" in paused and "preview" not in paused
    resumed = graph.invoke(Command(resume=choice), config=config)
    assert ("preview" in resumed) is choice
```

```bash
uv run --locked pytest -q tests/test_smoke.py::test_graph_runs_without_network
```

명령은 루트에서 `::`로 카운터 검사를 선택한다. 정상 결과는 1건 PASS다. 그래프 실습이 재개되지 않으면 checkpointer, thread ID, Command 입력을 확인한다. interrupt가 있는 노드는 재개 시 처음부터 다시 시작할 수 있다. 실제 설계에서는 신원·승인 범위·만료를 검증하고 승인 전 외부 쓰기를 금지하며, 재실행 중복을 막는 경계를 별도로 설계한다. “모델 답변에 승인됨이 들어 있다”는 실제 사람 승인으로 인정하지 않는다. 실제 MCP 쓰기는 현재 금지다.

**Claude Code 연습** — “워크플로우 README·검토 Spec을 확인하고 노드·상태·승인 전후를 표로 설명해줘. 가상 실행 계획을 먼저 보여줘.” 사람은 승인 전 출력이 없는지, 승인·거부가 다른지, diff에 외부 동작이 들어갔는지 확인한다. 상태나 재승인 규칙이 미정이면 Issue를 제안하게 한다.

- [ ] State·Node·Edge·Checkpoint를 예제에서 각각 찾는다.
- [ ] 중지·재개·거부를 확인하고 외부 시스템 승인 경계를 설명한다.

[LangGraph 그래프 API](https://docs.langchain.com/oss/python/langgraph/graph-api) · [Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)
