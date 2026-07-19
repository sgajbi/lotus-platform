from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AUDITOR_PATH = (
    ROOT
    / "codex"
    / "skills"
    / "lotus-app-issue-discovery"
    / "scripts"
    / "audit_rfc_issue_coverage.py"
)


def _load_auditor_module():
    spec = importlib.util.spec_from_file_location("audit_rfc_issue_coverage", AUDITOR_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_auditor_extracts_nested_issue_expectations_and_required_labels(tmp_path: Path) -> None:
    auditor = _load_auditor_module()
    contract_path = tmp_path / "contract.json"
    _write_json(
        contract_path,
        {
            "rfc": "RFC-0042",
            "ownedCapabilities": [
                {
                    "capability": "advisor opportunity queue",
                    "sliceIds": ["RFC-0042/slice-03", "RFC-0042/slice-07"],
                    "issues": [
                        {
                            "repository": "sgajbi/lotus-idea",
                            "number": 10,
                            "url": "https://github.com/sgajbi/lotus-idea/issues/10",
                        }
                    ],
                }
            ],
        },
    )

    rfc, expectations = auditor.load_issue_expectations(contract_path)

    assert rfc == "RFC-0042"
    assert len(expectations) == 1
    expectation = expectations[0]
    assert expectation.repository == "sgajbi/lotus-idea"
    assert expectation.number == 10
    assert expectation.required_labels == (
        "rfc/RFC-0042",
        "rfc/RFC-0042/slice-03",
        "rfc/RFC-0042/slice-07",
    )
    assert expectation.source_name == "advisor opportunity queue"


def test_auditor_reports_missing_labels_and_reviewable_gh_commands(tmp_path: Path) -> None:
    auditor = _load_auditor_module()
    contract_path = tmp_path / "contract.json"
    issues_path = tmp_path / "issues.json"
    _write_json(
        contract_path,
        {
            "rfc": "RFC-0002",
            "targetOpportunityFamilies": [
                {
                    "family": "high volatility / drawdown review",
                    "sliceIds": ["RFC-0002/slice-16", "RFC-0002/slice-17"],
                    "issues": [
                        {
                            "repository": "sgajbi/lotus-risk",
                            "number": 211,
                            "url": "https://github.com/sgajbi/lotus-risk/issues/211",
                        }
                    ],
                }
            ],
        },
    )
    _write_json(
        issues_path,
        [
            {
                "repository": "sgajbi/lotus-risk",
                "number": 211,
                "state": "OPEN",
                "title": "Certify volatility source receipts",
                "url": "https://github.com/sgajbi/lotus-risk/issues/211",
                "labels": ["rfc/RFC-0002", "status/blocked", "priority/P0"],
            }
        ],
    )

    rfc, expectations = auditor.load_issue_expectations(contract_path)
    snapshots = auditor.load_issue_snapshots_from_json(issues_path)
    audit = auditor.audit_issue_coverage(contract_path, expectations, snapshots, rfc)
    markdown = auditor.render_markdown(audit)

    assert audit.has_failures is True
    assert audit.missing_label_issues == 1
    assert audit.records[0].missing_labels == (
        "rfc/RFC-0002/slice-16",
        "rfc/RFC-0002/slice-17",
    )
    assert audit.records[0].status_labels == ("status/blocked",)
    assert audit.records[0].priority_labels == ("priority/P0",)
    assert audit.records[0].duplicate_posture == "active"
    assert (
        'gh issue edit 211 --repo sgajbi/lotus-risk --add-label "rfc/RFC-0002/slice-16"'
        in markdown
    )


def test_auditor_distinguishes_missing_issues_and_duplicate_contract_references(tmp_path: Path) -> None:
    auditor = _load_auditor_module()
    contract_path = tmp_path / "contract.json"
    issues_path = tmp_path / "issues.json"
    _write_json(
        contract_path,
        {
            "rfcId": "RFC-0099",
            "sections": [
                {
                    "name": "report handoff",
                    "sliceIds": ["RFC-0099/slice-12"],
                    "issues": [{"repository": "sgajbi/lotus-report", "number": 77}],
                },
                {
                    "name": "archive handoff",
                    "sliceIds": ["RFC-0099/slice-13"],
                    "issues": [{"repository": "sgajbi/lotus-report", "number": 77}],
                },
                {
                    "name": "render handoff",
                    "sliceIds": ["RFC-0099/slice-13"],
                    "issues": [{"repository": "sgajbi/lotus-render", "number": 78}],
                },
            ],
        },
    )
    _write_json(
        issues_path,
        [
            {
                "repository": "sgajbi/lotus-report",
                "number": 77,
                "state": "CLOSED",
                "title": "Superseded report proof issue",
                "labels": [
                    "rfc/RFC-0099",
                    "rfc/RFC-0099/slice-12",
                    "rfc/RFC-0099/slice-13",
                    "priority/P1",
                ],
            }
        ],
    )

    rfc, expectations = auditor.load_issue_expectations(contract_path)
    snapshots = auditor.load_issue_snapshots_from_json(issues_path)
    audit = auditor.audit_issue_coverage(contract_path, expectations, snapshots, rfc)
    records = {f"{record.repository}#{record.number}": record for record in audit.records}

    assert audit.missing_issues == 1
    assert audit.duplicate_contract_references == ("sgajbi/lotus-report#77",)
    assert records["sgajbi/lotus-report#77"].duplicate_posture == "superseded"
    assert records["sgajbi/lotus-report#77"].state == "CLOSED"
    assert records["sgajbi/lotus-render#78"].exists is False
    assert records["sgajbi/lotus-render#78"].status == "missing_issue"
