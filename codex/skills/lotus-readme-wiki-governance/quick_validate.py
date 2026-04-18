from __future__ import annotations

from pathlib import Path
import sys


SKILL_DIR = Path(__file__).resolve().parent
SKILL_FILE = SKILL_DIR / "SKILL.md"

REQUIRED_SNIPPETS = [
    "# Lotus Readme Wiki Governance",
    "## Workflow",
    "## README Standard",
    "## Wiki Standard",
    "## Validation",
    "README.md",
    "wiki/",
]

REQUIRED_RELATIVE_PATHS = [
    "references/lotus-readme-wiki-standard.md",
    "references/lotus-wiki-pages.md",
    "references/github-wiki-publication.md",
]


def main() -> int:
    text = SKILL_FILE.read_text(encoding="utf-8")
    failures: list[str] = []

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in text:
            failures.append(f"missing required snippet: {snippet}")

    for relative_path in REQUIRED_RELATIVE_PATHS:
        target = SKILL_DIR / relative_path
        if not target.exists():
            failures.append(f"missing referenced file: {relative_path}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("OK: lotus-readme-wiki-governance skill structure validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
