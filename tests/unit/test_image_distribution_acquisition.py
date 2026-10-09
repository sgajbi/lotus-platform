from __future__ import annotations

import hashlib
import io
import json
from urllib.error import HTTPError

import pytest

from test_technology_governance_policy import _policy, _validator
from pathlib import Path
import yaml


def _mapping():
    return _policy()["container_image_evidence_policy"][
        "approved_distribution_mappings"
    ][1]


def _arguments(mapping):
    return [
        "--source-image",
        mapping["original_repository"] + "@" + mapping["image_digest"],
        "--distribution-image",
        mapping["distribution_repository"] + "@" + mapping["image_digest"],
        "--platform",
        mapping["platform"],
    ]


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4, 5])
def test_each_admitted_mapping_resolves(index):
    mapping = _policy()["container_image_evidence_policy"][
        "approved_distribution_mappings"
    ][index]
    args = _arguments(mapping)
    assert (
        _validator().resolve_distribution(_policy(), args[1], args[3], args[5])
        == mapping
    )


@pytest.mark.parametrize(
    "position,value",
    [
        (1, ""),
        (3, "public.ecr.aws/docker/library/python:3.12-slim"),
        (3, "public.ecr.aws/other/python@" + "sha256:" + "0" * 64),
        (5, "linux/arm64"),
        (1, "docker.io/library/postgres@" + "sha256:" + "0" * 64),
    ],
)
def test_unadmitted_tuple_refused(position, value):
    args = _arguments(_mapping())
    args[position] = value
    with pytest.raises(ValueError, match="not uniquely admitted"):
        _validator().resolve_distribution(_policy(), args[1], args[3], args[5])


def _manifest_fixture():
    # Independent small OCI objects exercise byte hashing and child selection, not registry I/O.
    child = json.dumps(
        {
            "schemaVersion": 2,
            "config": {"digest": "sha256:" + "1" * 64},
            "layers": [{"digest": "sha256:" + "2" * 64}],
        }
    ).encode()
    child_digest = "sha256:" + hashlib.sha256(child).hexdigest()
    index = json.dumps(
        {
            "schemaVersion": 2,
            "manifests": [
                {
                    "digest": child_digest,
                    "platform": {"os": "linux", "architecture": "amd64"},
                }
            ],
        }
    ).encode()
    mapping = _mapping()
    mapping["image_digest"] = "sha256:" + hashlib.sha256(index).hexdigest()
    mapping["platform_manifest_digest"] = child_digest
    return mapping, index, child


@pytest.mark.parametrize("header", [False, True])
def test_live_manifest_check_accepts_matching_index_and_child(monkeypatch, header):
    validator = _validator()
    mapping, index, child = _manifest_fixture()
    calls = []

    def request(url, headers, *, timeout=20):
        calls.append(url)
        if "/token/" in url:
            return b'{"token":"ephemeral-test-token"}', {}
        raw = index if url.endswith(mapping["image_digest"]) else child
        return raw, {
            "Docker-Content-Digest": "sha256:" + hashlib.sha256(raw).hexdigest()
        } if header else {}

    monkeypatch.setattr(validator, "_registry_json", request)
    validator.verify_distribution(mapping)
    assert len(calls) == 3
    assert all("/blobs/" not in url for url in calls)


@pytest.mark.parametrize(
    "fault",
    [
        "body",
        "header",
        "child",
        "platform",
        "missing-token",
        "unavailable",
        "rate-limited",
    ],
)
def test_live_manifest_check_refuses_content_and_availability_faults(
    monkeypatch, fault
):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, index, child = _manifest_fixture()
    if fault == "platform":
        index = index.replace(b"amd64", b"arm64")
        mapping["image_digest"] = "sha256:" + hashlib.sha256(index).hexdigest()
    if fault == "child":
        mapping["platform_manifest_digest"] = "sha256:" + "0" * 64

    def request(url, headers, *, timeout=20):
        if fault in ("unavailable", "rate-limited"):
            raise HTTPError(
                url, 503 if fault == "unavailable" else 429, "unavailable", {}, None
            )
        if "/token/" in url:
            return b"{}" if fault == "missing-token" else b'{"token":"test"}', {}
        raw = index if url.endswith(mapping["image_digest"]) else child
        return (raw + b" " if fault == "body" else raw), (
            {"Docker-Content-Digest": "sha256:" + "f" * 64} if fault == "header" else {}
        )

    monkeypatch.setattr(validator, "_registry_json", request)
    with pytest.raises((ValueError, OSError)):
        validator.verify_distribution(mapping)


def test_acquisition_cannot_suppress_findings_or_emit_unverified_output(tmp_path):
    validator = _validator()
    with pytest.raises(SystemExit) as suppressed:
        validator.main(_arguments(_mapping()) + ["--report-only"])
    assert suppressed.value.code == 2
    with pytest.raises(SystemExit) as unverified:
        validator.main(
            _arguments(_mapping()) + ["--github-output", str(tmp_path / "output")]
        )
    assert unverified.value.code == 2
    assert not (tmp_path / "output").exists()


def test_failed_live_check_emits_no_service_output(monkeypatch, tmp_path):
    validator = _validator()
    monkeypatch.setattr(
        validator,
        "verify_distribution",
        lambda mapping: (_ for _ in ()).throw(OSError("offline")),
    )
    output = tmp_path / "output"
    assert (
        validator.main(
            _arguments(_mapping())
            + ["--verify-distribution", "--github-output", str(output)]
        )
        == 1
    )
    assert not output.exists()


def test_successful_live_check_exports_only_admitted_image(monkeypatch, tmp_path):
    validator = _validator()
    monkeypatch.setattr(validator, "verify_distribution", lambda mapping: None)
    output = tmp_path / "output"
    args = _arguments(_mapping())
    assert (
        validator.main(args + ["--verify-distribution", "--github-output", str(output)])
        == 0
    )
    assert output.read_text() == f"image={args[3]}\n"


def test_acquisition_still_refuses_expired_explicit_operational_register(
    monkeypatch, tmp_path
):
    validator = _validator()
    calls = []
    monkeypatch.setattr(
        validator, "verify_distribution", lambda mapping: calls.append(mapping)
    )
    register = (
        Path(__file__).resolve().parents[2]
        / "platform-contracts/vulnerability-exceptions/examples/lotus-platform-vulnerability-exception-register.valid.json"
    )
    output = tmp_path / "output"
    assert (
        validator.main(
            _arguments(_mapping())
            + [
                "--verify-distribution",
                "--github-output",
                str(output),
                "--exception-register",
                str(register),
                "--as-of-date",
                "2026-10-10",
            ]
        )
        == 1
    )
    assert calls == []
    assert not output.exists()


def test_prerequisite_template_checks_before_export_and_has_no_services():
    root = Path(__file__).resolve().parents[2]
    template = yaml.safe_load(
        (
            root
            / "platform-standards/templates/workflows/image-acquisition.backend.template.yml"
        ).read_text()
    )
    job = template["jobs"]["image-acquisition"]
    assert "services" not in job and "container" not in job
    assert job["outputs"]["image"] == "${{ steps.admission.outputs.image }}"
    steps = job["steps"]
    assert "^[0-9a-f]{40}$" in steps[0]["run"]
    assert steps[1]["with"]["ref"] == "${{ vars.LOTUS_PLATFORM_GOVERNANCE_SHA }}"
    admission = next(step for step in steps if step.get("id") == "admission")
    assert admission["id"] == "admission"
    assert "--verify-distribution" in admission["run"]
    assert '--github-output "$GITHUB_OUTPUT"' in admission["run"]
    assert "continue-on-error" not in admission


@pytest.mark.parametrize(
    "fault", ["empty", "duplicate", "publisher", "kind", "approval"]
)
def test_mapping_policy_fails_closed(fault):
    policy = _policy()
    mappings = policy["container_image_evidence_policy"][
        "approved_distribution_mappings"
    ]
    if fault == "empty":
        mappings.clear()
    elif fault == "duplicate":
        mappings.append(mappings[0].copy())
    elif fault == "publisher":
        mappings[0]["distribution_repository"] = (
            "public.ecr.aws/docker/library/postgres"
        )
    elif fault == "kind":
        mappings[0]["manifest_kind"] = "index"
    else:
        del mappings[0]["approval"]
    assert _validator().validate_policy(policy)


def _mock_budget_clock(monkeypatch, validator):
    elapsed = [0.0]
    waits = []
    monkeypatch.setattr(validator.time, "monotonic", lambda: elapsed[0])
    monkeypatch.setattr(validator.time, "time", lambda: 0.0)

    def sleep(delay):
        waits.append(delay)
        elapsed[0] += delay

    monkeypatch.setattr(validator.time, "sleep", sleep)
    return elapsed, waits


def test_429_recovery_preserves_original_failure_and_honors_retry_after(
    monkeypatch, tmp_path
):
    validator = _validator()
    _, waits = _mock_budget_clock(monkeypatch, validator)
    calls = []

    def request(url, headers, *, timeout):
        calls.append(timeout)
        if len(calls) == 1:
            raise HTTPError(
                url,
                429,
                "limited",
                {"Retry-After": "3"},
                io.BytesIO(b'{"error":"limited"}'),
            )
        return b"manifest", {}

    monkeypatch.setattr(validator, "_registry_json", request)
    budget = validator._AcquisitionBudget(tmp_path)
    assert budget.request(
        "https://public.ecr.aws/v2/docker/library/python/manifests/sha256:test", {}
    ) == (b"manifest", {})
    assert len(calls) == 2 and waits == [3.0]
    assert (tmp_path / "request-01-http-429.raw").read_bytes() == b'{"error":"limited"}'
    metadata = json.loads((tmp_path / "request-01-http-429.json").read_text())
    assert metadata["status"] == 429 and metadata["retry_after"] == "3"


def test_429_exhaustion_refuses_output_and_retains_every_failed_attempt(
    monkeypatch, tmp_path
):
    validator = _validator()
    _, waits = _mock_budget_clock(monkeypatch, validator)
    requests = []

    def request(url, headers, *, timeout):
        requests.append(url)
        if "/token/" in url:
            return b'{"token":"never-retain-this-token"}', {}
        raise HTTPError(url, 429, "limited", {}, io.BytesIO(b"limited"))

    monkeypatch.setattr(validator, "_registry_json", request)
    output = tmp_path / "github-output"
    evidence = tmp_path / "evidence"
    assert (
        validator.main(
            _arguments(_mapping())
            + [
                "--verify-distribution",
                "--github-output",
                str(output),
                "--acquisition-evidence",
                str(evidence),
            ]
        )
        == 1
    )
    assert len(requests) == 4 and waits == [2.0, 4.0]
    assert not output.exists()
    assert len(list(evidence.glob("*.raw"))) == 3
    assert all(
        b"never-retain-this-token" not in path.read_bytes()
        for path in evidence.iterdir()
    )


@pytest.mark.parametrize(
    "retry_after", ["21", "invalid", "Thu, 01 Jan 1970 00:00:30 GMT"]
)
def test_unserviceable_retry_after_fails_without_sleep(monkeypatch, retry_after):
    validator = _validator()
    _, waits = _mock_budget_clock(monkeypatch, validator)

    def request(url, headers, *, timeout):
        raise HTTPError(
            url, 429, "limited", {"Retry-After": retry_after}, io.BytesIO(b"limited")
        )

    monkeypatch.setattr(validator, "_registry_json", request)
    with pytest.raises(ValueError):
        validator._AcquisitionBudget(None).request("https://public.ecr.aws/token/", {})
    assert waits == []


def test_request_and_elapsed_budget_are_shared_and_fail_closed(monkeypatch):
    validator = _validator()
    elapsed, _ = _mock_budget_clock(monkeypatch, validator)
    calls = []

    def request(url, headers, *, timeout):
        calls.append(timeout)
        return b"ok", {}

    monkeypatch.setattr(validator, "_registry_json", request)
    budget = validator._AcquisitionBudget(None)
    for _ in range(9):
        budget.request("https://public.ecr.aws/token/", {})
    with pytest.raises(ValueError, match="budget exhausted"):
        budget.request("https://public.ecr.aws/token/", {})
    assert len(calls) == 9
    elapsed[0] = 90
    budget = validator._AcquisitionBudget(None)
    elapsed[0] = 181
    with pytest.raises(ValueError, match="budget exhausted"):
        budget.request("https://public.ecr.aws/token/", {})
    assert len(calls) == 9


def test_cumulative_wait_budget_refuses_another_429_recovery(monkeypatch):
    validator = _validator()
    _, waits = _mock_budget_clock(monkeypatch, validator)
    count = [0]

    def request(url, headers, *, timeout):
        count[0] += 1
        if count[0] in (1, 3):
            raise HTTPError(
                url, 429, "limited", {"Retry-After": "11"}, io.BytesIO(b"limited")
            )
        return b"ok", {}

    monkeypatch.setattr(validator, "_registry_json", request)
    budget = validator._AcquisitionBudget(None)
    budget.request("https://public.ecr.aws/token/", {})
    with pytest.raises(ValueError, match="wait/time budget"):
        budget.request("https://public.ecr.aws/token/", {})
    assert count[0] == 3 and waits == [11.0]


def test_response_arriving_after_deadline_is_not_accepted(monkeypatch):
    validator = _validator()
    elapsed, _ = _mock_budget_clock(monkeypatch, validator)

    def request(url, headers, *, timeout):
        assert timeout == 20
        elapsed[0] = 91
        return b"ok", {}

    monkeypatch.setattr(validator, "_registry_json", request)
    with pytest.raises(ValueError, match="time budget exhausted"):
        validator._AcquisitionBudget(None).request("https://public.ecr.aws/token/", {})


@pytest.mark.parametrize("fault", [None, "descriptor"])
def test_optional_config_proof_binds_observed_config_descriptor_without_blob_download(
    monkeypatch, fault
):
    validator = _validator()
    config = json.dumps({"os": "linux", "architecture": "amd64"}).encode()
    config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
    child = json.dumps(
        {
            "schemaVersion": 2,
            "config": {"digest": config_digest},
            "layers": [{"digest": "sha256:" + "1" * 64}],
        }
    ).encode()
    child_digest = "sha256:" + hashlib.sha256(child).hexdigest()
    mapping = _mapping()
    mapping.update(
        manifest_kind="manifest",
        image_digest=child_digest,
        platform_manifest_digest=child_digest,
        platform_config_digest="sha256:" + "0" * 64
        if fault == "descriptor"
        else config_digest,
    )

    def request(url, headers, *, timeout):
        if "/token/" in url:
            return b'{"token":"test"}', {}
        if "/manifests/" in url:
            return child, {}
        raise AssertionError("Preflight must not follow blob/CDN acquisition")

    monkeypatch.setattr(validator, "_registry_json", request)
    if fault is None:
        validator.verify_distribution(mapping)
    else:
        with pytest.raises(ValueError):
            validator.verify_distribution(mapping)


def test_official_trivy_uses_ghcr_repository_scope_and_preserves_child_identity(
    monkeypatch,
):
    validator = _validator()
    mapping, index, child = _manifest_fixture()
    mapping.update(
        original_repository="docker.io/aquasec/trivy",
        distribution_repository="ghcr.io/aquasecurity/trivy",
    )
    calls = []

    def request(url, headers, *, timeout):
        calls.append(url)
        if "/token?" in url:
            query = validator.urllib.parse.parse_qs(
                validator.urllib.parse.urlsplit(url).query
            )
            assert query == {
                "service": ["ghcr.io"],
                "scope": ["repository:aquasecurity/trivy:pull"],
            }
            return b'{"token":"test"}', {}
        assert url.startswith("https://ghcr.io/v2/aquasecurity/trivy/manifests/")
        return index if url.endswith(mapping["image_digest"]) else child, {}

    monkeypatch.setattr(validator, "_registry_json", request)
    validator.verify_distribution(mapping)
    assert len(calls) == 3


def test_unadmitted_distribution_cannot_receive_a_network_request(monkeypatch):
    validator = _validator()
    mapping = _mapping()
    mapping["distribution_repository"] = "attacker.example/python"
    calls = []
    monkeypatch.setattr(
        validator, "_registry_json", lambda *args, **kwargs: calls.append(args)
    )
    with pytest.raises(ValueError, match="not admitted"):
        validator.verify_distribution(mapping)
    assert calls == []


@pytest.mark.parametrize(
    "url",
    [
        "https://public.ecr.aws/token/?scope=public",
        "https://ghcr.io/token?scope=public",
    ],
)
def test_failed_token_responses_are_never_retained_as_raw_evidence(
    monkeypatch, tmp_path, url
):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)

    def request(url, headers, *, timeout):
        raise HTTPError(
            url,
            429,
            "limited",
            {"Retry-After": "21"},
            io.BytesIO(b"sensitive-token-response"),
        )

    monkeypatch.setattr(validator, "_registry_json", request)
    with pytest.raises(ValueError):
        validator._AcquisitionBudget(tmp_path).request(url, {})
    assert (tmp_path / "request-01-http-429.raw").read_bytes() == b""
    metadata = json.loads((tmp_path / "request-01-http-429.json").read_text())
    assert metadata["token_response_body_omitted"] is True
    assert all(
        b"sensitive-token-response" not in path.read_bytes()
        for path in tmp_path.iterdir()
    )
