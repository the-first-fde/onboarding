"""비밀값을 읽거나 출력하지 않는 개발 환경 진단."""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """도구/훅 존재 여부와 개인 설정 충돌 가능성을 알린다."""
    checks = {
        "Python 3.12": sys.version_info[:2] == (3, 12),
        "uv": shutil.which("uv") is not None,
        "Gitleaks": (ROOT / ".tools/bin/gitleaks").is_file(),
    }
    for hook in ("pre-commit", "pre-push"):
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", f"hooks/{hook}"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        path = Path(result.stdout.strip())
        if not path.is_absolute():
            path = ROOT / path
        checks[hook] = path.is_file() and "pre_commit" in path.read_text()
    custom = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"], cwd=ROOT, capture_output=True, check=False
    )
    checks["No custom hooksPath"] = custom.returncode == 1
    for name, passed in checks.items():
        print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print("Claude Code 개인/조직 설정은 읽지 않았습니다. /permissions, /hooks로 충돌을 확인하세요.")
    print("실제 .env/인증 파일/환경변수 값은 검사하지 않습니다. Windows는 WSL2 사용.")
    return int(not all(checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
