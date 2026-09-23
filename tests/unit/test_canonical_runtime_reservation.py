from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
from argparse import Namespace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from automation import canonical_runtime_lease as lease
from automation.canonical_runtime_inventory import select_containers, scope_for
from automation.canonical_runtime_reservation import exclusive, transact

NOW = datetime(2026, 9, 15, 5, tzinfo=timezone.utc)
SCOPE = {"projects": {"lotus-core-app-local": "c:/projects/lotus-core",
                      "canonical-ingress": "c:/projects/lotus-platform"},
         "ports": [80, 8202], "sources": {"lotus-core": "a" * 40}}
BINDINGS = [{"kind": "container", "id": "container-immutable-id", "project": "lotus-core-app-local",
             "checkout": "c:/projects/lotus-core", "ports": [8202]}]


def receipt(bindings=BINDINGS, holder="lotus-platform-47"):
    return {"holder": holder, "operator": "explicit-operator", "sourceReceipt": "issue849-handover",
            "scopeDigest": lease.digest(SCOPE), "bindingsDigest": lease.digest(bindings)}


def acquire(book=None, **overrides):
    book = lease.empty_book() if book is None else book
    values = {"holder": "lotus-platform-47", "purpose": "#849/#692 Cycle 6", "scope": copy.deepcopy(SCOPE),
              "bindings": [], "now": NOW, "expires": (NOW + timedelta(hours=2)).isoformat(),
              "reservation_id": "C6-X05"}
    values.update(overrides)
    lease.acquire(book, **values)
    return book


def preflight(book, **overrides):
    values = {"holder": "lotus-platform-47", "scope": SCOPE, "bindings": [], "now": NOW}
    values.update(overrides)
    return lease.preflight(book, **values)


def begin(book, action="change", bindings=None):
    return lease.begin(book, holder="lotus-platform-47", scope=SCOPE, bindings=bindings or [],
                       now=NOW, action=action, token="admitted-token")


def finish(book, bindings=None, outcome="success", token="admitted-token"):
    return lease.finish(book, holder="lotus-platform-47", scope=SCOPE, bindings=bindings or [],
                        now=NOW, token=token, outcome=outcome)


def test_free_acquire_change_and_proved_release_retains_history():
    book = acquire()
    assert preflight(book)["teardownOwner"] == "lotus-platform-47"
    begin(book)
    finish(book, BINDINGS)
    preflight(book, bindings=BINDINGS)
    begin(book, "teardown", BINDINGS)
    assert finish(book)["state"] == "released"
    assert lease.current(book) is None
    assert [event["action"] for event in book["reservations"][0]["events"]] == [
        "acquire", "begin", "finish", "begin", "release",
    ]
    lease.validate_book(book)


@pytest.mark.parametrize("holder", ["", " ", None])
def test_missing_holder_never_manufactures_grant(holder):
    with pytest.raises(lease.ReservationRefusal, match="Explicit holder"):
        acquire(holder=holder)


def test_missing_holder_in_existing_record_refuses():
    book = acquire()
    del book["reservations"][0]["holder"]
    with pytest.raises(lease.ReservationRefusal, match="missing/default holder"):
        preflight(book)


def test_actionable_foreign_holder_refusal():
    with pytest.raises(lease.ReservationRefusal, match=r"lotus-platform-47.*#849/#692.*since.*until"):
        preflight(acquire(), holder="other-agent")


def test_expired_live_requires_named_logged_reclaim_not_automatic_adoption():
    book = acquire(bindings=BINDINGS, receipt=receipt())
    later = NOW + timedelta(hours=3)
    teardown_book = copy.deepcopy(book)
    lease.begin(teardown_book, holder="lotus-platform-47", scope=SCOPE, bindings=BINDINGS,
                now=later, action="teardown", token="expired-owner-teardown")
    assert lease.finish(teardown_book, holder="lotus-platform-47", scope=SCOPE, bindings=[],
                        now=later, token="expired-owner-teardown", outcome="success")["state"] == "released"
    with pytest.raises(lease.ReservationRefusal, match="Expired"):
        preflight(book, bindings=BINDINGS, now=later)
    with pytest.raises(lease.ReservationRefusal, match="handover receipt"):
        acquire(book, reservation_id="next", now=later, expires=(later + timedelta(hours=1)).isoformat(),
                bindings=BINDINGS, reclaim=True)
    acquire(book, reservation_id="next", now=later, expires=(later + timedelta(hours=1)).isoformat(),
            bindings=BINDINGS, reclaim=True, receipt=receipt())
    assert book["reservations"][0]["state"] == "reclaimed"
    assert book["reservations"][0]["events"][-1]["action"] == "reclaim"
    lease.validate_book(book)


def test_unreserved_canonical_resources_require_bound_explicit_handover():
    with pytest.raises(lease.ReservationRefusal, match="handover receipt"):
        acquire(bindings=BINDINGS)
    assert preflight(acquire(bindings=BINDINGS, receipt=receipt()), bindings=BINDINGS)
    with pytest.raises(lease.ReservationRefusal, match="No acquired"):
        preflight(lease.empty_book(), bindings=BINDINGS)


@pytest.mark.parametrize("mutation", ["id", "ports", "scope"])
def test_stale_handover_refuses(mutation):
    old = receipt()
    if mutation == "scope":
        old["scopeDigest"] = "wrong"
    else:
        changed = copy.deepcopy(BINDINGS)
        changed[0][mutation] = "new-id" if mutation == "id" else [80]
        old["bindingsDigest"] = lease.digest(changed)
    with pytest.raises(lease.ReservationRefusal, match="actual resource"):
        acquire(bindings=BINDINGS, receipt=old)


@pytest.mark.parametrize("field,value", [("ports", [80, 8201]), ("sources", {"lotus-core": "b" * 40}),
                                         ("projects", {"lotus-core-app-local": "c:/foreign"})])
def test_scope_change_refuses(field, value):
    scope = copy.deepcopy(SCOPE)
    scope[field] = value
    with pytest.raises(lease.ReservationRefusal, match="differ"):
        preflight(acquire(), scope=scope)


def test_actual_binding_mismatch_refuses():
    with pytest.raises(lease.ReservationRefusal, match="Changed resource"):
        preflight(acquire(), bindings=BINDINGS)
    changed = copy.deepcopy(BINDINGS)
    changed[0]["ports"] = [9999]
    with pytest.raises(lease.ReservationRefusal, match="ports outside"):
        acquire(bindings=changed)


def test_two_overlapping_reservations_refuse():
    book = acquire()
    with pytest.raises(lease.ReservationRefusal, match="no second"):
        acquire(book, reservation_id="second")
    duplicate = copy.deepcopy(book["reservations"][0])
    duplicate["id"], duplicate["events"] = "malformed-second", []
    book["reservations"].append(duplicate)
    with pytest.raises(lease.ReservationRefusal, match="Multiple reservations"):
        preflight(book)


def test_interruption_arbitrary_binding_and_wrong_token_refuse_then_explicit_recovery():
    book = acquire()
    with pytest.raises(lease.ReservationRefusal, match="Matching admitted"):
        finish(book, BINDINGS)
    begin(book)
    with pytest.raises(lease.ReservationRefusal, match="Unfinished"):
        preflight(book)
    assert lease.operation_preflight(book, holder="lotus-platform-47", scope=SCOPE, bindings=BINDINGS,
                                     now=NOW, token="admitted-token")
    with pytest.raises(lease.ReservationRefusal, match="operation token"):
        lease.operation_preflight(book, holder="lotus-platform-47", scope=SCOPE, bindings=BINDINGS,
                                  now=NOW, token="resource-identifier-not-grant")
    with pytest.raises(lease.ReservationRefusal, match="Matching admitted"):
        finish(book, BINDINGS, token="request-path-is-not-authority")
    lease.recover(book, holder="lotus-platform-47", scope=SCOPE, bindings=BINDINGS, now=NOW,
                  receipt=receipt())
    assert preflight(book, bindings=BINDINGS)["events"][-1]["action"] == "recover"


@pytest.mark.parametrize("outcome,bindings", [("failure", []), ("success", BINDINGS)])
def test_failed_or_incomplete_teardown_cannot_release(outcome, bindings):
    book = acquire()
    begin(book, "teardown")
    record = finish(book, bindings, outcome)
    assert record["state"] == "active"
    assert record["events"][-1]["outcome"] == outcome
    assert record["events"][-1]["teardownProved"] is False


def container(project="lotus-core-app-local", root="C:/projects/lotus-core", port=8202):
    return {"Id": "full-docker-id", "Name": "/not-an-authority-grant", "State": {"Running": True}, "Config": {"Labels": {
        "com.docker.compose.project": project, "com.docker.compose.project.working_dir": root,
    }}, "HostConfig": {"PortBindings": {"8000/tcp": [{"HostPort": str(port)}]}}}


def test_incidental_test_container_not_canonical_but_port_collision_is_blocking():
    assert select_containers([container("lotus-unit-pytest-aabb", port=49152)], SCOPE) == []
    created = container("incidental-created-proof")
    created["State"] = {"Running": False, "Status": "created"}
    assert select_containers([created], SCOPE) == []  # Declared but never bound is not a live port claim.
    with pytest.raises(lease.ReservationRefusal, match="Foreign/unproven"):
        select_containers([container("lotus-unit-pytest-aabb")], SCOPE)
    with pytest.raises(lease.ReservationRefusal, match="Foreign/unproven"):
        select_containers([container(root="C:/projects/lotus-core/nested")], SCOPE)


def test_exact_labels_describe_inventory_but_never_admit_holder():
    observed = select_containers([container()], SCOPE)
    assert observed[0]["id"] == "full-docker-id"
    with pytest.raises(lease.ReservationRefusal, match="handover receipt"):
        acquire(bindings=observed)


def test_ingress_name_never_manufactures_checkout_or_holder_authority():
    ingress = container(project="", root="", port=80)
    ingress["Name"] = "/lotus-direct-dev-ingress"
    with pytest.raises(lease.ReservationRefusal, match="Unproven ingress checkout"):
        select_containers([ingress], SCOPE)
    ingress["Mounts"] = [{"Destination": "/etc/caddy/Caddyfile",
                           "Source": "C:/projects/foreign/platform-stack/dev-ingress/Caddyfile.direct-host"}]
    with pytest.raises(lease.ReservationRefusal, match="Unproven ingress checkout"):
        select_containers([ingress], SCOPE)
    ingress["Mounts"][0]["Source"] = "C:/projects/lotus-platform/platform-stack/dev-ingress/Caddyfile.direct-host"
    observed = select_containers([ingress], SCOPE)
    assert observed[0]["checkout"] == SCOPE["projects"]["canonical-ingress"]
    with pytest.raises(lease.ReservationRefusal, match="handover receipt"):
        acquire(bindings=observed)


def test_durable_transaction_refusal_does_not_write_and_lock_is_real(tmp_path):
    path = tmp_path / "reservations.json"
    transact(path, lambda book: acquire(book), write=True)
    before = path.read_bytes()
    with pytest.raises(lease.ReservationRefusal):
        transact(path, lambda book: preflight(book, holder="foreign"), write=True)
    assert path.read_bytes() == before
    with exclusive(path.with_suffix(".lock")):
        result = subprocess.run([sys.executable, "-c", (
            "from pathlib import Path; from automation.canonical_runtime_reservation import exclusive; "
            f"\nwith exclusive(Path({str(path.with_suffix('.lock'))!r})): pass"
        )], capture_output=True, text=True)
        assert result.returncode != 0
        assert "transaction already in progress" in result.stderr
    lease.validate_book(json.loads(path.read_text()))


def test_scope_uses_real_temporary_git_revisions_and_resolved_compose_ports(tmp_path, monkeypatch):
    from automation import canonical_runtime_inventory as inventory
    from automation.canonical_docker_ownership import CANONICAL_REPOSITORIES
    actual_command = inventory.command
    revisions = {}
    for repo in (*CANONICAL_REPOSITORIES, "lotus-platform"):
        root = tmp_path / repo
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                        "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "immutable receipt"], check=True)
        revisions[repo] = actual_command(["git", "rev-parse", "HEAD"], root).strip()
    def controlled_command(arguments, cwd=None):
        if arguments[0] == "docker":
            return json.dumps({"name": cwd.name, "services": {"api": {"ports": [{"published": "8301"}]}}})
        return actual_command(arguments, cwd)
    monkeypatch.setattr(inventory, "command", controlled_command)
    scope = scope_for(tmp_path, tmp_path / "lotus-workbench")
    assert scope["sources"] == revisions
    assert scope["ports"] == [80, 8001, 8111, 8301]  # Host modes plus a formerly omitted Compose port.
    selected = tmp_path / "selected-workbench"
    subprocess.run(["git", "-C", str(tmp_path / "lotus-workbench"), "worktree", "add", "--detach",
                    str(selected)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(selected), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                    "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "selected source"], check=True)
    selected_scope = scope_for(tmp_path, selected)
    assert selected_scope["sources"]["lotus-workbench"] != revisions["lotus-workbench"]
    assert selected_scope["projects"]["lotus-workbench"] == inventory.normalize_docker_path(str(selected))


def test_shipped_powershell_adapter_refuses_missing_holder_before_outbound_io():
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if not shell:
        pytest.fail("PowerShell is required for shipped canonical adapter proof.")
    module = Path(__file__).parents[2] / "automation/CanonicalRuntimeReservation.psm1"
    script = (f"$ErrorActionPreference='Stop'; Import-Module '{module}'; "
              "Enter-CanonicalRuntimeOperation -ProjectsRoot 'nonexistent-workspace'; "
              "Write-Output 'UNAUTHORIZED-MUTATION'")
    result = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True)
    assert result.returncode != 0
    assert "Explicit RuntimeHolder" in result.stderr
    assert "UNAUTHORIZED-MUTATION\n" not in result.stdout


def test_registered_partial_admission_uses_real_selected_git_and_refuses_full_or_missing_selected_proof(tmp_path, monkeypatch, capsys):
    from automation import canonical_runtime_inventory as inventory
    from automation import canonical_runtime_reservation as control
    selected = ("lotus-core", "lotus-manage", "lotus-workbench", "lotus-platform")
    for repo in selected:
        root = tmp_path / repo
        root.mkdir()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test",
                        "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", "immutable receipt"], check=True)
    actual = inventory.command
    compose_calls = []
    def controlled(arguments, cwd=None):
        if arguments[0] == "docker":
            compose_calls.append(cwd.name)
            assert cwd.name in {"lotus-core", "lotus-manage"}
            return json.dumps({"name": cwd.name, "services": {"api": {"ports": [{"published": "8202"}]}}})
        return actual(arguments, cwd)
    monkeypatch.setattr(inventory, "command", controlled)
    monkeypatch.setattr(control, "observe", lambda _: [])
    monkeypatch.setattr(control, "__file__", str(tmp_path / "lotus-platform/automation/canonical_runtime_reservation.py"))
    base = ["reservation", "acquire", "--projects-root", str(tmp_path), "--runtime-mode", "core-manage",
            "--holder", "lotus-platform-47", "--purpose", "#849 selected-mode proof",
            "--expiry-utc", (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()]
    monkeypatch.setattr(sys, "argv", base)
    assert control.main() == 0
    record = json.loads(capsys.readouterr().out)
    assert set(record["scope"]["sources"]) == set(selected)
    assert compose_calls == ["lotus-core", "lotus-manage"]
    assert record["scope"]["ports"] == [80, 8001, 8202]
    assert "lotus-ai" not in record["scope"]["projects"]
    path = tmp_path / "lotus-platform/output/canonical-runtime/reservations.v1.json"
    before = path.read_bytes()
    monkeypatch.setattr(sys, "argv", ["reservation", "preflight", "--projects-root", str(tmp_path),
                                     "--holder", "lotus-platform-47"])
    assert control.main() == 1  # Missing skipped siblings cannot turn partial authority into full authority.
    assert path.read_bytes() == before
    # Removing selected immutable evidence must still refuse even in explicit partial mode.
    subprocess.run(["git", "-C", str(tmp_path / "lotus-manage"), "update-ref", "-d", "HEAD"], check=True)
    monkeypatch.setattr(sys, "argv", ["reservation", "preflight", "--projects-root", str(tmp_path),
                                     "--runtime-mode", "core-manage", "--holder", "lotus-platform-47"])
    assert control.main() == 1
    assert path.read_bytes() == before


def test_authoritative_contract_matches_executable_fields_and_boundaries():
    root = Path(__file__).parents[2]
    contract = json.loads((root / "platform-contracts/runtime/canonical-runtime-reservation.v1.json").read_text())
    assert contract["contractId"] == lease.SCHEMA
    assert set(contract["requiredReservationFields"]) == lease.FIELDS
    assert contract["productionIamImplemented"] is False
    assert contract["implementationOwner"] == "lotus-platform"
    assert contract["consumerOwner"] == "lotus-workbench"
    assert "zero canonical" in contract["release"]
    assert contract["version"] == "1.1.0"
    assert contract["scope"]["modes"] == ["full", "core-manage"]
    assert "registered by Enter" in contract["nestedConsumer"]


def test_malformed_reversed_event_chronology_refuses():
    book = acquire()
    begin(book)
    book["reservations"][0]["events"].reverse()
    with pytest.raises(lease.ReservationRefusal, match="chronology is reversed"):
        lease.validate_book(book)


def test_shipped_control_retains_acquired_scope_for_teardown_not_new_changes(tmp_path, monkeypatch):
    from automation import canonical_runtime_reservation as control
    root = tmp_path / "lotus-platform/automation"
    root.mkdir(parents=True)
    monkeypatch.setattr(control, "__file__", str(root / "canonical_runtime_reservation.py"))
    admitted_scope = copy.deepcopy(SCOPE)
    admitted_scope["projects"]["lotus-workbench"] = str(tmp_path / "lotus-workbench").replace("\\", "/").lower()
    changed = copy.deepcopy(admitted_scope)
    changed["sources"]["lotus-core"] = "b" * 40
    monkeypatch.setattr(control, "scope_for", lambda *_: changed)
    monkeypatch.setattr(control, "observe", lambda _: BINDINGS)
    # Real-time expiry for the actual shipped execute boundary.
    now = datetime.now(timezone.utc)
    book = acquire(scope=admitted_scope, now=now, expires=(now + timedelta(hours=1)).isoformat())
    args = Namespace(projects_root=str(tmp_path), holder="lotus-platform-47", handover_receipt=None,
                     action="begin-change", workbench_repo_path="")
    with pytest.raises(lease.ReservationRefusal, match="sources differ"):
        control.execute(args, book)

    handover = {
        "holder": "lotus-platform-47",
        "operator": "explicit-operator",
        "sourceReceipt": "issue905-reviewed-runtime",
        "scopeDigest": lease.digest(admitted_scope),
        "bindingsDigest": lease.digest(BINDINGS),
    }
    receipt_path = tmp_path / "handover.json"
    receipt_path.write_text(json.dumps({**handover, "bindingsDigest": "wrong"}), encoding="utf-8")
    args.action = "recover"
    args.handover_receipt = str(receipt_path)
    with pytest.raises(lease.ReservationRefusal, match="actual resource identities"):
        control.execute(args, book)
    receipt_path.write_text(json.dumps(handover), encoding="utf-8")
    record = control.execute(args, book)
    assert record["scope"] == admitted_scope
    assert record["bindings"] == BINDINGS
    assert record["events"][-1]["action"] == "recover"

    args.action = "begin-change"
    args.handover_receipt = None
    with pytest.raises(lease.ReservationRefusal, match="sources differ"):
        control.execute(args, book)
    args.action = "begin-teardown"
    record = control.execute(args, book)
    assert record["scope"] == admitted_scope
    assert record["operation"]["action"] == "teardown"
    args.workbench_repo_path = str(tmp_path / "different-workbench")
    with pytest.raises(lease.ReservationRefusal, match="Selected Workbench checkout differs"):
        control.execute(args, book)
    args.workbench_repo_path = ""
    args.action = "finish"
    args.operation_token = record["operation"]["token"]
    args.outcome = "success"
    monkeypatch.setattr(control, "observe", lambda _: [])
    assert control.execute(args, book)["state"] == "released"
    assert lease.current(book) is None


@pytest.mark.parametrize("action", ["preflight", "begin-change", "preflight-operation", "acquire"])
def test_shipped_cli_selects_requested_workbench_before_admission(tmp_path, monkeypatch, action):
    from automation import canonical_runtime_reservation as control
    root = tmp_path / "lotus-platform/automation"
    root.mkdir(parents=True)
    monkeypatch.setattr(control, "__file__", str(root / "canonical_runtime_reservation.py"))
    selected = tmp_path / "selected-workbench"
    class ScopeObserved(Exception):
        pass
    def capture_scope(projects, workbench):
        assert projects == tmp_path
        assert workbench == selected
        raise ScopeObserved
    monkeypatch.setattr(control, "scope_for", capture_scope)
    now = datetime.now(timezone.utc)
    book = acquire(now=now, expires=(now + timedelta(hours=1)).isoformat())
    args = Namespace(projects_root=str(tmp_path), holder="lotus-platform-47", handover_receipt=None,
                     action=action, workbench_repo_path=str(selected))
    with pytest.raises(ScopeObserved):
        control.execute(args, book)


@pytest.mark.parametrize("action", ["recover", "reclaim"])
def test_shipped_cli_recovery_refuses_actual_powershell_whole_operation_lock(tmp_path, monkeypatch, capsys, action):
    from automation import canonical_runtime_reservation as control
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell, "PowerShell is required for cross-language operation-lock proof"
    path = tmp_path / "lotus-platform/output/canonical-runtime/reservations.v1.json"
    transact(path, lambda book: acquire(book), write=True)
    before = path.read_bytes()
    lock = path.parent / "operation.lock"
    script = (f"$f=[System.IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); "
              "try { Write-Output 'LOCKED'; [void][Console]::ReadLine() } finally { $f.Dispose() }")
    process = subprocess.Popen([shell, "-NoProfile", "-Command", script], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
    try:
        assert process.stdout.readline().strip() == "LOCKED"
        monkeypatch.setattr(sys, "argv", ["reservation", action, "--projects-root", str(tmp_path),
                                          "--holder", "lotus-platform-47"])
        assert control.main() == 1
        assert "lock" in capsys.readouterr().out.lower()
        assert path.read_bytes() == before
    finally:
        _, stderr = process.communicate(input="release\n", timeout=15)
        assert process.returncode == 0, stderr


@pytest.mark.parametrize("status", [0, 23])
def test_shipped_publisher_preserves_actual_incoming_native_status(status):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell, "PowerShell is required for native outcome proof"
    module = Path(__file__).parents[2] / "automation/CanonicalRuntimeReservation.psm1"
    script = (f"$ErrorActionPreference='Stop'; Import-Module '{module}'; "
              f"& '{sys.executable}' -c 'import sys; sys.exit({status})'; "
              "function global:python { $global:LASTEXITCODE=0; Write-Output '{}' }; "
              "$op=[pscustomobject]@{ProjectsRoot='controlled-fixture'; Holder='fixture-owner'; "
              "Token='admitted'; Lock=[System.IO.MemoryStream]::new()}; "
              "Exit-CanonicalRuntimeOperation -Operation $op -Outcome failure; "
              f"if ($LASTEXITCODE -ne {status}) {{ throw 'PUBLISHER_MASKED_NATIVE_STATUS' }}; exit 0")
    result = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_shipped_adapter_forwards_selected_workbench_through_begin_and_finish():
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell
    module = Path(__file__).parents[2] / "automation/CanonicalRuntimeReservation.psm1"
    script = (f"$ErrorActionPreference='Stop'; Import-Module '{module}'; "
              "function global:python { "
              "$i=[Array]::IndexOf($args,'--workbench-repo-path'); "
              "if ($i -lt 0 -or $args[$i+1] -ne 'selected-workbench') { throw 'SELECTED_SCOPE_LOST' }; "
              "$global:LASTEXITCODE=0; Write-Output '{}' }; "
              "Invoke-CanonicalReservation -Action begin-change -ProjectsRoot controlled-fixture "
              "-Holder fixture-owner -WorkbenchRepoPath selected-workbench | Out-Null; "
              "$op=[pscustomobject]@{ProjectsRoot='controlled-fixture'; Holder='fixture-owner'; "
              "WorkbenchRepoPath='selected-workbench'; Token='admitted'; Lock=[System.IO.MemoryStream]::new()}; "
              "Exit-CanonicalRuntimeOperation -Operation $op -Outcome failure; exit 0")
    result = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("mode", [
    "missing", "foreign", "contended", "admitted", "cash-denied", "cash-native-failure",
    "cash-error-array", "cash-error-field-array", "cash-invalid-output", "cash-incomplete",
    "cash-array", "cash-wrong-date", "cash-invalid-weight", "cash-inconsistent", "partial",
    "nested-partial", "nested", "nested-absent", "nested-disposed", "nested-foreign",
    "nested-shared", "nested-replacement", "nested-new-process",
])
def test_shipped_dpm_seed_holds_actual_operation_fence_across_writes(tmp_path, mode):
    shell = shutil.which("pwsh") or shutil.which("powershell")
    assert shell
    root = Path(__file__).parents[2]
    workspace = tmp_path / "workspace"
    lock = workspace / "lotus-platform/output/canonical-runtime/operation.lock"
    lock.parent.mkdir(parents=True)
    holder = "" if mode == "missing" else mode
    script = f"""
$ErrorActionPreference='Stop'
$global:proofWriteUris=@()
$parentFence=$null
if ('{mode}' -in @('nested-disposed','nested-foreign','nested-shared','nested-new-process')) {{
  $fencePath=if ('{mode}' -eq 'nested-foreign') {{ '{tmp_path / 'foreign.lock'}' }} else {{ '{lock}' }}
  $share=if ('{mode}' -eq 'nested-shared') {{ 'ReadWrite' }} else {{ 'None' }}
  $parentFence=[IO.File]::Open($fencePath,'OpenOrCreate','ReadWrite',$share)
  if ('{mode}' -eq 'nested-disposed') {{ $parentFence.Dispose() }}
}}
function global:python {{
  $global:LASTEXITCODE=0
  if ($args[0] -like '*canonical_runtime_reservation.py') {{
    if ($args[1] -eq 'preflight-operation') {{
      $token=$args[[Array]::IndexOf($args,'--operation-token')+1]
      if ($token -ne 'admitted-dpm') {{ throw 'NESTED_AUTHORITY_CHANGED' }}
      Write-Host 'NESTED_SOURCE_ADMITTED'; return '{{}}'
    }}
    if ($args[1] -eq 'begin-change') {{
      if ('{mode}' -eq 'foreign') {{ $global:LASTEXITCODE=1; return 'CONTROLLED_FOREIGN_HOLDER_REFUSAL' }}
      return '{{"operation":{{"token":"admitted-dpm"}},"bindings":[]}}'
    }}
    $outcome=$args[[Array]::IndexOf($args,'--outcome')+1]
    $count=@($global:proofWriteUris | Select-Object -Unique).Count
    if ($outcome -ne 'failure') {{ throw 'FALSE_DPM_OUTCOME' }}
    Write-Host "FENCED_DPM_WRITES=$count;OUTCOME=$outcome"
    return '{{}}'
  }}
  if ($args -contains '--validate-caller-only') {{ return '{{"state":"caller_scope_validated","network_performed":false}}' }}
  if ($args -notcontains '--caller-tenant-id=tenant-sg') {{ throw 'CALLER_FENCE_LOST' }}
  if ('{mode}' -eq 'cash-denied') {{ $global:LASTEXITCODE=1; return '{{"error_code":"CANONICAL_CASH_SOURCE_HTTP_403"}}' }}
  if ('{mode}' -eq 'cash-native-failure') {{ $global:LASTEXITCODE=23; return 'PRIVATE CHILD OUTPUT' }}
  if ('{mode}' -eq 'cash-error-array') {{ $global:LASTEXITCODE=1; return '[{{"error_code":"CANONICAL_CASH_SOURCE_HTTP_403"}},{{"error_code":"PRIVATE CHILD OUTPUT"}}]' }}
  if ('{mode}' -eq 'cash-error-field-array') {{ $global:LASTEXITCODE=1; return '{{"error_code":["CANONICAL_CASH_SOURCE_HTTP_403","PRIVATE CHILD OUTPUT"]}}' }}
  if ('{mode}' -eq 'cash-invalid-output') {{ return '{{"state":"failed"}}' }}
  if ('{mode}' -eq 'cash-incomplete') {{ return '{{"state":"ready"}}' }}
  $cash=@{{state='ready'; source_service='lotus-gateway'; source_contract='WorkbenchOverviewResponse';
    source_uri='http://gateway.dev.lotus/api/v1/workbench/PB_SG_GLOBAL_BAL_001/overview?as_of_date=2026-04-10&include_performance_snapshot=false&include_rebalance_snapshot=false';
    portfolio_id='PB_SG_GLOBAL_BAL_001'; requested_as_of_date='2026-04-10'; resolved_as_of_date='2026-04-10';
    effective_as_of_date='2026-04-10'; cash_weight_pct='10'; normalized_cash_weight='0.10'}}
  if ('{mode}' -eq 'cash-wrong-date') {{ $cash.effective_as_of_date='2026-04-09' }}
  if ('{mode}' -eq 'cash-invalid-weight') {{ $cash.normalized_cash_weight='NaN' }}
  if ('{mode}' -eq 'cash-inconsistent') {{ $cash.cash_weight_pct='50' }}
  $json=$cash | ConvertTo-Json -Compress
  if ('{mode}' -eq 'cash-array') {{ return "[$json]" }}
  return $json
}}
function global:Start-Sleep {{ param($Seconds) }}
function global:Invoke-RestMethod {{
  param($Method,$Uri,$Headers,$TimeoutSec,$ContentType,$Body)
  $contended=$false
  try {{ $f=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); $f.Dispose() }}
  catch [IO.IOException] {{ $contended=$true }}
  if (-not $contended) {{ throw 'DPM_WRITE_OUTSIDE_OPERATION_FENCE' }}
  if ($Body -like '*not-a-date*') {{
    $e=[Exception]::new('side-effect-free probe'); $e | Add-Member NoteProperty Response @{{StatusCode=422}}; throw $e
  }}
  $global:proofWriteUris += $Uri
  if (@($global:proofWriteUris | Select-Object -Unique).Count -eq 2) {{
    if ('{mode}' -eq 'nested') {{ Write-Host 'NESTED_FENCED_DPM_ROUTES=2' }}
    throw 'CONTROLLED_SECOND_WRITE_FAILURE'
  }}
  return @{{mandate=@{{}}}}
}}
try {{
  if ('{mode}' -in @('nested','nested-replacement','nested-partial')) {{
    Import-Module '{root / 'automation/CanonicalRuntimeReservation.psm1'}'
    $parent=Enter-CanonicalRuntimeOperation -ProjectsRoot '{workspace}' -WorkbenchRepoPath 'selected-workbench' -Holder '{holder}' -RuntimeMode '{"core-manage" if mode == "nested-partial" else "full"}'
    $parentFence=$parent.Lock
    if ('{mode}' -eq 'nested-replacement') {{
      $parentFence.Dispose()
      $parentFence=[IO.File]::Open('{lock}','Open','ReadWrite','None')
    }}
  }}
  & '{root / 'automation/Invoke-DpmCommandCenterSeed.ps1'}' -ProjectsRoot '{workspace}' `
    -WorkbenchRepoPath 'selected-workbench' -RuntimeHolder '{holder}' -OutputDirectory '{tmp_path / 'evidence'}' -SkipGatewayValidation -RuntimeMode '{"core-manage" if mode in {"partial", "nested-partial"} else "full"}' {"-RuntimeOperationToken admitted-dpm -RuntimeOperationFence $parentFence" if mode.startswith("nested") else ""}
  exit $LASTEXITCODE
}} finally {{ if ($parentFence) {{ $parentFence.Dispose() }} }}
"""
    fence = None
    if mode == "contended":
        fence = subprocess.Popen([shell, "-NoProfile", "-Command",
                                  f"$f=[IO.File]::Open('{lock}','OpenOrCreate','ReadWrite','None'); "
                                  "try { Write-Output 'LOCKED'; [void][Console]::ReadLine() } finally { $f.Dispose() }"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        assert fence.stdout.readline().strip() == "LOCKED"
    try:
        result = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=30)
        assert result.returncode == 1, result.stdout + result.stderr
        summary = json.loads((tmp_path / "evidence/dpm-command-center-seed-latest.json").read_text())
        assert summary["status"] == "failed"
        if mode == "admitted":
            assert "FENCED_DPM_WRITES=2;OUTCOME=failure" in result.stdout, result.stdout + result.stderr
            assert "CONTROLLED_SECOND_WRITE_FAILURE" in summary["error"]
        elif mode.startswith("cash-"):
            assert "FENCED_DPM_WRITES=0;OUTCOME=failure" in result.stdout
            assert summary["refresh_response"] is None
            assert summary["steps"] == ["manage-refresh-authorization-preflight"]
            expected = {"cash-denied": "CANONICAL_CASH_SOURCE_HTTP_403",
                        "cash-native-failure": "CANONICAL_CASH_RESOLVER_FAILED",
                        "cash-error-array": "CANONICAL_CASH_RESOLVER_FAILED",
                        "cash-error-field-array": "CANONICAL_CASH_RESOLVER_FAILED",
                        "cash-invalid-output": "CANONICAL_CASH_RESOLVER_INVALID_OUTPUT"}.get(mode, "CANONICAL_CASH_RESOLVER_INVALID_OUTPUT")
            assert expected in summary["error"]
            assert "PRIVATE CHILD OUTPUT" not in json.dumps(summary)
        elif mode == "nested":
            assert "CONTROLLED_SECOND_WRITE_FAILURE" in summary["error"], json.dumps(summary)
            assert "NESTED_SOURCE_ADMITTED" in result.stdout
            assert "NESTED_FENCED_DPM_ROUTES=2" in result.stdout
            assert "FENCED_DPM_WRITES" not in result.stdout  # Caller owns finish, not this child.
            assert "CONTROLLED_SECOND_WRITE_FAILURE" in summary["error"]
        else:
            assert "FENCED_DPM_WRITES" not in result.stdout
            assert "NESTED_SOURCE_ADMITTED" not in result.stdout
            assert summary["steps"] == []
            if mode in {"partial", "nested-partial"}:
                assert "requires a full canonical reservation" in summary["error"]
            elif mode.startswith("nested"):
                assert "live canonical parent operation fence" in summary["error"]
    finally:
        if fence:
            _, stderr = fence.communicate(input="release\n", timeout=15)
            assert fence.returncode == 0, stderr
