from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_DIR = ROOT / "automation"
if str(AUTOMATION_DIR) not in sys.path:
    sys.path.insert(0, str(AUTOMATION_DIR))

import core_seeded_analytics_maturity_validation as maturity_module  # noqa: E402


def test_seed_reference_visibility_requeues_missing_instruments(monkeypatch):
    config = maturity_module.ValidationConfig(
        ingestion_url="http://ingestion",
        query_url="http://query",
        query_control_plane_url="http://control",
        timeout_seconds=1,
        poll_interval_seconds=0.1,
    )
    accepted: list[tuple[str, dict]] = []

    def _fake_get_json(url: str):
        if "/portfolios?" in url:
            return 200, {"total": 1}
        if "SEC_VISIBLE" in url:
            return 200, {"total": 1}
        return 200, {"total": 0}

    def _fake_ingest(config, endpoint, payload):  # noqa: ARG001
        accepted.append((endpoint, payload))

    monkeypatch.setattr(maturity_module, "_get_json", _fake_get_json)
    monkeypatch.setattr(maturity_module, "_assert_ingest_accepted", _fake_ingest)

    result = maturity_module._wait_for_seed_reference_visibility(
        config=config,
        portfolio_id="PORT_1",
        instrument_ids=["SEC_VISIBLE", "SEC_MISSING"],
        portfolio_payload={"portfolios": []},
        instrument_payload={"instruments": [{"security_id": "SEC_MISSING"}]},
    )

    assert result is None
    assert accepted == [
        ("/ingest/instruments", {"instruments": [{"security_id": "SEC_MISSING"}]})
    ]


def test_seed_reference_visibility_returns_visible_seed(monkeypatch):
    config = maturity_module.ValidationConfig(
        ingestion_url="http://ingestion",
        query_url="http://query",
        query_control_plane_url="http://control",
        timeout_seconds=1,
        poll_interval_seconds=0.1,
    )

    monkeypatch.setattr(maturity_module, "_get_json", lambda _url: (200, {"total": 1}))

    result = maturity_module._wait_for_seed_reference_visibility(
        config=config,
        portfolio_id="PORT_1",
        instrument_ids=["SEC_A", "SEC_B"],
        portfolio_payload={"portfolios": []},
        instrument_payload={"instruments": []},
    )

    assert result == {
        "portfolio_visible": "PORT_1",
        "instrument_ids_visible": ["SEC_A", "SEC_B"],
    }
