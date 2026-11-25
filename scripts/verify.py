"""로컬과 CI에서 동일한 인증 없는 검증을 수행한다."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """모든 검사 결과를 모으며 Sonar는 실행하지 않는다."""
    checks = [
        ("Ruff lint", ["ruff", "check", "."]),
        ("Ruff format", ["ruff", "format", "--check", "."]),
        ("Instructions", [sys.executable, "scripts/check_instructions.py"]),
        ("Pyright", ["pyright"]),
        (
            "Mock tests/coverage",
            ["pytest", "--cov", "--cov-report=term-missing", "--cov-report=xml"],
        ),
        ("Gitleaks", [sys.executable, "scripts/scan_secrets.py"]),
    ]
    failed = False
    for label, command in checks:
        code = subprocess.run(command, cwd=ROOT, check=False).returncode
        print(f"{label}: {'PASS' if code == 0 else 'FAIL'}", flush=True)
        failed |= code != 0
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
