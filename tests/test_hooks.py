# ruff: noqa: S603
# 이 테스트는 고정된 프로젝트 hook만 subprocess로 호출한다.
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(".claude/hooks/protect_files.py").resolve()
spec = importlib.util.spec_from_file_location("protect_files", HOOK)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize(
    "name",
    [
        ".env",
        ".env.local",
        "secrets/probe.txt",
        "credentials/probe.json",
        "private.key",
        ".claude/settings.local.json",
        "../outside.md",
    ],
)
def test_sensitive_paths_are_denied_without_reading(name):
    decision, _ = module.decide({"tool_name": "Read", "tool_input": {"file_path": name}}, "task/x")
    assert decision == "deny"


def test_main_edits_are_denied():
    assert (
        module.decide({"tool_name": "Write", "tool_input": {"file_path": "README.md"}}, "main")[0]
        == "deny"
    )


def test_task_branch_allows_ordinary_edits_to_default_permissions():
    assert (
        module.decide({"tool_name": "Edit", "tool_input": {"file_path": "README.md"}}, "task/x")[0]
        is None
    )


def test_dependency_change_asks_for_approval():
    assert (
        module.decide({"tool_name": "Edit", "tool_input": {"file_path": "uv.lock"}}, "task/x")[0]
        == "ask"
    )


def test_mcp_is_denied():
    assert module.decide({"tool_name": "mcp__probe__read", "tool_input": {}}, "task/x")[0] == "deny"


def test_shell_mutation_requires_permission():
    for command in [
        "git commit -m test",
        "git push",
        "cat .env",
        "python -c pass",
        "git status; cat .env",
    ]:
        assert (
            module.decide({"tool_name": "Bash", "tool_input": {"command": command}}, "main")[0]
            == "ask"
        )


def test_hook_executable_protocol():
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"tool_name": "Read", "tool_input": {"file_path": ".env"}}),
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
    malformed = subprocess.run(
        [sys.executable, str(HOOK)], input="{", text=True, capture_output=True
    )
    assert malformed.returncode == 2


def test_env_example_is_readable():
    assert (
        module.decide({"tool_name": "Read", "tool_input": {"file_path": ".env.example"}}, "main")[0]
        is None
    )


@pytest.mark.parametrize("tool", ["Grep", "Glob"])
@pytest.mark.parametrize("path", [".env.production", "token.json", "private.key", "."])
def test_search_sensitive_paths_and_broad_root_are_denied(tool, path):
    decision, _ = module.decide({"tool_name": tool, "tool_input": {"path": path}}, "task/x")
    assert decision == "deny"


def test_scoped_source_search_uses_default_permissions():
    decision, _ = module.decide(
        {"tool_name": "Grep", "tool_input": {"path": "src", "pattern": "State"}}, "task/x"
    )
    assert decision is None


def test_glob_sensitive_pattern_is_denied():
    decision, _ = module.decide(
        {"tool_name": "Glob", "tool_input": {"path": "src", "pattern": "**/.env*"}}, "task/x"
    )
    assert decision == "deny"
