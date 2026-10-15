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
    return next(
        item
        for item in _policy()["container_image_evidence_policy"][
            "approved_distribution_mappings"
        ]
        if item["image_digest"]
        == "sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1"
    )


@pytest.fixture(params=["16", "17", "python", "python312"])
def original_variant(request):
    return request.param


def _selected(variant):
    digest = {"16": "ca0bd484", "17": "2d2b8998", "python": "e5290282", "python312": "a6e34c59"}[variant]
    return next(item for item in _policy()["container_image_evidence_policy"]["approved_distribution_mappings"]
                if item["image_digest"].startswith("sha256:" + digest))


def _original_responder(monkeypatch, validator, variant, *, fault=None):
    mapping, index, child = _manifest_fixture()
    authority = _selected(variant)
    repository = authority["original_repository"].removeprefix("docker.io/")
    if authority["manifest_kind"] == "manifest":
        mapping.update(manifest_kind="manifest", image_digest=mapping["platform_manifest_digest"])
    mapping.update(original_repository="docker.io/" + repository,
                   distribution_repository="public.ecr.aws/docker/" + repository,
                   platform_config_digest="sha256:" + ("2" if fault == "config-descriptor" else "1") * 64,
                   original_source_selection_approval=authority["original_source_selection_approval"])
    identity = tuple(mapping[key] for key in validator.ORIGINAL_SELECTION_FIELDS)
    monkeypatch.setattr(validator, "ORIGINAL_SELECTION_APPROVALS",
                        {identity: mapping["original_source_selection_approval"]})
    calls = []
    challenge = ('Bearer realm="https://auth.docker.io/token",'
                 f'service="registry.docker.io",scope="repository:{repository}:pull"')

    def request(url, headers, *, timeout):
        calls.append(url)
        assert timeout <= 20 and "public.ecr.aws" not in url
        if url.startswith("https://auth.docker.io/token?"):
            query = validator.urllib.parse.parse_qs(validator.urllib.parse.urlsplit(url).query)
            assert query == {"service": ["registry.docker.io"], "scope": [f"repository:{repository}:pull"]}
            if fault == "token":
                return b'{}', {}
            return b'{"token":"pg-secret"}', {}
        assert url.startswith(f"https://registry-1.docker.io/v2/{repository}/manifests/")
        if "Authorization" not in headers:
            if fault == "absent-challenge":
                return index, {}
            if fault == "redirect":
                raise ValueError("distribution registry redirects are not admitted")
            if fault == "tls":
                raise validator.urllib.error.URLError("TLS failed")
            value = challenge
            if fault in ("realm", "scope", "service"):
                value = value.replace({"realm": "auth.docker.io", "scope": repository,
                                       "service": "registry.docker.io"}[fault], "attacker.example")
            code = 403 if fault == "forbidden" else 401
            raise HTTPError(url, code, "challenge", {"WWW-Authenticate": value}, io.BytesIO(b"public"))
        assert headers["Authorization"] == "Bearer pg-secret"
        if fault in ("unauthorized", "rate", "unavailable"):
            code = {"unauthorized": 401, "rate": 429, "unavailable": 503}[fault]
            raise HTTPError(url, code, "refused", {}, io.BytesIO(b"reflected pg-secret"))
        raw = index if mapping["manifest_kind"] == "index" and url.endswith(mapping["image_digest"]) else child
        if fault == "root-bytes" and url.endswith(mapping["image_digest"]) or fault == "child-bytes" and raw == child:
            raw += b" "
        response = {"Docker-Content-Digest": "sha256:" + "0" * 64} if fault == "header" else {}
        return raw, response

    monkeypatch.setattr(validator, "_registry_json", request)
    return mapping, calls


def test_explicit_original_selects_before_any_distribution_request(monkeypatch, original_variant):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, calls = _original_responder(monkeypatch, validator, original_variant)
    assert validator.verify_distribution(mapping, acquisition_source="original") == (
        mapping["original_repository"] + "@" + mapping["image_digest"]
    )
    assert len(calls) == (3 if mapping["manifest_kind"] == "manifest" else 4)
    assert not any("ecr" in url for url in calls)


def test_original_selection_authority_preserves_default_distribution(monkeypatch, original_variant):
    validator = _validator()
    mapping = _selected(original_variant)
    calls = []
    monkeypatch.setattr(validator, "_verify_publisher_distribution", lambda actual, budget: calls.append(actual))
    monkeypatch.setattr(validator, "_verify_official_original", lambda *args: pytest.fail("unexpected original request"))
    assert validator.verify_distribution(mapping) == mapping["distribution_repository"] + "@" + mapping["image_digest"]
    assert calls == [mapping]


@pytest.mark.parametrize("fault", ["absent-challenge", "redirect", "tls", "realm", "scope", "service",
                                   "forbidden", "unauthorized", "rate", "unavailable", "root-bytes",
                                   "child-bytes", "header", "config-descriptor", "token"])
def test_explicit_original_fails_closed_without_alternate_source(monkeypatch, tmp_path, original_variant, fault):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, calls = _original_responder(monkeypatch, validator, original_variant, fault=fault)
    with pytest.raises((OSError, ValueError)):
        validator.verify_distribution(mapping, acquisition_source="original", evidence_dir=tmp_path)
    assert len(calls) <= 9
    assert all("ecr" not in url and "attacker" not in url for url in calls)
    assert all(b"pg-secret" not in path.read_bytes() for path in tmp_path.iterdir())


@pytest.mark.parametrize("key", ["original_repository", "distribution_repository", "image_digest", "manifest_kind",
                                 "platform", "platform_manifest_digest", "platform_config_digest",
                                 "original_source_selection_approval"])
def test_explicit_original_authority_binds_every_identity_before_network(monkeypatch, original_variant, key):
    validator = _validator()
    mapping = _selected(original_variant)
    mapping[key] = "wrong"
    calls = []
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(ValueError):
        validator.verify_distribution(mapping, acquisition_source="original")
    assert calls == []


@pytest.mark.parametrize("index", range(11))
def test_original_selection_refuses_unapproved_mappings(monkeypatch, index):
    validator = _validator()
    mapping = _policy()["container_image_evidence_policy"]["approved_distribution_mappings"][index]
    if mapping.get("original_source_selection_approval"):
        mapping.pop("original_source_selection_approval")
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: pytest.fail("network before admission"))
    with pytest.raises(ValueError):
        validator.verify_distribution(mapping, acquisition_source="original")


@pytest.mark.parametrize("options", [[], ["--verify-distribution", "--allow-original-source-fallback"],
                                     ["--report-only", "--verify-distribution"]])
def test_explicit_selection_requires_live_nonconflicting_cli(monkeypatch, tmp_path, original_variant, options):
    validator = _validator()
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: pytest.fail("unexpected network"))
    with pytest.raises(SystemExit) as exc:
        validator.main(_arguments(_selected(original_variant)) + ["--acquisition-source", "original"] + options)
    assert exc.value.code == 2


def test_explicit_selection_cli_emits_only_verified_original(monkeypatch, tmp_path, original_variant):
    validator = _validator()
    mapping = _selected(original_variant)
    calls = []
    monkeypatch.setattr(validator, "_verify_official_original", lambda actual, budget, repository: calls.append((actual, repository)))
    output = tmp_path / "github-output"
    assert validator.main(_arguments(mapping) + ["--acquisition-source", "original", "--verify-distribution",
                                                "--github-output", str(output)]) == 0
    assert output.read_text() == "image=" + mapping["original_repository"] + "@" + mapping["image_digest"] + "\n"
    assert calls == [(mapping, mapping["original_repository"].removeprefix("docker.io/"))]


def test_explicit_selection_cli_no_output_after_verification_failure(monkeypatch, tmp_path, original_variant):
    validator = _validator()
    def unavailable(*args):
        raise ValueError("unavailable")
    monkeypatch.setattr(validator, "_verify_official_original", unavailable)
    output = tmp_path / "github-output"
    assert validator.main(_arguments(_selected(original_variant)) + ["--acquisition-source", "original", "--verify-distribution",
                                              "--github-output", str(output)]) == 1
    assert not output.exists()


@pytest.mark.parametrize("approval", [None, "", 7, False, "unreviewed", "16", "17", "python", "python312"])
def test_explicit_original_missing_or_transplanted_approval_refuses_before_output(
    monkeypatch, tmp_path, original_variant, approval
):
    validator = _validator()
    policy = _policy()
    mapping = next(item for item in policy["container_image_evidence_policy"]["approved_distribution_mappings"]
                   if item["image_digest"] == _selected(original_variant)["image_digest"])
    if approval is None:
        mapping.pop("original_source_selection_approval")
    elif approval in ("16", "17", "python", "python312"):
        mapping["original_source_selection_approval"] = _selected(approval)["original_source_selection_approval"]
        if approval == original_variant:
            # Same authority on a different tuple also refuses before network.
            mapping["platform_config_digest"] = "sha256:" + "0" * 64
    else:
        mapping["original_source_selection_approval"] = approval
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy))
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: pytest.fail("network before approval"))
    output = tmp_path / "github-output"
    assert validator.main(_arguments(mapping) + ["--policy", str(policy_path), "--acquisition-source", "original",
                                               "--verify-distribution", "--github-output", str(output)]) == 1
    assert not output.exists()


@pytest.mark.parametrize("exhaustion", ["requests", "deadline", "wait"])
def test_explicit_original_keeps_one_acquisition_budget(monkeypatch, original_variant, exhaustion):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, calls = _original_responder(monkeypatch, validator, original_variant, fault="rate")
    original = validator._AcquisitionBudget

    class ExhaustedBudget(original):
        def __init__(self, evidence_dir):
            super().__init__(evidence_dir)
            if exhaustion == "requests": self.requests = 9
            if exhaustion == "deadline": self.deadline = 0
            if exhaustion == "wait": self.waited = 20

    monkeypatch.setattr(validator, "_AcquisitionBudget", ExhaustedBudget)
    with pytest.raises(ValueError, match="budget"):
        validator.verify_distribution(mapping, acquisition_source="original")
    assert len(calls) == (3 if exhaustion == "wait" else 0)


def test_operator_original_selection_commands_bind_all_exact_approved_tuples():
    import shlex

    root = Path(__file__).resolve().parents[2]
    commands = [shlex.split(line) for line in
                (root / "platform-contracts/technology-governance/README.md").read_text().splitlines()
                if line.startswith("python automation/validate_technology_governance_policy.py ")
                and "--acquisition-source original" in line]
    assert len(commands) == 4
    validator = _validator()
    admitted = []
    for command in commands:
        assert command[:2] == ["python", "automation/validate_technology_governance_policy.py"]
        assert "--verify-distribution" in command
        mapping = validator.resolve_distribution(
            _policy(), command[command.index("--source-image") + 1],
            command[command.index("--distribution-image") + 1], command[command.index("--platform") + 1],
        )
        validator.require_original_selection(mapping)
        admitted.append(mapping["image_digest"])
    assert set(admitted) == {_selected(variant)["image_digest"] for variant in ("16", "17", "python", "python312")}


def test_python312_selection_does_not_admit_conditional_fallback(monkeypatch, tmp_path):
    validator = _validator()
    mapping = _selected("python312")
    validator.require_original_selection(mapping)
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: pytest.fail("network before fallback admission"))
    with pytest.raises(ValueError, match="fallback is not admitted"):
        validator.verify_distribution(mapping, allow_original_source=True)
    output = tmp_path / "github-output"
    assert validator.main(_arguments(mapping) + ["--verify-distribution", "--allow-original-source-fallback",
                                               "--github-output", str(output)]) == 1
    assert not output.exists()


def _arguments(mapping):
    return [
        "--source-image",
        mapping["original_repository"] + "@" + mapping["image_digest"],
        "--distribution-image",
        mapping["distribution_repository"] + "@" + mapping["image_digest"],
        "--platform",
        mapping["platform"],
    ]


@pytest.mark.parametrize("index", range(11))
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
    "fixture_name,name",
    [
        ("gateway", "trivy"),
        ("gateway", "syft"),
        ("core", "python"),
        ("core", "trivy"),
        ("core", "prometheus"),
    ],
)
@pytest.mark.parametrize(
    "fault", [None, "digest", "platform", "repository", "host", "child", "config"]
)
def test_admitted_metadata_verifies_observed_bytes_and_refuses_drift(
    monkeypatch, tmp_path, fixture_name, name, fault
):
    # Retained public bytes from the sealed observation, not synthesized digests.
    # Root's admission independently checked original/distribution equality.
    fixture = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / f"fixtures/image-distribution/{fixture_name}-admitted-metadata.json"
        ).read_text()
    )[name]
    raw = {kind: value.encode() for kind, value in fixture.items()}

    def digest(kind):
        return "sha256:" + hashlib.sha256(raw[kind]).hexdigest()

    policy = _policy()
    mapping = next(
        item
        for item in policy["container_image_evidence_policy"][
            "approved_distribution_mappings"
        ]
        if item["image_digest"] == digest("root")
    )
    assert mapping["platform_manifest_digest"] == digest("child")
    assert mapping["platform_config_digest"] == digest("config")
    config = json.loads(raw["config"])
    assert (config["os"], config["architecture"]) == ("linux", "amd64")
    assert json.loads(raw["child"])["config"]["digest"] == digest("config")
    args = _arguments(mapping)
    if fault == "digest":
        args[1] = mapping["original_repository"] + "@sha256:" + "0" * 64
        args[3] = mapping["distribution_repository"] + "@sha256:" + "0" * 64
    elif fault == "platform":
        args[5] = "linux/arm64"
    elif fault == "repository":
        host = mapping["distribution_repository"].split("/", 1)[0]
        args[3] = host + "/attacker/" + name + "@" + mapping["image_digest"]
    elif fault == "host":
        args[3] = "unrelated.example/" + name + "@" + mapping["image_digest"]
    elif fault in ("child", "config"):
        mapping[
            "platform_manifest_digest" if fault == "child" else "platform_config_digest"
        ] = "sha256:" + "0" * 64
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy))
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    calls = []
    host, repository = mapping["distribution_repository"].split("/", 1)

    def request(url, headers, *, timeout):
        calls.append(url)
        if "/token" in url:
            assert host != "quay.io"
            query = validator.urllib.parse.parse_qs(
                validator.urllib.parse.urlsplit(url).query
            )
            assert query == {
                "service": [host],
                "scope": [f"repository:{repository}:pull"],
            }
            return b'{"token":"ephemeral-test-token"}', {}
        assert url.startswith(f"https://{host}/v2/{repository}/manifests/")
        assert ("Authorization" in headers) == (host != "quay.io")
        return raw["root"] if url.endswith(digest("root")) else raw["child"], {}

    monkeypatch.setattr(validator, "_registry_json", request)
    output = tmp_path / "image-output"
    result = validator.main(
        args
        + [
            "--policy",
            str(policy_path),
            "--verify-distribution",
            "--github-output",
            str(output),
        ]
    )
    if fault is None:
        assert result == 0
        assert output.read_text() == f"image={args[3]}\n"
        assert len(calls) == (2 if host == "quay.io" else 3)
    else:
        assert result == 1
        assert not output.exists()
        if fault in ("digest", "platform", "repository", "host"):
            assert calls == []


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
    mapping.pop("original_source_selection_approval", None)
    mapping["image_digest"] = "sha256:" + hashlib.sha256(index).hexdigest()
    mapping["platform_manifest_digest"] = child_digest
    mapping["platform_config_digest"] = "sha256:" + "1" * 64
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
    monkeypatch.setattr(validator, "verify_distribution", lambda mapping: (
        mapping["distribution_repository"] + "@" + mapping["image_digest"]
    ))
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


@pytest.mark.parametrize(
    "original,distribution",
    [
        ("docker.io/library/python", "attacker.example/python"),
        ("docker.io/prom/prometheus", "quay.io/other/prometheus"),
        ("docker.io/prom/prometheus", "other.example/prometheus/prometheus"),
        ("docker.io/other/prometheus", "quay.io/prometheus/prometheus"),
    ],
)
def test_unadmitted_distribution_cannot_receive_a_network_request(
    monkeypatch, original, distribution
):
    validator = _validator()
    mapping = _mapping()
    mapping.update(original_repository=original, distribution_repository=distribution)
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


def _fallback_fixture(monkeypatch, validator):
    mapping, _, child = _manifest_fixture()
    mapping.update(
        manifest_kind="manifest",
        image_digest="sha256:" + hashlib.sha256(child).hexdigest(),
        platform_manifest_digest="sha256:" + hashlib.sha256(child).hexdigest(),
        platform_config_digest="sha256:" + "1" * 64,
        original_source_fallback_approval="https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6160682836",
    )
    # Synthetic bytes exercise identity checks; real policy identity is tested separately.
    monkeypatch.setattr(validator, "ORIGINAL_SOURCE_FALLBACK_IDENTITY", tuple(
        mapping[key] for key in (
            "original_repository", "image_digest", "platform", "platform_config_digest"
        )
    ))
    return mapping, child


def _fallback_responder(monkeypatch, validator, mapping, raw, *, fault=None, status=429):
    calls = []
    challenge = ('Bearer realm="https://auth.docker.io/token",'
                 'service="registry.docker.io",scope="repository:library/python:pull"')

    def request(url, headers, *, timeout):
        calls.append(url)
        assert timeout <= 20
        if url.startswith("https://public.ecr.aws/token/"):
            return b'{"token":"ecr-secret"}', {}
        if url.startswith("https://public.ecr.aws/"):
            if fault == "preferred-body":
                return raw + b" ", {}
            if fault == "preferred-valid":
                return raw, {}
            if fault == "preferred-tls":
                raise validator.urllib.error.URLError("TLS verification failed")
            raise HTTPError(url, status, "unavailable", {}, io.BytesIO(b"quota"))
        if url.startswith("https://auth.docker.io/token?"):
            assert headers == {}
            query = validator.urllib.parse.parse_qs(validator.urllib.parse.urlsplit(url).query)
            assert query == {"service": ["registry.docker.io"],
                             "scope": ["repository:library/python:pull"]}
            if fault == "token-failure":
                raise HTTPError(url, 503, "unavailable", {}, io.BytesIO(b"source-secret"))
            return b'{"token":"source-secret"}', {}
        assert url == ("https://registry-1.docker.io/v2/library/python/manifests/"
                       + mapping["image_digest"])
        if "Authorization" not in headers:
            value = challenge
            if fault in ("realm", "service", "scope"):
                value = value.replace({"realm": "auth.docker.io", "service": "registry.docker.io",
                                       "scope": "library/python"}[fault], "attacker.example")
            if fault == "missing-challenge":
                value = ""
            if fault == "redirect":
                raise ValueError("distribution registry redirects are not admitted")
            raise HTTPError(url, 401, "challenge", {"WWW-Authenticate": value}, io.BytesIO(b"challenge"))
        assert headers["Authorization"] == "Bearer source-secret"
        if fault == "source-quota":
            raise HTTPError(url, 429, "limited", {}, io.BytesIO(b"reflected source-secret"))
        if fault == "source-body":
            return raw + b" ", {}
        if fault == "source-header":
            return raw, {"Docker-Content-Digest": "sha256:" + "0" * 64}
        return raw, {}

    monkeypatch.setattr(validator, "_registry_json", request)
    return calls


@pytest.mark.parametrize("status", [429, 502, 503, 504])
def test_exact_original_source_recovers_only_availability_with_shared_budget(
    monkeypatch, tmp_path, status
):
    validator = _validator()
    _, waits = _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    calls = _fallback_responder(monkeypatch, validator, mapping, raw, status=status)
    assert validator.verify_distribution(mapping, evidence_dir=tmp_path,
                                         allow_original_source=True) == (
        mapping["original_repository"] + "@" + mapping["image_digest"]
    )
    assert len(calls) == (7 if status == 429 else 5)
    assert waits == ([2.0, 4.0] if status == 429 else [])
    assert len(list(tmp_path.glob("*-http-429.raw"))) == (3 if status == 429 else 0)
    assert all(b"secret" not in path.read_bytes() for path in tmp_path.iterdir())


@pytest.mark.parametrize("fault", ["preferred-valid", "preferred-body", "preferred-tls"])
def test_original_source_never_hides_preferred_success_identity_or_trust_failure(monkeypatch, fault):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    calls = _fallback_responder(monkeypatch, validator, mapping, raw, fault=fault)
    if fault == "preferred-valid":
        assert validator.verify_distribution(mapping, allow_original_source=True).startswith("public.ecr.aws/")
    else:
        with pytest.raises((ValueError, OSError)):
            validator.verify_distribution(mapping, allow_original_source=True)
    assert all("docker.io" not in url for url in calls)


@pytest.mark.parametrize("status", [401, 403, 404, 500])
def test_non_availability_http_failure_never_falls_back(monkeypatch, status):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    calls = _fallback_responder(monkeypatch, validator, mapping, raw, status=status)
    with pytest.raises(HTTPError):
        validator.verify_distribution(mapping, allow_original_source=True)
    assert len(calls) == 2


@pytest.mark.parametrize("fault", ["realm", "service", "scope", "missing-challenge", "redirect",
                                   "token-failure", "source-quota", "source-body", "source-header"])
def test_original_source_refuses_unsafe_or_unavailable_inputs_without_secrets(monkeypatch, tmp_path, fault):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    calls = _fallback_responder(monkeypatch, validator, mapping, raw, fault=fault)
    with pytest.raises((ValueError, OSError)):
        validator.verify_distribution(mapping, evidence_dir=tmp_path, allow_original_source=True)
    assert len(calls) <= 9
    assert all("attacker" not in url for url in calls)
    assert all(b"secret" not in path.read_bytes() for path in tmp_path.iterdir())


@pytest.mark.parametrize("fault", ["unapproved", "config", "digest", "platform", "publisher"])
def test_fallback_admission_refuses_drift_before_network(monkeypatch, fault):
    validator = _validator()
    mapping = next(item for item in _policy()["container_image_evidence_policy"]["approved_distribution_mappings"]
                   if item.get("original_source_fallback_approval"))
    if fault == "unapproved":
        del mapping["original_source_fallback_approval"]
    else:
        key = {"config": "platform_config_digest", "digest": "image_digest",
               "platform": "platform", "publisher": "original_repository"}[fault]
        mapping[key] = "unapproved"
    calls = []
    monkeypatch.setattr(validator, "_registry_json", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(ValueError):
        validator.verify_distribution(mapping, allow_original_source=True)
    assert calls == []


def test_fallback_requires_live_verification_and_explicit_policy_admission(tmp_path):
    validator = _validator()
    with pytest.raises(SystemExit) as error:
        validator.main(_arguments(_mapping()) + ["--allow-original-source-fallback"])
    assert error.value.code == 2
    policy = _policy()
    mapping = policy["container_image_evidence_policy"]["approved_distribution_mappings"][0]
    mapping["original_source_fallback_approval"] = "https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6160682836"
    assert any("exact admitted identity" in error for error in validator.validate_policy(policy))


UNREVIEWED_FALLBACK_APPROVALS = [
    "https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-1",
    "https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6159989398",
    "https://github.com/sgajbi/lotus-platform/issues/946#issuecomment-6160682836",
    "https://example.com/sgajbi/lotus-platform/issues/945#issuecomment-6160682836",
    None,
    "",
    7,
    False,
]
APPROVAL_CASE_IDS = [
    "fabricated", "candidate-only", "wrong-issue", "wrong-host",
    "null", "empty", "number", "boolean",
]


def _policy_with_fallback_approval(approval):
    policy = _policy()
    mapping = next(
        item
        for item in policy["container_image_evidence_policy"]["approved_distribution_mappings"]
        if "original_source_fallback_approval" in item
    )
    mapping["original_source_fallback_approval"] = approval
    return policy, mapping


def _refuse_unexpected_registry_request(*args, **kwargs):
    pytest.fail("Approval drift must be refused before any registry request")


def test_fallback_approval_accepts_the_actual_reviewed_policy():
    validator = _validator()
    policy = _policy()
    assert validator.validate_policy(policy, exception_register_paths=[]) == []


@pytest.mark.parametrize("approval", UNREVIEWED_FALLBACK_APPROVALS, ids=APPROVAL_CASE_IDS)
def test_fallback_approval_refuses_policy_and_schema_drift(approval):
    validator = _validator()
    policy, _ = _policy_with_fallback_approval(approval)
    semantic_errors = []
    validator._validate_distribution_mappings(policy, semantic_errors)
    assert any("reviewed approval" in error for error in semantic_errors)
    assert any(
        "original_source_fallback_approval" in error
        for error in validator.validate_policy(policy, exception_register_paths=[])
    )


@pytest.mark.parametrize("approval", UNREVIEWED_FALLBACK_APPROVALS, ids=APPROVAL_CASE_IDS)
def test_fallback_approval_refuses_direct_admission_before_requests(monkeypatch, approval):
    validator = _validator()
    _, mapping = _policy_with_fallback_approval(approval)
    monkeypatch.setattr(validator, "_registry_json", _refuse_unexpected_registry_request)
    with pytest.raises(ValueError, match="not admitted"):
        validator.verify_distribution(mapping, allow_original_source=True)


@pytest.mark.parametrize("approval", UNREVIEWED_FALLBACK_APPROVALS, ids=APPROVAL_CASE_IDS)
def test_fallback_approval_refuses_cli_supplied_policy_before_output(monkeypatch, tmp_path, approval):
    validator = _validator()
    policy, mapping = _policy_with_fallback_approval(approval)
    policy_path = tmp_path / "supplied-policy.json"
    policy_path.write_text(json.dumps(policy), encoding="utf-8")
    output = tmp_path / "image-output"
    evidence = tmp_path / "acquisition-evidence"
    monkeypatch.setattr(validator, "_registry_json", _refuse_unexpected_registry_request)
    assert validator.main(_arguments(mapping) + [
        "--policy", str(policy_path), "--verify-distribution", "--allow-original-source-fallback",
        "--github-output", str(output), "--acquisition-evidence", str(evidence),
    ]) == 1
    assert not output.exists() and not evidence.exists()


@pytest.mark.parametrize("fault", [None, "source-body", "source-quota", "scope"])
def test_cli_exports_only_verified_original_source_or_no_image(monkeypatch, tmp_path, fault):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    policy = _policy()
    policy["container_image_evidence_policy"]["approved_distribution_mappings"] = [mapping]
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy))
    _fallback_responder(monkeypatch, validator, mapping, raw, fault=fault)
    output = tmp_path / "image-output"
    result = validator.main(_arguments(mapping) + ["--policy", str(policy_path),
                            "--verify-distribution", "--allow-original-source-fallback",
                            "--github-output", str(output)])
    if fault is None:
        assert result == 0
        assert output.read_text() == f"image={mapping['original_repository']}@{mapping['image_digest']}\n"
    else:
        assert result == 1
        assert not output.exists()


def test_source_fallback_reuses_deadline_and_refuses_after_budget_exhaustion(monkeypatch):
    validator = _validator()
    elapsed, _ = _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    native = _fallback_responder(monkeypatch, validator, mapping, raw)
    request = validator._registry_json

    def late_request(url, headers, *, timeout):
        if "registry-1.docker.io" in url:
            elapsed[0] = 91
        return request(url, headers, timeout=timeout)

    monkeypatch.setattr(validator, "_registry_json", late_request)
    with pytest.raises(ValueError, match="budget exhausted"):
        validator.verify_distribution(mapping, allow_original_source=True)
    assert len(native) == 5


def test_source_fallback_refuses_wrong_config_descriptor(monkeypatch):
    validator = _validator()
    _mock_budget_clock(monkeypatch, validator)
    mapping, raw = _fallback_fixture(monkeypatch, validator)
    mapping["platform_config_digest"] = "sha256:" + "0" * 64
    monkeypatch.setattr(validator, "ORIGINAL_SOURCE_FALLBACK_IDENTITY", tuple(
        mapping[key] for key in ("original_repository", "image_digest", "platform", "platform_config_digest")
    ))
    _fallback_responder(monkeypatch, validator, mapping, raw)
    with pytest.raises(ValueError, match="config descriptor mismatch"):
        validator.verify_distribution(mapping, allow_original_source=True)
