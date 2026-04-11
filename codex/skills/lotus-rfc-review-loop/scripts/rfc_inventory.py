#!/usr/bin/env python3
"""Generate a normalized RFC inventory scaffold for iterative review loops.

Usage:
  python scripts/rfc_inventory.py --rfc-dir <repo>/docs/RFCs --output <repo>/docs/RFCs/RFC-INDEX.md
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

STATUS_PATTERNS = [
    re.compile(r"\|\s*\*\*Status\*\*\s*\|\s*([^|]+)\|", re.IGNORECASE),
    re.compile(r"^-\s*Status\s*:\s*(.+)$", re.IGNORECASE),
    re.compile(r"^Status\s*:\s*(.+)$", re.IGNORECASE),
]

RFC_ID_RE = re.compile(r"RFC\s*[- ]?([0-9]{3,4}[A-Z]?)", re.IGNORECASE)


@dataclass
class RfcRecord:
    rfc_id: str
    title: str
    file_name: str
    current_doc_status: str


def normalize_rfc_id(text: str) -> str:
    match = RFC_ID_RE.search(text)
    if not match:
        return "RFC-UNPARSED"
    return f"RFC-{match.group(1).upper()}"


def title_from_filename(path: Path) -> str:
    stem = path.stem
    parts = stem.split("-", 1)
    if len(parts) == 2 and re.search(r"\d", parts[0]):
        return parts[1].strip()
    return stem.replace("RFC ", "").strip()


def detect_status(lines: Iterable[str]) -> str:
    for raw in lines:
        line = raw.strip()
        for pattern in STATUS_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group(1).strip().strip("`")
    return "Unknown"


def sort_key(rfc_id: str) -> tuple[int, str]:
    m = re.match(r"RFC-(\d+)([A-Z]?)", rfc_id)
    if not m:
        return (999999, rfc_id)
    return (int(m.group(1)), m.group(2))


def collect_records(rfc_dir: Path) -> list[RfcRecord]:
    records: list[RfcRecord] = []
    for path in sorted(rfc_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        first_lines = text.splitlines()[:40]
        rfc_id = normalize_rfc_id(path.name)
        title = title_from_filename(path)
        status = detect_status(first_lines)
        records.append(RfcRecord(rfc_id=rfc_id, title=title, file_name=path.name, current_doc_status=status))
    records.sort(key=lambda r: sort_key(r.rfc_id))
    return records


def render_markdown(records: list[RfcRecord], rfc_dir: Path) -> str:
    today = date.today().isoformat()
    lines = [
        "# RFC Review Index",
        "",
        f"Generated: `{today}`",
        "",
        "Status vocabulary for review loop:",
        "- Draft",
        "- Approved",
        "- Implemented",
        "- Partially Implemented",
        "- Deprecated",
        "- Archived",
        "",
        "Implementation classification vocabulary:",
        "- Fully implemented and aligned",
        "- Partially implemented (requires enhancement)",
        "- Outdated (requires revision)",
        "- No longer relevant to this repository",
        "",
        "| RFC | Title | Current Doc Status | Review Status | Implementation Classification | Evidence (code/tests/docs) | Next Actions |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for record in records:
        rel = f"docs/RFCs/{record.file_name}"
        lines.append(
            f"| {record.rfc_id} | {record.title} | {record.current_doc_status} | Draft | TBD | TBD | TBD |"
        )

    lines.extend(
        [
            "",
            "## Loop Execution Notes",
            "",
            "- Review in small batches (3-7 RFCs per loop).",
            "- For each RFC, gather concrete evidence from `src/`, `tests/`, OpenAPI contracts, and runbooks.",
            "- Update `Review Status`, `Implementation Classification`, `Evidence`, and `Next Actions` per reviewed RFC.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a normalized RFC review index scaffold.")
    parser.add_argument("--rfc-dir", required=True, type=Path, help="Directory containing RFC markdown files")
    parser.add_argument("--output", required=True, type=Path, help="Output markdown path")
    args = parser.parse_args()

    if not args.rfc_dir.exists() or not args.rfc_dir.is_dir():
        raise SystemExit(f"RFC directory not found: {args.rfc_dir}")

    records = collect_records(args.rfc_dir)
    output = render_markdown(records, args.rfc_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(output, encoding="utf-8")
    print(f"Wrote {len(records)} RFC rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
