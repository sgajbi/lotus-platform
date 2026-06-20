from __future__ import annotations

import json

from automation.generate_automation_inventory import (
    collect_inventory,
    render_inventory_markdown,
    validate_inventory_surface,
    write_inventory,
)


def test_automation_inventory_collects_scripts_and_classifies_discoverability() -> None:
    inventory = collect_inventory()
    entries = {entry["path"]: entry for entry in inventory["entries"]}

    assert inventory["script_count"] > 0
    assert "automation/New-Lotus-Service.ps1" in entries
    assert "automation/generate_automation_inventory.py" in entries
    assert entries["automation/New-Lotus-Service.ps1"]["classification"] == "covered"
    assert entries["automation/review_analytics_ui_canonical_proof.py"]["reference_count"] > 0


def test_automation_inventory_markdown_surfaces_review_candidates() -> None:
    inventory = collect_inventory()
    markdown = render_inventory_markdown(inventory)

    assert "# Automation Inventory" in markdown
    assert "Lowest-Discoverability Scripts" in markdown
    assert "review" in markdown or "undocumented" in markdown


def test_automation_inventory_artifacts_are_validated(tmp_path, monkeypatch) -> None:
    from automation import generate_automation_inventory as inventory_module

    monkeypatch.setattr(inventory_module, "QUALITY_DIR", tmp_path)
    monkeypatch.setattr(inventory_module, "INVENTORY_JSON", tmp_path / "automation_inventory.json")
    monkeypatch.setattr(inventory_module, "INVENTORY_MD", tmp_path / "automation_inventory.md")

    write_inventory(collect_inventory())

    assert validate_inventory_surface() == []
    payload = json.loads((tmp_path / "automation_inventory.json").read_text(encoding="utf-8"))
    assert payload["entries"]
