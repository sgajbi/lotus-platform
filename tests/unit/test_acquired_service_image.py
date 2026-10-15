from __future__ import annotations

import gzip
import importlib.util
import io
import json
import sys
import tarfile
from pathlib import Path

import pytest


PATH = Path(__file__).resolve().parents[2] / "automation" / "verify_acquired_service_image.py"
spec = importlib.util.spec_from_file_location("service_proof", PATH)
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)
CONTAINER_ID = "a" * 64
SELECTED_MAPPINGS = [item for item in proof.policy.load_policy()["container_image_evidence_policy"]["approved_distribution_mappings"]
                     if item.get("original_source_selection_approval") and item["original_repository"] == "docker.io/library/postgres"]
SELECTED_IMAGES = [item["original_repository"] + "@" + item["image_digest"] for item in SELECTED_MAPPINGS]
EXPECTED = SELECTED_IMAGES[0]


def make_export(path, *, engine="classic", fault=None, expected=EXPECTED):
    layers = [b"first layer tar bytes", b"second layer tar bytes"]
    config = {"os": "linux", "architecture": "arm64" if fault == "platform" else "amd64",
              "rootfs": {"type": "layers", "diff_ids": [proof.sha256(layer) for layer in layers]},
              "config": {"Env": ["SHOULD_NOT_RETAIN=secret"]}}
    raw = json.dumps(config).encode()
    config_digest = proof.sha256(raw)
    config_name = "config.json" if engine == "classic" else "blobs/sha256/" + config_digest[7:]
    layer_names = [f"{index}/layer.tar" if engine == "classic" else "blobs/sha256/" + proof.sha256(layer)[7:]
                   for index, layer in enumerate(layers)]
    entry = {"Config": config_name, "Layers": list(layer_names)}
    if fault == "reordered":
        entry["Layers"].reverse()
    if fault == "missing":
        entry["Layers"].pop()
    members = [("manifest.json", json.dumps([entry]).encode()), (config_name, raw + (b" " if fault == "config" else b""))]
    for name, layer in zip(layer_names, layers):
        if fault == "layer":
            layer += b"mutation"
        members.append((name, gzip.compress(layer) if engine == "containerd" else layer))
    with tarfile.open(path, "w", format=tarfile.USTAR_FORMAT) as archive:
        for name, content in members:
            info = tarfile.TarInfo(name)
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))
    image = {"Id": config_digest if engine == "classic" else expected.split("@")[1],
             "Os": "linux", "Architecture": "amd64", "RepoDigests": [expected],
             "RootFS": {"Layers": config["rootfs"]["diff_ids"]}}
    container = {"Id": CONTAINER_ID, "Config": {"Image": expected}, "Image": image["Id"],
                 "State": {"Running": True}}
    return config_digest, image, container


@pytest.mark.parametrize("engine", ["classic", "containerd"])
@pytest.mark.parametrize("expected", SELECTED_IMAGES)
def test_valid_real_export_shapes_hash_config_and_ordered_layers(tmp_path, engine, expected):
    archive = tmp_path / "image.tar"
    config, image, container = make_export(archive, engine=engine, expected=expected)
    proof.verify_service(container, image, CONTAINER_ID, expected)
    result = proof.verify_export(archive, config, image, proof.Budget())
    assert result == {"config_digest": config, "rootfs_diff_ids": image["RootFS"]["Layers"], "platform": "linux/amd64"}
    assert "secret" not in json.dumps(result)
    if engine == "containerd":
        assert image["Id"] != config


@pytest.mark.parametrize("fault", ["config", "platform", "reordered", "missing", "layer", "inspect", "descriptor"])
def test_false_config_platform_or_rootfs_refused(tmp_path, fault):
    archive = tmp_path / "image.tar"
    config, image, _ = make_export(archive, fault=fault)
    if fault == "inspect":
        image["RootFS"]["Layers"].reverse()
    if fault == "descriptor":
        config = proof.sha256(b"unrelated config")
    with pytest.raises(ValueError):
        proof.verify_export(archive, config, image, proof.Budget())


@pytest.mark.parametrize("fault", ["id", "requested-ref", "image-id", "mutable-id", "stopped", "platform", "repodigest"])
def test_unrelated_container_or_cached_image_cannot_substitute(tmp_path, fault):
    _, image, container = make_export(tmp_path / "image.tar")
    if fault == "id": container["Id"] = "b" * 64
    if fault == "requested-ref": container["Config"]["Image"] = "postgres:16"
    if fault == "image-id": container["Image"] = proof.sha256(b"another image")
    if fault == "mutable-id": container["Image"] = "postgres:16"
    if fault == "stopped": container["State"]["Running"] = False
    if fault == "platform": image["Architecture"] = "arm64"
    if fault == "repodigest": image["RepoDigests"] = ["public.ecr.aws/docker/library/postgres@" + EXPECTED.split("@")[1]]
    with pytest.raises(ValueError):
        proof.verify_service(container, image, CONTAINER_ID, EXPECTED)


@pytest.mark.parametrize("fault", ["duplicate", "traversal", "absolute", "backslash", "symlink", "hardlink",
                                   "pax", "gnu-longname", "oversize", "member-count", "truncated", "trailer"])
def test_unsafe_archive_refused_before_unbounded_tar_parsing(tmp_path, monkeypatch, fault):
    archive = tmp_path / "bad.tar"
    with tarfile.open(archive, "w", format=tarfile.USTAR_FORMAT) as writer:
        name = {"traversal": "../outside", "absolute": "/outside", "backslash": "a\\b"}.get(fault, "safe")
        info = tarfile.TarInfo(name)
        info.size = 4
        if fault in ("symlink", "hardlink", "pax", "gnu-longname"):
            info.type = {"symlink": tarfile.SYMTYPE, "hardlink": tarfile.LNKTYPE,
                         "pax": tarfile.XHDTYPE, "gnu-longname": tarfile.GNUTYPE_LONGNAME}[fault]
            info.linkname = "outside"
        writer.addfile(info, io.BytesIO(b"data"))
        if fault == "duplicate": writer.addfile(info, io.BytesIO(b"data"))
    if fault == "oversize": monkeypatch.setattr(proof, "MAX_ARCHIVE_BYTES", 20)
    if fault == "member-count": monkeypatch.setattr(proof, "MAX_MEMBERS", 0)
    if fault == "truncated": archive.write_bytes(archive.read_bytes()[:600])
    if fault == "trailer":
        raw = bytearray(archive.read_bytes())
        raw[-1] = 1
        archive.write_bytes(raw)
    with pytest.raises((ValueError, tarfile.TarError)):
        proof.verify_export(archive, proof.sha256(b"config"), {}, proof.Budget())
    assert not (tmp_path / "outside").exists()


def test_decompression_expansion_and_aggregate_deadline_are_bounded(tmp_path, monkeypatch):
    archive = tmp_path / "image.tar"
    config, image, _ = make_export(archive, engine="containerd")
    monkeypatch.setattr(proof, "MAX_EXPANDED_BYTES", 10)
    with pytest.raises(ValueError, match="expansion"):
        proof.verify_export(archive, config, image, proof.Budget())
    budget = proof.Budget()
    budget.deadline = 0
    with pytest.raises(ValueError, match="deadline"):
        proof.verify_export(archive, config, image, budget)


def test_actual_gzip_bomb_is_stopped_during_layer_read(tmp_path, monkeypatch):
    archive = tmp_path / "compressed.tar"
    payload = b"x" * (3 * 1024**2)
    with tarfile.open(archive, "w", format=tarfile.USTAR_FORMAT) as writer:
        raw = gzip.compress(payload)
        info = tarfile.TarInfo("compressed-layer")
        info.size = len(raw)
        writer.addfile(info, io.BytesIO(raw))
    monkeypatch.setattr(proof, "MAX_EXPANDED_BYTES", 1024)
    with tarfile.open(archive, "r:") as reader:
        exported = proof.Export(reader, proof.Budget())
        with pytest.raises(ValueError, match="expansion"):
            exported.layer_digest("compressed-layer")


@pytest.fixture(params=SELECTED_IMAGES)
def local_service(tmp_path, monkeypatch, request):
    expected = request.param
    archive = tmp_path / "fixture.tar"
    config, image, container = make_export(archive, engine="containerd", expected=expected)
    mapping = dict(proof.admitted_mapping(expected), platform_config_digest=config)
    monkeypatch.setattr(proof, "admitted_mapping", lambda expected: mapping)
    monkeypatch.setattr(proof, "policy_identity", lambda expected, budget: {"commit": expected})
    calls, exports = [], []
    def command(argv, budget, *, artifact=None):
        calls.append(argv)
        assert argv[:3] == ["docker", "--context", "default"]
        if "context" in argv[3:]:
            return json.dumps([{"Endpoints": {"docker": {"Host": "unix:///var/run/docker.sock"}}}]).encode()
        if "save" in argv:
            exports.append(artifact)
            artifact.write_bytes(archive.read_bytes())
            return b""
        return json.dumps([container if "container" in argv else image]).encode()
    monkeypatch.setattr(proof, "command", command)
    return tmp_path, image, container, calls, exports, expected


def test_same_runner_proof_never_pulls_or_substitutes_and_cleans_export(local_service):
    tmp_path, image, _, calls, exports, expected = local_service
    result = proof.verify(CONTAINER_ID, expected, "b" * 40, tmp_path / "proof.json")
    assert result["admitted_index_digest"] == expected.split("@")[1]
    assert len(calls) == 5
    assert calls[2][-1] == image["Id"] and calls[3][-1] == image["Id"]
    assert all(not set(argv).intersection({"pull", "run", "start", "load", "push", "rm", "prune"}) for argv in calls)
    assert all(not path.parent.exists() for path in exports)
    assert result["raw_export_retained"] is False and result["compressed_transfer_verified"] is False
    assert result["cold_acquisition_proven"] is False and result["runtime_execution_verified"] is False
    assert "secret" not in (tmp_path / "proof.json").read_text()


def test_failed_content_proof_cleans_export_and_blocks_consumer(local_service, monkeypatch):
    tmp_path, _, _, _, exports, expected = local_service
    def refuse(*args):
        raise ValueError("bad content")
    monkeypatch.setattr(proof, "verify_export", refuse)
    output = tmp_path / "proof.json"
    result = proof.main(["--container-id", CONTAINER_ID, "--expected-image", expected,
                         "--expected-policy-commit", "b" * 40, "--output", str(output)])
    benchmark = []
    if result == 0: benchmark.append("ran")
    assert result == 1 and benchmark == [] and not output.exists()
    assert all(not path.parent.exists() for path in exports)


def test_replaced_service_after_export_refused(local_service, monkeypatch):
    tmp_path, _, container, calls, _, expected = local_service
    original = proof.command
    def replace(argv, *args, **kwargs):
        if len(calls) == 4:
            container["Config"]["Image"] = "postgres:16"
        return original(argv, *args, **kwargs)
    monkeypatch.setattr(proof, "command", replace)
    with pytest.raises(ValueError, match="binding"):
        proof.verify(CONTAINER_ID, expected, "b" * 40, tmp_path / "proof.json")


@pytest.mark.parametrize("fault", ["nonzero", "capture", "timeout", "export"])
def test_real_offline_subprocess_limits_and_cleanup(tmp_path, monkeypatch, fault):
    monkeypatch.setattr(proof.tempfile, "tempdir", str(tmp_path))
    artifact = None
    code = {"nonzero": "raise SystemExit(7)", "capture": "print('x'*8192)",
            "timeout": "import time; time.sleep(1)", "export": ""}[fault]
    if fault == "capture": monkeypatch.setattr(proof, "MAX_CAPTURE_BYTES", 32)
    if fault == "timeout": monkeypatch.setattr(proof, "COMMAND_SECONDS", 0.01)
    if fault == "export":
        artifact = tmp_path / "owned-export"
        artifact.write_bytes(b"large export")
        monkeypatch.setattr(proof, "MAX_ARCHIVE_BYTES", 2)
    with pytest.raises(ValueError):
        proof.command([sys.executable, "-I", "-B", "-c", code], proof.Budget(), artifact=artifact)
    assert not list(tmp_path.glob("lotus-service-command-*"))


@pytest.mark.parametrize("completion", ["valid", "stdout", "stderr", "export", "command-deadline", "budget-deadline"])
def test_first_completion_poll_rechecks_late_growth_and_deadlines(tmp_path, monkeypatch, completion):
    monkeypatch.setattr(proof.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(proof, "MAX_CAPTURE_BYTES", 8)
    monkeypatch.setattr(proof, "MAX_ARCHIVE_BYTES", 8)
    clock = [0.0]
    monkeypatch.setattr(proof.time, "monotonic", lambda: clock[0])
    artifact = tmp_path / "owned-export" if completion == "export" else None
    calls = {"poll": 0, "wait": 0}

    class CompletesOnFirstPoll:
        returncode = 0

        def __init__(self, argv, **kwargs):
            self.stdout, self.stderr = kwargs["stdout"], kwargs["stderr"]

        def poll(self):
            calls["poll"] += 1
            if calls["poll"] == 1:
                stream = self.stderr if completion == "stderr" else self.stdout
                stream.write(b"x" * 9 if completion in ("stdout", "stderr") else b"ok")
                stream.flush()
                if artifact is not None:
                    artifact.write_bytes(b"x" * 9)
                if completion == "command-deadline": clock[0] = proof.COMMAND_SECONDS + 1
                if completion == "budget-deadline": clock[0] = proof.TOTAL_SECONDS + 1
            return 0

        def wait(self, timeout):
            assert timeout == 5
            calls["wait"] += 1
            return 0

        def kill(self):
            pytest.fail("completed child must not be killed")

    monkeypatch.setattr(proof.subprocess, "Popen", CompletesOnFirstPoll)
    if completion == "valid":
        assert proof.command(["offline-mocked-child"], proof.Budget()) == b"ok"
    else:
        with pytest.raises(ValueError, match="limit|deadline"):
            proof.command(["offline-mocked-child"], proof.Budget(), artifact=artifact)
    assert calls["wait"] == 1
    assert not list(tmp_path.glob("lotus-service-command-*"))


def test_capture_read_is_bounded_even_after_final_stat(tmp_path, monkeypatch):
    monkeypatch.setattr(proof.tempfile, "tempdir", str(tmp_path))
    monkeypatch.setattr(proof, "MAX_CAPTURE_BYTES", 8)
    original_limits = proof._command_limits
    checks = []

    def limits(stdout, stderr, *args):
        original_limits(stdout, stderr, *args)
        checks.append(stdout)
        if len(checks) == 2:
            # Deterministically model growth between the final stat and capture read.
            stdout.write_bytes(b"x" * 32)

    class Completed:
        returncode = 0

        def __init__(self, argv, **kwargs): pass
        def poll(self): return 0
        def wait(self, timeout): return 0

    monkeypatch.setattr(proof, "_command_limits", limits)
    monkeypatch.setattr(proof.subprocess, "Popen", Completed)
    with pytest.raises(ValueError, match="capture limit"):
        proof.command(["offline-mocked-child"], proof.Budget())
    assert len(checks) == 2
    assert not list(tmp_path.glob("lotus-service-command-*"))


def test_policy_authority_requires_clean_exact_source(monkeypatch):
    outputs = iter([b"b" * 40, str(proof.policy.ROOT).encode(), b"?? foreign-file\0"])
    monkeypatch.setattr(proof, "command", lambda *args, **kwargs: next(outputs))
    with pytest.raises(ValueError, match="untracked"):
        proof.policy_identity("b" * 40, proof.Budget())


@pytest.mark.parametrize("mapping", SELECTED_MAPPINGS)
def test_actual_policy_resolves_each_original_postgres_tuple(mapping):
    assert proof.admitted_mapping(mapping["original_repository"] + "@" + mapping["image_digest"]) == mapping


@pytest.mark.parametrize("expected", SELECTED_IMAGES)
@pytest.mark.parametrize("fault", ["approval", "config"])
def test_local_mapping_rechecks_tuple_approval_before_docker(monkeypatch, expected, fault):
    payload = proof.policy.load_policy()
    mappings = payload["container_image_evidence_policy"]["approved_distribution_mappings"]
    selected = next(item for item in mappings if expected == item["original_repository"] + "@" + item["image_digest"])
    other = next(item for item in mappings if item.get("original_source_selection_approval") and item is not selected)
    key = "original_source_selection_approval" if fault == "approval" else "platform_config_digest"
    selected[key] = other[key]
    monkeypatch.setattr(proof.policy, "validate_policy_path", lambda **kwargs: [])
    monkeypatch.setattr(proof.policy, "load_policy", lambda: payload)
    monkeypatch.setattr(proof, "command", lambda *args, **kwargs: pytest.fail("Docker before tuple approval"))
    with pytest.raises(ValueError, match="original-source selection"):
        proof.admitted_mapping(expected)


@pytest.mark.parametrize("expected", [
    "docker.io/library/python@" + proof.policy.ORIGINAL_SOURCE_FALLBACK_IDENTITY[1],
    "docker.io/library/postgres@sha256:" + "0" * 64,
    EXPECTED.replace("docker.io/library", "public.ecr.aws/docker/library"),
    "postgres:17", EXPECTED + "\n",
])
def test_actual_policy_refuses_other_service_references(expected):
    with pytest.raises(ValueError):
        proof.admitted_mapping(expected)


@pytest.mark.parametrize("digest", ["e5290282", "a6e34c59"])
def test_python_selection_approval_does_not_expand_local_postgres_service_proof(monkeypatch, tmp_path, digest):
    mapping = next(item for item in proof.policy.load_policy()["container_image_evidence_policy"]["approved_distribution_mappings"]
                   if item["image_digest"].startswith("sha256:" + digest))
    proof.policy.require_original_selection(mapping)
    expected = mapping["original_repository"] + "@" + mapping["image_digest"]
    monkeypatch.setattr(proof, "policy_identity", lambda *args: {"commit": "b" * 40})
    monkeypatch.setattr(proof, "command", lambda *args, **kwargs: pytest.fail("Docker before PostgreSQL admission"))
    output = tmp_path / "proof.json"
    with pytest.raises(ValueError, match="only original PostgreSQL"):
        proof.verify(CONTAINER_ID, expected, "b" * 40, output)
    assert not output.exists()


@pytest.mark.parametrize("expected", SELECTED_IMAGES)
def test_default_postgres_still_uses_distribution_without_original_request(monkeypatch, expected):
    mapping = proof.admitted_mapping(expected)
    calls = []
    monkeypatch.setattr(proof.policy, "_verify_publisher_distribution", lambda actual, budget: calls.append(actual))
    monkeypatch.setattr(proof.policy, "_verify_official_original", lambda *args: pytest.fail("unexpected original request"))
    assert proof.policy.verify_distribution(mapping) == mapping["distribution_repository"] + "@" + mapping["image_digest"]
    assert calls == [mapping]


def test_policy_bytes_checked_even_when_git_status_is_clean(monkeypatch):
    outputs = iter([b"b" * 40, str(proof.policy.ROOT).encode(), b"", b"tampered committed blob"])
    monkeypatch.setattr(proof, "command", lambda *args, **kwargs: next(outputs))
    with pytest.raises(ValueError, match="bytes differ"):
        proof.policy_identity("b" * 40, proof.Budget())


def test_policy_identity_validates_all_four_committed_blobs(monkeypatch):
    paths = (proof.policy.POLICY_PATH, proof.policy.SCHEMA_PATH, Path(proof.policy.__file__), PATH)
    outputs = iter([b"b" * 40, str(proof.policy.ROOT).encode(), b""] +
                   [path.read_bytes().replace(b"\r\n", b"\n") for path in paths])
    monkeypatch.setattr(proof, "command", lambda *args, **kwargs: next(outputs))
    source = proof.policy_identity("b" * 40, proof.Budget())
    assert source["commit"] == "b" * 40 and len(source["committed_content_sha256"]) == 4


def test_compressed_input_deadline_checked_before_each_read():
    budget = proof.Budget()
    reader = proof.DeadlineReader(io.BytesIO(b"compressed"), budget)
    assert reader.read(2) == b"co"
    budget.deadline = 0
    with pytest.raises(ValueError, match="deadline"):
        reader.read(1)


def test_partial_owned_output_is_removed_and_existing_output_preserved(local_service, monkeypatch):
    tmp_path, _, _, _, _, expected = local_service
    output = tmp_path / "proof.json"
    original = Path.open
    class BrokenWrite:
        def __init__(self, stream): self.stream = stream
        def __enter__(self): return self
        def __exit__(self, *args): self.stream.close()
        def write(self, value):
            self.stream.write(value[:10])
            raise OSError("disk full")
    def opened(path, *args, **kwargs):
        stream = original(path, *args, **kwargs)
        return BrokenWrite(stream) if path == output else stream
    monkeypatch.setattr(Path, "open", opened)
    with pytest.raises(OSError):
        proof.verify(CONTAINER_ID, expected, "b" * 40, output)
    assert not output.exists()
    monkeypatch.setattr(Path, "open", original)
    output.write_text("prior evidence")
    with pytest.raises(ValueError, match="unused"):
        proof.verify(CONTAINER_ID, expected, "b" * 40, output)
    assert output.read_text() == "prior evidence"
