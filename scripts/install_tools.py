"""해시를 고정한 공식 Gitleaks를 프로젝트 로컬에 설치한다."""

import hashlib
import io
import json
import platform
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    """지원하는 OS의 압축 파일을 검증한 뒤 실행 파일 하나만 추출한다."""
    system = platform.system().lower()
    machine = {"x86_64": "x64", "AMD64": "x64", "aarch64": "arm64"}.get(
        platform.machine(), platform.machine()
    )
    key = f"{system}_{machine}"
    manifest = json.loads((ROOT / "scripts/tools.json").read_text())
    expected = manifest["sha256"].get(key)
    if not expected:
        raise SystemExit("Unsupported OS/architecture; use macOS/Linux or WSL2")
    version = manifest["version"]
    url = (
        f"https://github.com/gitleaks/gitleaks/releases/download/v{version}/"
        f"gitleaks_{version}_{key}.tar.gz"
    )
    with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise SystemExit("Gitleaks checksum mismatch")
    target = ROOT / ".tools/bin/gitleaks"
    target.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        member = archive.getmember("gitleaks")
        if not member.isfile():
            raise SystemExit("Invalid Gitleaks archive")
        stream = archive.extractfile(member)
        if stream is None:
            raise SystemExit("Missing Gitleaks binary")
        target.write_bytes(stream.read())
    target.chmod(0o755)
    print("Gitleaks installed locally; SHA256 verified")


if __name__ == "__main__":
    main()
