from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    path = ROOT / "tests/unit" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_reporting_population_survives_missing_optional_sibling(tmp_path):
    repo = tmp_path / "lotus-platform"
    test = repo / "tests/unit/test_reporting_observability_contract.py"
    test.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "tests/unit" / test.name, test)
    metric = tmp_path / "lotus-render/src/app/render_metrics.py"
    inventories = []
    for present in (False, True):
        if present:
            metric.parent.mkdir(parents=True)
            metric.write_text('METRIC = "lotus_render_test"\n', encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", str(test)],
            cwd=repo, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        inventories.append([line for line in result.stdout.splitlines() if "::test_" in line])
    assert len(inventories[0]) == 8
    assert inventories[0] == inventories[1]


def test_reporting_absence_skips_execution_and_present_drift_fails(tmp_path, monkeypatch):
    module = _load("test_reporting_observability_contract")
    monkeypatch.setattr(module, "RENDER_METRICS_PATH", None)
    with pytest.raises(pytest.skip.Exception, match="not checked out"):
        module.require_render_metrics.__wrapped__()
    metric = tmp_path / "metrics.py"
    metric.write_text('METRIC = "lotus_render_known"\n', encoding="utf-8")
    monkeypatch.setattr(module, "RENDER_METRICS_PATH", metric)
    module.require_render_metrics.__wrapped__()
    monkeypatch.setattr(module, "REPORT_REPO", tmp_path / "report")
    monkeypatch.setattr(module, "ARCHIVE_REPO", tmp_path / "archive")
    for path in (tmp_path / "report/src/app/reporting_metrics.py",
                 tmp_path / "archive/src/app/archive/metrics.py"):
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
    contract = {
        "metrics_catalog": [{"metric_name": "lotus_render_known", "implemented": True,
                             "metric_type": "counter", "cardinality_policy": "bounded-enum-only"}],
        "dashboards": [], "alerts": [],
    }
    monkeypatch.setattr(module, "_load_json", lambda _: contract)
    module.test_reporting_observability_contract_references_only_implemented_metrics()
    metric.write_text('METRIC = "lotus_render_drifted"\n', encoding="utf-8")
    with pytest.raises(AssertionError):
        module.test_reporting_observability_contract_references_only_implemented_metrics()


@pytest.mark.parametrize("available", [(), ("pwsh",), ("powershell",), ("pwsh", "powershell"), ("alias",)])
def test_audit_shell_slots_execute_only_distinct_available_shells(tmp_path, monkeypatch, available):
    module = _load("test_gh_issue_fix_qa_loop")
    paths = {}
    for shell in ("pwsh", "powershell"):
        executable = tmp_path / shell
        executable.write_text("", encoding="utf-8")
        paths[shell] = str(executable) if shell in available else None
    if available == ("alias",):
        paths = dict(pwsh=str(tmp_path / "pwsh"), powershell=str(tmp_path / "pwsh"))
    monkeypatch.setattr(module.shutil, "which", lambda shell: paths.get(shell))
    invoked = []
    def run(script, arguments, env, powershell=None):
        invoked.append(powershell)
        return SimpleNamespace(returncode=0, stderr="", stdout=json.dumps({"issueCount": 3, "violationCount": 0}))
    monkeypatch.setattr(module, "_run_script", run)
    state = tmp_path / "state.json"
    for slot in ("pwsh", "powershell"):
        try:
            executable = module.audit_shell.__wrapped__(SimpleNamespace(param=slot))
        except pytest.skip.Exception as error:
            assert ("unavailable" if paths[slot] is None else "aliases pwsh") in str(error)
            continue
        module.test_audit_accepts_clean_closed_and_open_issue_states((state, None, {}), executable)
    assert invoked == list(dict.fromkeys(path for path in paths.values() if path is not None))


def test_audit_population_has_fixed_named_slots_across_shell_discovery(tmp_path):
    repo = tmp_path / "lotus-platform"
    test = repo / "tests/unit/test_gh_issue_fix_qa_loop.py"
    test.parent.mkdir(parents=True)
    shutil.copyfile(ROOT / "tests/unit" / test.name, test)
    discoveries = [{}, {"pwsh": "/one"}, {"powershell": "/two"},
                   {"pwsh": "/one", "powershell": "/two"},
                   {"pwsh": "/one", "powershell": "/one"}]
    for discovery in discoveries:
        (repo / "conftest.py").write_text(
            "import shutil\noriginal = shutil.which\n"
            "def pytest_sessionstart(session):\n"
            f"    discoveries = {discovery!r}\n"
            "    shutil.which = lambda name: discoveries.get(name) if name in ('pwsh', 'powershell') else original(name)\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", str(test),
             "-k", "test_audit_accepts_clean_closed_and_open_issue_states"],
            cwd=repo, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        nodes = [line.split("::", 1)[1] for line in result.stdout.splitlines() if "::test_" in line]
        assert nodes == ["test_audit_accepts_clean_closed_and_open_issue_states[pwsh]",
                         "test_audit_accepts_clean_closed_and_open_issue_states[powershell]"]
