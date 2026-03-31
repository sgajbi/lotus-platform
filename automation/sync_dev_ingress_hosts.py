from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENTRIES_PATH = ROOT / "platform-stack" / "dev-ingress" / "hosts.example"
DEFAULT_OUTPUT_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
BLOCK_START = "# >>> lotus-platform dev ingress >>>"
BLOCK_END = "# <<< lotus-platform dev ingress <<<"


def _normalize_entries(text: str) -> list[str]:
    normalized: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.replace("\ufeff", "").strip()
        if not line or line.startswith("#"):
            continue
        normalized.append(" ".join(line.split()))
    return normalized


def render_managed_block(entries: list[str]) -> str:
    lines = [BLOCK_START, *entries, BLOCK_END]
    return "\n".join(lines)


def upsert_managed_block(existing_text: str, entries: list[str]) -> str:
    managed_block = render_managed_block(entries)

    if BLOCK_START in existing_text and BLOCK_END in existing_text:
        start_index = existing_text.index(BLOCK_START)
        end_index = existing_text.index(BLOCK_END) + len(BLOCK_END)
        before = existing_text[:start_index].rstrip()
        after = existing_text[end_index:].lstrip()
        merged_parts = [part for part in (before, managed_block, after) if part]
        return "\n\n".join(merged_parts) + "\n"

    trimmed = existing_text.rstrip()
    if not trimmed:
        return managed_block + "\n"
    return f"{trimmed}\n\n{managed_block}\n"


def build_backup_path(output_path: Path, backup_dir: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return backup_dir / f"{output_path.name}.{timestamp}.bak"


def sync_dev_ingress_hosts(
    entries_path: Path,
    output_path: Path,
    write: bool,
    backup_dir: Path | None = None,
) -> dict[str, str | bool | None]:
    entries = _normalize_entries(entries_path.read_text(encoding="utf-8"))
    existing_text = output_path.read_text(encoding="utf-8").replace("\ufeff", "") if output_path.exists() else ""
    updated_text = upsert_managed_block(existing_text, entries)
    changed = updated_text != existing_text
    backup_path: Path | None = None

    if write and changed:
        if output_path.exists() and backup_dir is not None:
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = build_backup_path(output_path, backup_dir)
            backup_path.write_text(existing_text, encoding="utf-8")
        output_path.write_text(updated_text, encoding="utf-8")

    return {
        "updated_text": updated_text,
        "changed": changed,
        "backup_path": None if backup_path is None else str(backup_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries-path", type=Path, default=DEFAULT_ENTRIES_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--backup-dir", type=Path, default=ROOT / "output" / "hosts-backups")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    result = sync_dev_ingress_hosts(
        entries_path=args.entries_path,
        output_path=args.output_path,
        write=args.write,
        backup_dir=args.backup_dir,
    )

    if args.write:
        if result["changed"]:
            print(f"Updated {args.output_path}")
            if result["backup_path"]:
                print(f"Backup {result['backup_path']}")
        else:
            print(f"No change {args.output_path}")
    else:
        print(result["updated_text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
