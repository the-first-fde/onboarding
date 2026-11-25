"""HR Schema와 무관한 SDK/그래프/Markdown 연결 기술 검증."""

from pathlib import Path
from typing import TypedDict

from claude_agent_sdk import ClaudeAgentOptions
from langgraph.graph import END, START, StateGraph


class SmokeState(TypedDict):
    """테스트 전용 카운터이며 HR 공통 State가 아니다."""

    count: int


def read_template(path: Path) -> str:
    """지정된 안전한 Markdown 양식을 읽는다.

    Args:
        path: 호출자가 선택한 비민감 Markdown 파일.

    Returns:
        비어 있지 않은 Markdown 문자열.

    Raises:
        ValueError: Markdown 확장자가 아니거나 내용이 비었을 때.
    """
    if path.suffix != ".md":
        raise ValueError("Only Markdown templates are supported")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("Template is empty")
    return content


def offline_options() -> ClaudeAgentOptions:
    """SDK 옵션만 생성하며 CLI 실행·인증·모델 호출은 수행하지 않는다."""
    return ClaudeAgentOptions(
        tools=[],
        allowed_tools=[],
        mcp_servers={},
        strict_mcp_config=True,
        setting_sources=[],
        skills=[],
        max_turns=1,
    )


async def run_smoke() -> int:
    """로컬 그래프 한 노드의 비동기 실행 결과를 반환한다."""

    async def increment(state: SmokeState) -> SmokeState:
        return {"count": state["count"] + 1}

    builder = StateGraph(SmokeState)
    builder.add_node("increment", increment)
    builder.add_edge(START, "increment")
    builder.add_edge("increment", END)
    result = await builder.compile().ainvoke({"count": 0})
    return result["count"]
