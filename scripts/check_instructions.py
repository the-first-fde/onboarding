"""계층 지침의 길이와 로컬 Markdown 참조를 검사한다."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    """공유 문서의 깨진 참조 또는 과도한 CLAUDE.md를 보고한다."""
    errors: list[str] = []
    paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "SECURITY.md", ROOT / "CLAUDE.md"]
    directories = ("docs", ".claude", ".github", "agents", "src", "tests", "scripts", "fixtures")
    for directory in directories:
        paths.extend((ROOT / directory).rglob("*.md"))
    for path in paths:
        content = path.read_text(encoding="utf-8")
        if path.name == "CLAUDE.md":
            if len(content.splitlines()) > 200:
                errors.append(f"Too many instruction lines: {path.relative_to(ROOT)}")
            if not path.with_name("README.md").is_file():
                errors.append(f"Missing companion README.md: {path.relative_to(ROOT)}")
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#")[0]
            if target and not (path.parent / target).exists():
                errors.append(f"Broken link in {path.relative_to(ROOT)}: {target}")
    for error in errors:
        print(error)
    print(f"Instructions/links: {'FAIL' if errors else 'PASS'} ({len(paths)} documents)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
