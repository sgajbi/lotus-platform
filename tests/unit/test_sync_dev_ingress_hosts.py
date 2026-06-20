from __future__ import annotations

from pathlib import Path

from automation.sync_dev_ingress_hosts import (
    BLOCK_END,
    BLOCK_START,
    sync_dev_ingress_hosts,
    upsert_managed_block,
)


def test_upsert_managed_block_appends_new_block_when_missing() -> None:
    updated = upsert_managed_block("127.0.0.1 localhost\n", ["127.0.0.1 gateway.dev.lotus"])

    assert BLOCK_START in updated
    assert "127.0.0.1 gateway.dev.lotus" in updated
    assert updated.endswith("\n")


def test_upsert_managed_block_replaces_existing_managed_block() -> None:
    existing = (
        "127.0.0.1 localhost\n\n"
        f"{BLOCK_START}\n"
        "127.0.0.1 old.dev.lotus\n"
        f"{BLOCK_END}\n"
    )

    updated = upsert_managed_block(
        existing,
        ["127.0.0.1 gateway.dev.lotus", "127.0.0.1 workbench.dev.lotus"],
    )

    assert "old.dev.lotus" not in updated
    assert updated.count(BLOCK_START) == 1
    assert updated.count(BLOCK_END) == 1
    assert "127.0.0.1 gateway.dev.lotus" in updated


def test_sync_dev_ingress_hosts_writes_managed_block(tmp_path: Path) -> None:
    entries = tmp_path / "hosts.example"
    hosts = tmp_path / "hosts"
    backups = tmp_path / "backups"
    entries.write_text(
        "# comment\n127.0.0.1 gateway.dev.lotus\n127.0.0.1 workbench.dev.lotus\n",
        encoding="utf-8",
    )
    hosts.write_text("127.0.0.1 localhost\n", encoding="utf-8")

    result = sync_dev_ingress_hosts(entries, hosts, write=True, backup_dir=backups)

    written = hosts.read_text(encoding="utf-8")
    assert result["updated_text"] == written
    assert result["changed"] is True
    assert result["backup_path"] is not None
    assert "127.0.0.1 gateway.dev.lotus" in written
    assert "127.0.0.1 workbench.dev.lotus" in written
    assert Path(str(result["backup_path"])).exists()


def test_sync_dev_ingress_hosts_preview_does_not_modify_output_file(tmp_path: Path) -> None:
    entries = tmp_path / "hosts.example"
    hosts = tmp_path / "hosts"
    entries.write_text("127.0.0.1 gateway.dev.lotus\n", encoding="utf-8")
    hosts.write_text("127.0.0.1 localhost\n", encoding="utf-8")

    preview = sync_dev_ingress_hosts(entries, hosts, write=False)

    assert "127.0.0.1 gateway.dev.lotus" in str(preview["updated_text"])
    assert preview["changed"] is True
    assert preview["backup_path"] is None
    assert hosts.read_text(encoding="utf-8") == "127.0.0.1 localhost\n"


def test_sync_dev_ingress_hosts_creates_missing_output_without_backup(tmp_path: Path) -> None:
    entries = tmp_path / "hosts.example"
    hosts = tmp_path / "hosts"
    backups = tmp_path / "backups"
    entries.write_text("127.0.0.1 gateway.dev.lotus\n", encoding="utf-8")

    result = sync_dev_ingress_hosts(entries, hosts, write=True, backup_dir=backups)

    assert result["changed"] is True
    assert result["backup_path"] is None
    assert not backups.exists()
    assert "127.0.0.1 gateway.dev.lotus" in hosts.read_text(encoding="utf-8")


def test_sync_dev_ingress_hosts_skips_backup_when_content_is_already_current(tmp_path: Path) -> None:
    entries = tmp_path / "hosts.example"
    hosts = tmp_path / "hosts"
    backups = tmp_path / "backups"
    current = (
        "127.0.0.1 localhost\n\n"
        f"{BLOCK_START}\n"
        "127.0.0.1 gateway.dev.lotus\n"
        f"{BLOCK_END}\n"
    )
    entries.write_text("127.0.0.1 gateway.dev.lotus\n", encoding="utf-8")
    hosts.write_text(current, encoding="utf-8")

    result = sync_dev_ingress_hosts(entries, hosts, write=True, backup_dir=backups)

    assert result["changed"] is False
    assert result["backup_path"] is None
    assert not backups.exists()


def test_sync_dev_ingress_hosts_stages_output_when_write_is_denied(tmp_path: Path) -> None:
    entries = tmp_path / "hosts.example"
    hosts = tmp_path / "hosts"
    staged = tmp_path / "preview" / "hosts.merged"
    entries.write_text("127.0.0.1 gateway.dev.lotus\n", encoding="utf-8")
    hosts.write_text("127.0.0.1 localhost\n", encoding="utf-8")

    original_write_text = Path.write_text

    def fake_write_text(path: Path, data: str, encoding: str = "utf-8", **kwargs):
        if path == hosts:
            raise PermissionError("denied")
        return original_write_text(path, data, encoding=encoding, **kwargs)

    Path.write_text = fake_write_text  # type: ignore[method-assign]
    try:
        result = sync_dev_ingress_hosts(
            entries,
            hosts,
            write=True,
            backup_dir=tmp_path / "backups",
            staged_output_path=staged,
        )
    finally:
        Path.write_text = original_write_text  # type: ignore[method-assign]

    assert result["permission_denied"] is True
    assert result["staged_output_path"] == str(staged)
    assert staged.exists()
    assert "127.0.0.1 gateway.dev.lotus" in staged.read_text(encoding="utf-8")
