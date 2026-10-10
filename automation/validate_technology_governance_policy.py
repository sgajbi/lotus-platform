from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_DIR = ROOT / "platform-contracts" / "technology-governance"
POLICY_PATH = CONTRACT_DIR / "lotus-technology-governance-policy.v1.json"
SCHEMA_PATH = CONTRACT_DIR / "technology-governance-policy.schema.json"
VULNERABILITY_EXCEPTION_EXAMPLES = (
    ROOT / "platform-contracts" / "vulnerability-exceptions" / "examples"
)

if str(ROOT / "automation") not in sys.path:
    sys.path.insert(0, str(ROOT / "automation"))

from json_contract_validation import validate_json_schema_subset_document  # noqa: E402
from validate_vulnerability_exception_register import (  # noqa: E402
    validate_register_paths as validate_vulnerability_exception_register_paths,
)


REQUIRED_STATES = {"approved_default", "restricted_exception", "prohibited"}
EXCLUDED_RELEASE_PHASES = {
    "alpha",
    "beta",
    "preview",
    "release_candidate",
    "experimental",
    "incubating",
    "end_of_life",
    "novelty_driven_major_upgrade",
}
REQUIRED_DEFAULT_CRITERIA = {
    "general_availability",
    "active_maintenance",
    "broad_adoption",
    "credible_security_patch_channel",
    "well_documented",
    "broad_training_and_tooling_support",
    "license_compatible",
}
REQUIRED_DEPENDENCY_ARTIFACTS = {
    "direct_dependency_manifest",
    "locked_manifest",
    "transitive_dependency_inventory",
    "runtime_sbom",
    "license_inventory",
    "vulnerability_scan",
}
REQUIRED_CONTAINER_IDENTITY_FIELDS = {
    "image_repository",
    "image_digest",
    "git_sha",
    "source_repository",
    "build_pipeline",
    "build_timestamp",
    "architecture",
}
REQUIRED_CONTAINER_ARTIFACTS = {
    "oci_labels",
    "image_sbom",
    "signature",
    "provenance_attestation",
    "scan_receipt",
    "base_image_support_evidence",
    "runtime_smoke_receipt",
}
REQUIRED_SEVERITY_CLASSES = {"known_exploited", "critical", "high", "medium", "low"}
PUBLISHER_DISTRIBUTIONS = {
    "docker.io/library/python": "public.ecr.aws/docker/library/python",
    "docker.io/library/postgres": "public.ecr.aws/docker/library/postgres",
    "docker.io/aquasec/trivy": "ghcr.io/aquasecurity/trivy",
    "docker.io/anchore/syft": "ghcr.io/anchore/syft",
    "docker.io/prom/prometheus": "quay.io/prometheus/prometheus",
}
REQUIRED_LENSES = {
    "lens/dependency-hygiene",
    "lens/environment-supply-chain-provenance",
    "lens/vulnerability-management",
    "lens/release-rollout-compatibility",
}


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: policy must be a JSON object")
    return payload


def validate_policy_path(
    path: Path = POLICY_PATH,
    *,
    exception_register_paths: list[Path] | None = None,
    as_of_date: date | None = None,
) -> list[str]:
    try:
        policy = load_policy(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"{path}: {exc}"]
    return validate_policy(
        policy,
        document_name=str(path),
        exception_register_paths=exception_register_paths,
        as_of_date=as_of_date,
    )


def validate_policy(
    policy: dict[str, Any],
    *,
    document_name: str = "policy",
    exception_register_paths: list[Path] | None = None,
    as_of_date: date | None = None,
) -> list[str]:
    errors = validate_json_schema_subset_document(
        SCHEMA_PATH,
        policy,
        document_name=document_name,
    )

    try:
        _validate_default_posture(policy, errors)
        _validate_technology_states(policy, errors)
        _validate_dependency_evidence(policy, errors)
        _validate_container_image_evidence(policy, errors)
        _validate_distribution_mappings(policy, errors)
        _validate_vulnerability_policy(policy, errors)
        _validate_exception_policy(policy, errors)
        _validate_lens_routing(policy, errors)
        _validate_rollout(policy, errors)
    except (KeyError, TypeError) as exc:
        errors.append(
            f"{document_name}: semantic validation could not complete after schema findings: {exc}"
        )

    exception_paths = exception_register_paths
    if exception_paths is None:
        exception_paths = sorted(VULNERABILITY_EXCEPTION_EXAMPLES.glob("*.json"))
    errors.extend(
        validate_vulnerability_exception_register_paths(
            exception_paths,
            as_of_date=as_of_date,
        )
    )
    return errors


def _validate_default_posture(policy: dict[str, Any], errors: list[str]) -> None:
    posture = policy["default_technology_posture"]
    criteria = set(posture["required_criteria"])
    excluded = set(posture["excluded_by_default"])
    missing_criteria = REQUIRED_DEFAULT_CRITERIA - criteria
    missing_exclusions = EXCLUDED_RELEASE_PHASES - excluded
    if missing_criteria:
        errors.append(
            "default_technology_posture.required_criteria missing required values: "
            + ", ".join(sorted(missing_criteria))
        )
    if missing_exclusions:
        errors.append(
            "default_technology_posture.excluded_by_default missing required values: "
            + ", ".join(sorted(missing_exclusions))
        )


def _validate_technology_states(policy: dict[str, Any], errors: list[str]) -> None:
    states = {state["state"]: state for state in policy["technology_states"]}
    missing_states = REQUIRED_STATES - set(states)
    if missing_states:
        errors.append(
            "technology_states missing required states: "
            + ", ".join(sorted(missing_states))
        )
        return

    approved = states["approved_default"]
    restricted = states["restricted_exception"]
    prohibited = states["prohibited"]
    if approved["requires_exception"] or not approved["production_use_allowed"]:
        errors.append(
            "approved_default technology must allow production use without an exception"
        )
    if not restricted["requires_exception"] or restricted["production_use_allowed"]:
        errors.append(
            "restricted_exception technology must require an exception and remain non-production by default"
        )
    if prohibited["requires_exception"] or prohibited["production_use_allowed"]:
        errors.append(
            "prohibited technology must not allow production use or exception-based promotion"
        )


def _validate_dependency_evidence(policy: dict[str, Any], errors: list[str]) -> None:
    evidence = policy["dependency_evidence_policy"]
    artifacts = set(evidence["required_artifacts"])
    missing = REQUIRED_DEPENDENCY_ARTIFACTS - artifacts
    if missing:
        errors.append(
            "dependency_evidence_policy.required_artifacts missing required values: "
            + ", ".join(sorted(missing))
        )
    if evidence["inventory_source"] != "locked_manifests":
        errors.append(
            "dependency_evidence_policy.inventory_source must be locked_manifests"
        )


def _validate_container_image_evidence(
    policy: dict[str, Any], errors: list[str]
) -> None:
    evidence = policy["container_image_evidence_policy"]
    identity_fields = set(evidence["required_identity_fields"])
    artifacts = set(evidence["required_artifacts"])
    missing_identity = REQUIRED_CONTAINER_IDENTITY_FIELDS - identity_fields
    missing_artifacts = REQUIRED_CONTAINER_ARTIFACTS - artifacts
    if evidence["identity_source"] != "immutable_digest":
        errors.append(
            "container_image_evidence_policy.identity_source must be immutable_digest"
        )
    if evidence["mutable_tag_posture"] != "non_certifying":
        errors.append(
            "container_image_evidence_policy.mutable_tag_posture must be non_certifying"
        )
    if evidence["max_scan_age_days"] > 30:
        errors.append("container_image_evidence_policy.max_scan_age_days must be <= 30")
    if missing_identity:
        errors.append(
            "container_image_evidence_policy.required_identity_fields missing required values: "
            + ", ".join(sorted(missing_identity))
        )
    if missing_artifacts:
        errors.append(
            "container_image_evidence_policy.required_artifacts missing required values: "
            + ", ".join(sorted(missing_artifacts))
        )


def _validate_vulnerability_policy(policy: dict[str, Any], errors: list[str]) -> None:
    severities = {
        entry["class"]: entry for entry in policy["vulnerability_severity_policy"]
    }
    missing = REQUIRED_SEVERITY_CLASSES - set(severities)
    if missing:
        errors.append(
            "vulnerability_severity_policy missing required classes: "
            + ", ".join(sorted(missing))
        )
        return

    known_exploited = severities["known_exploited"]
    critical = severities["critical"]
    high = severities["high"]
    if known_exploited["exception_allowed"]:
        errors.append("known_exploited vulnerability policy must not allow exceptions")
    if "block_release" not in known_exploited["release_behavior"]:
        errors.append("known_exploited vulnerability policy must block release")
    for severity_name, entry in (("critical", critical), ("high", high)):
        if not entry["exception_allowed"]:
            errors.append(
                f"{severity_name} vulnerability policy must allow approved exceptions"
            )
        if "block_release" not in entry["release_behavior"]:
            errors.append(
                f"{severity_name} vulnerability policy must block release without proof"
            )


def _validate_exception_policy(policy: dict[str, Any], errors: list[str]) -> None:
    exception_policy = policy["exception_policy"]
    if not exception_policy["fail_closed_when_scan_unavailable"]:
        errors.append("exception_policy.fail_closed_when_scan_unavailable must be true")
    if exception_policy["permanent_suppressions_allowed"]:
        errors.append("exception_policy.permanent_suppressions_allowed must be false")
    required = set(exception_policy["required_fields"])
    for field in (
        "canonical_github_issue",
        "accountable_owner",
        "component_identity",
        "version_or_digest",
        "severity",
        "runtime_exposure",
        "exploitability",
        "expiry_date",
        "planned_fix",
        "approval_evidence",
        "removal_proof",
    ):
        if field not in required:
            errors.append(f"exception_policy.required_fields missing {field}")


def _validate_lens_routing(policy: dict[str, Any], errors: list[str]) -> None:
    lenses = {entry["lens"] for entry in policy["lens_routing"]}
    missing = REQUIRED_LENSES - lenses
    if missing:
        errors.append(
            "lens_routing missing required lenses: " + ", ".join(sorted(missing))
        )


def _validate_rollout(policy: dict[str, Any], errors: list[str]) -> None:
    rollout = policy["rollout"]
    pilot_repositories = set(rollout["pilot_repositories"])
    for repository in ("lotus-platform", "lotus-core"):
        if repository not in pilot_repositories:
            errors.append(f"rollout.pilot_repositories missing {repository}")
    if rollout["lane_posture"] == "blocking":
        promotion = rollout["promotion_requirement"].lower()
        for term in ("baseline", "exception", "exact-sha"):
            if term not in promotion:
                errors.append(
                    f"rollout.promotion_requirement must cite {term} before blocking promotion"
                )


def _validate_distribution_mappings(policy: dict[str, Any], errors: list[str]) -> None:
    seen = set()
    for mapping in policy["container_image_evidence_policy"][
        "approved_distribution_mappings"
    ]:
        key = (
            mapping["original_repository"],
            mapping["image_digest"],
            mapping["platform"],
        )
        if key in seen:
            errors.append(
                "distribution mappings must have unique source digest/platform identities"
            )
        seen.add(key)
        if mapping["distribution_repository"] != PUBLISHER_DISTRIBUTIONS.get(
            mapping["original_repository"]
        ):
            errors.append(
                "distribution mapping must preserve the original publisher repository"
            )
        same = mapping["image_digest"] == mapping["platform_manifest_digest"]
        if same != (mapping["manifest_kind"] == "manifest"):
            errors.append(
                "distribution mapping manifest/index and platform digest disagree"
            )


def resolve_distribution(
    policy: dict[str, Any], source_image: str, distribution_image: str, platform: str
) -> dict[str, Any]:
    """Resolve an exact admitted tuple; tags, empty values and other platforms cannot match."""
    matches = [
        mapping
        for mapping in policy["container_image_evidence_policy"][
            "approved_distribution_mappings"
        ]
        if source_image
        == mapping["original_repository"] + "@" + mapping["image_digest"]
        and distribution_image
        == mapping["distribution_repository"] + "@" + mapping["image_digest"]
        and platform == mapping["platform"]
    ]
    if len(matches) != 1:
        raise ValueError(
            "image source/distribution/digest/platform tuple is not uniquely admitted"
        )
    return matches[0]


def _registry_json(
    url: str, headers: dict[str, str], *, timeout: float = 20
) -> tuple[bytes, Any]:
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, response_headers, newurl):
            raise ValueError("distribution registry redirects are not admitted")

    opener = urllib.request.build_opener(NoRedirect())
    with opener.open(
        urllib.request.Request(url, headers=headers), timeout=timeout
    ) as response:
        if response.status != 200:
            raise ValueError("distribution registry returned a non-success response")
        body = response.read(2 * 1024 * 1024 + 1)
        if len(body) > 2 * 1024 * 1024:
            raise ValueError("distribution registry response exceeds manifest limit")
        return body, response.headers


class _AcquisitionBudget:
    """One acquisition: at most 9 requests, 90 seconds and 20 seconds of paced waits."""

    def __init__(self, evidence_dir: Path | None):
        self.deadline = time.monotonic() + 90
        self.requests = 0
        self.waited = 0.0
        self.evidence_dir = evidence_dir

    def _record_failure(self, url: str, error: urllib.error.HTTPError) -> None:
        if self.evidence_dir is None:
            return
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        prefix = self.evidence_dir / f"request-{self.requests:02d}-http-{error.code}"
        # Successful token responses and authorization headers are never retained.
        is_token = urllib.parse.urlsplit(url).path.rstrip("/") == "/token"
        body = error.read(2 * 1024 * 1024 + 1) if not is_token else b""
        prefix.with_suffix(".raw").write_bytes(body)
        prefix.with_suffix(".json").write_text(
            json.dumps(
                {
                    "url": url,
                    "status": error.code,
                    "request": self.requests,
                    "retry_after": error.headers.get("Retry-After"),
                    "body_sha256": hashlib.sha256(body).hexdigest(),
                    "body_truncated": len(body) > 2 * 1024 * 1024,
                    "token_response_body_omitted": is_token,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def request(self, url: str, headers: dict[str, str]) -> tuple[bytes, Any]:
        for attempt in range(3):
            remaining = self.deadline - time.monotonic()
            if self.requests >= 9 or remaining <= 0:
                raise ValueError("image acquisition request/time budget exhausted")
            self.requests += 1
            try:
                result = _registry_json(url, headers, timeout=min(20, remaining))
                if time.monotonic() >= self.deadline:
                    raise ValueError("image acquisition time budget exhausted")
                return result
            except urllib.error.HTTPError as error:
                self._record_failure(url, error)
                error.close()
                if error.code != 429 or attempt == 2:
                    raise
                retry_after = error.headers.get("Retry-After")
                if retry_after is None:
                    delay = float(2 ** (attempt + 1))
                elif retry_after.isdecimal():
                    delay = float(retry_after)
                else:
                    delay = parsedate_to_datetime(retry_after).timestamp() - time.time()
                delay = max(1.0, delay)
                if (
                    self.waited + delay > 20
                    or delay >= self.deadline - time.monotonic()
                ):
                    raise ValueError(
                        "image acquisition Retry-After exceeds wait/time budget"
                    ) from error
                self.waited += delay
                time.sleep(delay)
        raise ValueError("image acquisition retry budget exhausted")


def verify_distribution(
    mapping: dict[str, Any], *, evidence_dir: Path | None = None
) -> None:
    """Read manifest bytes only. Unavailable/rate-limited registries fail; never pull layers."""
    distribution = mapping["distribution_repository"]
    if distribution != PUBLISHER_DISTRIBUTIONS.get(mapping["original_repository"]):
        raise ValueError("distribution publisher repository is not admitted")
    host, repository = distribution.split("/", 1)
    budget = _AcquisitionBudget(evidence_dir)
    headers = {
        "Accept": ", ".join(
            [
                "application/vnd.oci.image.index.v1+json",
                "application/vnd.docker.distribution.manifest.list.v2+json",
                "application/vnd.oci.image.manifest.v1+json",
                "application/vnd.docker.distribution.manifest.v2+json",
            ]
        ),
    }
    # This exact public Quay repository serves manifests anonymously. Publisher
    # admission above still precedes every request; no generic host discovery.
    if host != "quay.io":
        query = urllib.parse.urlencode(
            {"service": host, "scope": f"repository:{repository}:pull"}
        )
        token_path = "/token/" if host == "public.ecr.aws" else "/token"
        body, _ = budget.request(f"https://{host}{token_path}?{query}", {})
        token_payload = json.loads(body)
        if not isinstance(token_payload, dict):
            raise ValueError("distribution registry token response must be an object")
        token = token_payload.get("token") or token_payload.get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError(
                "distribution registry did not provide an anonymous pull token"
            )
        headers["Authorization"] = "Bearer " + token

    def manifest(digest: str) -> dict[str, Any]:
        raw, response_headers = budget.request(
            f"https://{host}/v2/{repository}/manifests/{digest}", headers
        )
        actual = "sha256:" + hashlib.sha256(raw).hexdigest()
        declared = response_headers.get("Docker-Content-Digest")
        if actual != digest or declared not in (None, actual):
            raise ValueError(
                "distribution manifest bytes or optional digest header mismatch"
            )
        payload = json.loads(raw)
        if not isinstance(payload, dict) or payload.get("schemaVersion") != 2:
            raise ValueError(
                "distribution manifest is not a supported OCI/Docker v2 object"
            )
        return payload

    payload = manifest(mapping["image_digest"])
    if mapping["manifest_kind"] == "index":
        children = [
            item.get("digest")
            for item in payload.get("manifests", [])
            if item.get("platform") == {"os": "linux", "architecture": "amd64"}
        ]
        if children != [mapping["platform_manifest_digest"]]:
            raise ValueError(
                "distribution index does not select the admitted linux/amd64 child"
            )
        payload = manifest(mapping["platform_manifest_digest"])
    if (
        "manifests" in payload
        or not isinstance(payload.get("config"), dict)
        or not payload.get("layers")
    ):
        raise ValueError("distribution platform object must be an image manifest")
    # Config-platform bytes were independently observed at admission. Bind that
    # immutable descriptor here; blob redirects are left to actual Docker acquisition.
    config_digest = mapping.get("platform_config_digest")
    if config_digest is not None and payload["config"].get("digest") != config_digest:
        raise ValueError("distribution platform config descriptor mismatch")


def _parse_as_of_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be YYYY-MM-DD") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Lotus technology maturity and vulnerability posture policy."
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=POLICY_PATH,
        help="Technology-governance policy JSON file to validate.",
    )
    parser.add_argument(
        "--exception-register",
        action="append",
        type=Path,
        dest="exception_registers",
        help="Vulnerability exception register JSON file to validate with the policy. Defaults to checked-in examples in policy mode, none in acquisition mode.",
    )
    parser.add_argument(
        "--as-of-date",
        type=_parse_as_of_date,
        default=date.today(),
        help="As-of date for exception expiry checks, in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Print findings but return success so repositories can measure before lane promotion.",
    )
    parser.add_argument(
        "--source-image", help="Original publisher repository@sha256 digest."
    )
    parser.add_argument(
        "--distribution-image", help="Admitted distribution repository@sha256 digest."
    )
    parser.add_argument(
        "--platform", help="Explicit acquisition platform, currently linux/amd64."
    )
    parser.add_argument(
        "--verify-distribution",
        action="store_true",
        help="Verify live manifest availability and bytes without pulling layers.",
    )
    parser.add_argument(
        "--github-output",
        type=Path,
        help="Append image output only after successful live verification.",
    )
    parser.add_argument(
        "--acquisition-evidence",
        type=Path,
        help="Optional temporary directory for failed public manifest response bytes and safe HTTP metadata; tokens omitted.",
    )
    args = parser.parse_args(argv)
    acquisition = any(
        (
            args.source_image is not None,
            args.distribution_image is not None,
            args.platform is not None,
            args.verify_distribution,
            args.github_output is not None,
            args.acquisition_evidence is not None,
        )
    )
    if acquisition and (
        args.report_only
        or not all((args.source_image, args.distribution_image, args.platform))
    ):
        parser.error(
            "acquisition requires source image, distribution image and platform; report-only is forbidden"
        )
    if args.github_output and not args.verify_distribution:
        parser.error("GitHub image output requires live distribution verification")
    if args.acquisition_evidence and not args.verify_distribution:
        parser.error("Acquisition evidence requires live distribution verification")

    errors = validate_policy_path(
        args.policy,
        # Acquisition does not evaluate historical schema fixtures as today's
        # operational exceptions. Explicit consumer registers still fail closed.
        exception_register_paths=(args.exception_registers or [])
        if acquisition
        else args.exception_registers,
        as_of_date=args.as_of_date,
    )
    if errors:
        print("Technology governance policy findings:")
        for error in errors:
            print(f"- {error}")
        if args.report_only and not acquisition:
            print("Result: report-only findings emitted; exit code suppressed.")
            return 0
        return 1

    if acquisition:
        try:
            mapping = resolve_distribution(
                load_policy(args.policy),
                args.source_image,
                args.distribution_image,
                args.platform,
            )
            if args.verify_distribution:
                if args.acquisition_evidence:
                    verify_distribution(mapping, evidence_dir=args.acquisition_evidence)
                else:
                    verify_distribution(mapping)
            if args.github_output:
                with args.github_output.open("a", encoding="utf-8") as output:
                    output.write(f"image={args.distribution_image}\n")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            # Never print HTTP headers, anonymous tokens, or potentially sensitive response bodies.
            print(
                f"Image acquisition refused ({type(exc).__name__}); no image output emitted."
            )
            return 1
        print(
            "Exact distribution mapping accepted; live manifest check: "
            + str(args.verify_distribution)
        )
    print(f"Technology governance policy validation passed: {args.policy}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
