from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENTRIES_PATH = ROOT / "platform-stack" / "dev-ingress" / "hosts.example"
DEFAULT_OUTPUT_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
DEFAULT_STAGED_OUTPUT_PATH = ROOT / "output" / "hosts-preview" / "hosts.merged"
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


def _read_existing_hosts(output_path: Path) -> str:
    if not output_path.exists():
        return ""
    return output_path.read_text(encoding="utf-8").replace("\ufeff", "")


def _write_updated_hosts(
    *,
    output_path: Path,
    updated_text: str,
    existing_text: str,
    backup_dir: Path | None,
) -> Path | None:
    backup_path: Path | None = None
    if output_path.exists() and backup_dir is not None:
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = build_backup_path(output_path, backup_dir)
        backup_path.write_text(existing_text, encoding="utf-8")
    output_path.write_text(updated_text, encoding="utf-8")
    return backup_path


def _stage_updated_hosts(
    *, staged_output_path: Path | None, updated_text: str
) -> Path | None:
    if staged_output_path is None:
        return None
    staged_output_path.parent.mkdir(parents=True, exist_ok=True)
    staged_output_path.write_text(updated_text, encoding="utf-8")
    return staged_output_path


def _sync_result(
    *,
    updated_text: str,
    changed: bool,
    backup_path: Path | None,
    staged_output_path: Path | None,
    permission_denied: bool,
) -> dict[str, str | bool | None]:
    return {
        "updated_text": updated_text,
        "changed": changed,
        "backup_path": None if backup_path is None else str(backup_path),
        "staged_output_path": None
        if staged_output_path is None
        else str(staged_output_path),
        "permission_denied": permission_denied,
    }


def sync_dev_ingress_hosts(
    entries_path: Path,
    output_path: Path,
    write: bool,
    backup_dir: Path | None = None,
    staged_output_path: Path | None = None,
) -> dict[str, str | bool | None]:
    entries = _normalize_entries(entries_path.read_text(encoding="utf-8"))
    existing_text = _read_existing_hosts(output_path)
    updated_text = upsert_managed_block(existing_text, entries)
    changed = updated_text != existing_text
    backup_path: Path | None = None
    staged_path: Path | None = None
    permission_denied = False

    if write and changed:
        try:
            backup_path = _write_updated_hosts(
                output_path=output_path,
                updated_text=updated_text,
                existing_text=existing_text,
                backup_dir=backup_dir,
            )
        except PermissionError:
            staged_path = _stage_updated_hosts(
                staged_output_path=staged_output_path,
                updated_text=updated_text,
            )
            permission_denied = True

    return _sync_result(
        updated_text=updated_text,
        changed=changed,
        backup_path=backup_path,
        staged_output_path=staged_path,
        permission_denied=permission_denied,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--entries-path", type=Path, default=DEFAULT_ENTRIES_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--backup-dir", type=Path, default=ROOT / "output" / "hosts-backups")
    parser.add_argument("--staged-output-path", type=Path, default=DEFAULT_STAGED_OUTPUT_PATH)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    result = sync_dev_ingress_hosts(
        entries_path=args.entries_path,
        output_path=args.output_path,
        write=args.write,
        backup_dir=args.backup_dir,
        staged_output_path=args.staged_output_path,
    )

    if args.write:
        if result["permission_denied"]:
            print(f"Permission denied {args.output_path}")
            if result["staged_output_path"]:
                print(f"Staged {result['staged_output_path']}")
            return 1
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
