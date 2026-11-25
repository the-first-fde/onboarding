"""로컬 환경과 Git hooks를 설치한다. 실제 .env는 생성하지 않는다."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """Lock 기반 설치 뒤 Gitleaks 및 pre-commit hooks를 준비한다."""
    commands = [
        ["uv", "sync", "--locked"],
        [sys.executable, "scripts/install_tools.py"],
        [
            "uv",
            "run",
            "--locked",
            "pre-commit",
            "install",
            "--hook-type",
            "pre-commit",
            "--hook-type",
            "pre-push",
        ],
        ["uv", "run", "--locked", "python", "scripts/doctor.py"],
    ]
    for command in commands:
        subprocess.run(command, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
