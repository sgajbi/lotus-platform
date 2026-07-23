from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_automation_module(module_name: str):
    automation_path = str(ROOT / "automation")
    if automation_path not in sys.path:
        sys.path.insert(0, automation_path)
    module_path = ROOT / "automation" / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_mesh_maturity_scope_is_shared_across_certification_automation() -> None:
    scope = _load_automation_module("mesh_maturity_scope")
    collect = _load_automation_module("collect_trust_telemetry")
    slo = _load_automation_module("validate_mesh_slo_policies")
    access = _load_automation_module("validate_mesh_access_policies")
    evidence = _load_automation_module("generate_mesh_evidence_pack")
    gate = _load_automation_module("mesh_certification_gate")
    matrix = _load_automation_module("generate_enterprise_mesh_maturity_matrix")

    assert scope.REQUIRED_PRODUCTS == {
        "lotus-core:PortfolioStateSnapshot:v1": "lotus-core",
        "lotus-core:DpmSourceReadiness:v1": "lotus-core",
        "lotus-performance:ReturnsSeriesBundle:v1": "lotus-performance",
        "lotus-risk:RiskMetricsReport:v1": "lotus-risk",
        "lotus-advise:AdvisoryProposalLifecycleRecord:v1": "lotus-advise",
        "lotus-advise:AdvisoryProposalMemoEvidencePack:v1": "lotus-advise",
        "lotus-report:ClientReportEvidencePack:v1": "lotus-report",
        "lotus-manage:PortfolioActionRegister:v1": "lotus-manage",
    }
    assert scope.CERTIFICATION_CANDIDATE_PRODUCT_IDS == {
        "lotus-idea:IdeaCandidate:v1"
    }
    assert "lotus-idea:IdeaCandidate:v1" not in scope.REQUIRED_PRODUCTS

    assert collect.REQUIRED_PRODUCTS is scope.REQUIRED_PRODUCTS
    assert slo.REQUIRED_PRODUCTS is scope.REQUIRED_PRODUCTS
    assert access.REQUIRED_PRODUCTS is scope.REQUIRED_PRODUCTS
    assert evidence.REQUIRED_PRODUCTS is scope.REQUIRED_PRODUCTS
    assert gate.REQUIRED_PRODUCTS is scope.REQUIRED_PRODUCTS
    assert matrix.FIRST_WAVE_PRODUCTS == set(scope.REQUIRED_PRODUCT_IDS)
    assert matrix.CERTIFICATION_CANDIDATE_PRODUCTS == set(
        scope.CERTIFICATION_CANDIDATE_PRODUCT_IDS
    )


def test_mesh_maturity_scope_default_telemetry_directories_follow_required_repos() -> (
    None
):
    scope = _load_automation_module("mesh_maturity_scope")
    projects_root = ROOT.parent

    assert [
        path.relative_to(projects_root).as_posix()
        for path in scope.default_static_telemetry_directories()
    ] == [
        "lotus-core/contracts/trust-telemetry",
        "lotus-performance/contracts/trust-telemetry",
        "lotus-risk/contracts/trust-telemetry",
        "lotus-advise/contracts/trust-telemetry",
        "lotus-report/contracts/trust-telemetry",
        "lotus-manage/contracts/trust-telemetry",
    ]
    assert [
        path.relative_to(projects_root).as_posix()
        for path in scope.default_runtime_telemetry_directories()
    ] == [
        "lotus-core/output/trust-telemetry/runtime",
        "lotus-performance/output/trust-telemetry/runtime",
        "lotus-risk/output/trust-telemetry/runtime",
        "lotus-advise/output/trust-telemetry/runtime",
        "lotus-report/output/trust-telemetry/runtime",
        "lotus-manage/output/trust-telemetry/runtime",
    ]
