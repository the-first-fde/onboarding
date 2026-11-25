"""수정한 Python 파일만 Ruff로 가볍게 확인한다. 자동 수정은 하지 않는다."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    """공유 소스만 검사하며 실패는 Claude에 진단으로 반환한다."""
    try:
        event = json.load(sys.stdin)
        path = Path(event.get("tool_input", {}).get("file_path", ""))
        path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
        if path.suffix != ".py" or not path.is_relative_to(ROOT):
            return 0
        relative = path.relative_to(ROOT)
        if relative.parts[0] not in {"src", "tests", "scripts"}:
            return 0
        result = subprocess.run(
            ["uv", "run", "--locked", "ruff", "check", str(relative)], cwd=ROOT, check=False
        )
        return 2 if result.returncode else 0
    except (ValueError, OSError):
        print("Post-edit check failed; run verify manually", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
