from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from claude_agent_sdk import query
from mcp.types import CallToolResult, TextContent
from pydantic import ValidationError

from hr_onboarding.config import Settings
from hr_onboarding.smoke import offline_options, read_template, run_smoke


@pytest.mark.asyncio
async def test_graph_runs_without_network():
    assert await run_smoke() == 1


def test_sdk_options_do_not_enable_tools():
    options = offline_options()
    assert options.tools == []
    assert options.setting_sources == []
    assert options.skills == []
    assert options.strict_mcp_config
    assert options.allowed_tools == []
    assert options.mcp_servers == {}
    assert options.max_turns == 1
    assert callable(query)  # SDK import surface only; never invoke query.


@pytest.mark.asyncio
async def test_mcp_mock_result_without_transport():
    mock_call = AsyncMock(
        return_value=CallToolResult(
            content=[TextContent(type="text", text="technical mock")], is_error=False
        )
    )
    result = await mock_call("technical_probe", {})
    assert not result.is_error
    assert result.content[0].text == "technical mock"
    mock_call.assert_awaited_once_with("technical_probe", {})


def test_runtime_template_is_readable():
    text = read_template(Path("agents/template.md"))
    assert "DEFERRED" in text


def test_template_rejects_wrong_extension(tmp_path):
    with pytest.raises(ValueError, match="Markdown"):
        read_template(tmp_path / "probe.txt")


def test_template_rejects_empty_content(tmp_path):
    path = tmp_path / "empty.md"
    path.write_text(" ", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        read_template(path)


def test_missing_template_is_reported(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_template(tmp_path / "missing.md")


def test_settings_default_to_mock_without_dotenv():
    assert Settings().mode == "mock"
    with pytest.raises(ValidationError):
        Settings(mode="live")
