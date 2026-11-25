"""Git 공유 대상만 복사해 Gitleaks로 검사하며 실제 dotenv는 읽지 않는다."""

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """검사 결과를 종료 코드로 반환한다. 비밀값은 전부 마스킹한다."""
    binary = ROOT / ".tools/bin/gitleaks"
    if not binary.is_file():
        print("FAIL: Gitleaks missing; run scripts/install_tools.py")
        return 1
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    names = set(result.stdout.decode().split("\0")) - {""}
    with tempfile.TemporaryDirectory(prefix="onboarding-scan-") as directory:
        staging = Path(directory)
        for name in names:
            path = Path(name)
            sensitive = (
                any(part in {"secrets", "credentials", "data", ".git"} for part in path.parts)
                or (path.name.startswith(".env") and path.name != ".env.example")
                or path.suffix in {".pem", ".key", ".p12", ".pfx"}
                or path.name in {"credentials.json", "token.json", "tokens.json", ".mcp.json"}
                or path.name.startswith(("client_secret", "service-account"))
            )
            source = ROOT / path
            if sensitive or source.is_symlink() or not source.resolve().is_relative_to(ROOT):
                print("FAIL: forbidden or linked file in Git candidate list (content not read)")
                return 1
            if not source.is_file():
                continue  # Deleted tracked file.
            target = staging / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        return subprocess.run(
            [
                str(binary),
                "dir",
                str(staging),
                "--redact=100",
                "--no-banner",
                "--config",
                str(ROOT / ".gitleaks.toml"),
            ],
            cwd=ROOT,
            check=False,
        ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
