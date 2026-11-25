"""Claude PreToolUse 입력에 대해 비밀 파일과 위험 작업을 차단한다."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def branch_name() -> str:
    """현재 브랜치를 조회하며 실패하면 보호 대상으로 처리한다."""
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "main"


def decide(event: dict, branch: str) -> tuple[str | None, str]:
    """도구 요청의 허용/질문/차단 결정을 반환한다.

    Args:
        event: Claude Code PreToolUse JSON payload.
        branch: 현재 브랜치 이름.

    Returns:
        결정과 비민감 설명. None은 기본 권한 판단을 계속하라는 의미.
    """
    name = event.get("tool_name", "")
    data = event.get("tool_input", {})
    if name.startswith("mcp__"):
        return "deny", "Development MCP execution is disabled"
    if name in {"Read", "Edit", "Write", "NotebookEdit", "Grep", "Glob"}:
        raw = data.get("file_path", data.get("notebook_path", data.get("path", "")))
        path = Path(raw)
        path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        parts = path.parts
        if (
            (path.name.startswith(".env") and path.name != ".env.example")
            or any(part in {"secrets", "credentials", ".aws", ".ssh"} for part in parts)
            or path.suffix in {".pem", ".key", ".p12", ".pfx"}
            or path.name
            in {
                "token.json",
                "tokens.json",
                "credentials.json",
                ".mcp.json",
                "settings.local.json",
                "CLAUDE.local.md",
            }
            or path.name.startswith(("client_secret", "service-account"))
        ):
            return "deny", "Sensitive file access is prohibited"
        if not path.is_relative_to(ROOT):
            return "deny", "File access outside the project is prohibited"
        if name in {"Grep", "Glob"}:
            # Searches must stay in known shared subtrees; broad root searches are denied.
            relative = path.relative_to(ROOT)
            public = {"src", "tests", "scripts", "docs", "agents", ".github", "third_party"}
            if path.is_dir() and (not relative.parts or relative.parts[0] not in public):
                return "deny", "Scope searches to shared source/docs/tests directories"
            pattern = data.get("glob", "") if name == "Grep" else data.get("pattern", "")
            if any(
                word in pattern.lower()
                for word in (
                    ".env",
                    "secret",
                    "credential",
                    "token",
                    ".key",
                    ".pem",
                    "settings.local",
                )
            ):
                return "deny", "Searching sensitive file patterns is prohibited"
        if name in {"Edit", "Write", "NotebookEdit"}:
            if branch in {"main", "master"}:
                return "deny", "Create a task branch manually; first commit needs approval"
            if path.name in {"pyproject.toml", "uv.lock", "settings.json"}:
                return "ask", "Dependency or permission changes require explicit approval"
    if name == "Bash":
        command = data.get("command", "").strip()
        safe = {
            "git status",
            "git status --short",
            "git diff",
            "git diff --stat",
            "git diff --staged",
            "git log --oneline -5",
            "uv run --locked python scripts/verify.py",
            "uv run --locked python scripts/doctor.py",
        }
        if command not in safe:
            return (
                "ask",
                "Review shell effects: secrets, main edits and external writes are prohibited",
            )
    return None, "Default project permissions apply"


def main() -> int:
    """JSON 규약으로 결정을 출력하고 잘못된 입력은 차단한다."""
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or not isinstance(event.get("tool_input", {}), dict):
            raise ValueError("Invalid hook payload")
        decision, reason = decide(event, branch_name())
        if decision:
            print(
                json.dumps(
                    {
                        "hookSpecificOutput": {
                            "hookEventName": "PreToolUse",
                            "permissionDecision": decision,
                            "permissionDecisionReason": reason,
                        }
                    }
                )
            )
        else:
            print("{}")
        return 0
    except (ValueError, TypeError, OSError):
        print("Hook input/branch validation failed; tool blocked", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
