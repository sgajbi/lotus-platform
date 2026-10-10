# Technology Governance Policy Contract

This directory defines the platform contract for Lotus technology maturity, dependency evidence,
container-image evidence, vulnerability severity policy, and exception routing.

The contract is intentionally broader than the vulnerability-exception register. The policy defines
what technology posture Lotus accepts by default; the vulnerability-exception register records
bounded exceptions for concrete dependency, image, or image-layer findings.

## Files

| File | Purpose |
| --- | --- |
| `technology-governance-policy.schema.json` | Machine-readable JSON schema for the policy shape. |
| `lotus-technology-governance-policy.v1.json` | Canonical Lotus policy for maturity states, dependency/image evidence, vulnerability severity behavior, lens routing, and rollout posture. |
| `automation/validate_technology_governance_policy.py` | Deterministic validator for schema, semantic policy rules, and optional vulnerability-exception register integration. |

## Validator

Run:

```powershell
python automation/validate_technology_governance_policy.py
```

The default command validates the checked-in policy and the checked-in vulnerability-exception
examples. Use `--report-only` while piloting repository rollout or when scanner baselines are still
being measured.

## Policy boundary

The current contract is `report_only`. It is canonical policy truth, but it is not yet a claim that
every Lotus repository has completed rollout. Blocking promotion requires measured dependency and
container-image baselines, exception-register migration, false-positive classification,
repository-native commands, and exact-SHA validation for each pilot repository.

## Exact CI distribution admission

`container_image_evidence_policy.approved_distribution_mappings` admits only eleven exact
source/content/platform tuples approved in [the initial Platform #945 decision](https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6089421841)
and [the additional admission](https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6089758654),
with two Gateway audit tuples in [the exact Trivy/Syft admission](https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6090967601)
and three Core tuples in [the exact Python/Trivy/Prometheus admission](https://github.com/sgajbi/lotus-platform/issues/945#issuecomment-6091423369).
Original publishers remain `docker.io/library/python`, `docker.io/library/postgres` and
`docker.io/aquasec/trivy`, `docker.io/anchore/syft` and `docker.io/prom/prometheus`. Acquisition aliases are Docker's `public.ecr.aws/docker/library/...`
repositories, Trivy's official `ghcr.io/aquasecurity/trivy`, Syft's official `ghcr.io/anchore/syft` and Prometheus's `quay.io/prometheus/prometheus`. This is not approval
of all images in either registry. Mutable tags, replacement digests, other platforms and fallback
registries are not admitted. New tuples require reviewed policy and observation evidence.
Policy version `1.1.2` retains the `1.1.0` mapping structure and adds the three Core tuples; consumers must bind the matching
qualified schema and validator rather than mix it with an earlier policy checkout.

The Performance `e529...` digest is an existing single-platform manifest, so its platform
manifest digest equals its image digest. Report Python `a6e34...` and PostgreSQL `721873...`
are indexes with separately admitted Linux/amd64 children. The retained observation SHA
identifies manifest-byte equality evidence, not a signature or an image pull. R2 originally
contained no independent e529 config-platform measurement. Additive R3 observation
`2cffba060fea24c93b7e39273ba19f2ac5acaf91df76e092662192aa18e718f5` also verifies
source/alias config `541096...` bytes and its Linux/amd64 fields; R2 remains unchanged.
Mappings with `platform_config_digest` additionally bind the live manifest's config
descriptor to that independently observed config. The preflight does not fetch config
blobs or follow blob/CDN redirects. Actual Docker acquisition must still verify blobs.
No image layers are downloaded. Do not generalize that evidence to other tuples.

R3 additionally supplies the admitted PostgreSQL 16 index `ca0bd...`, child `75adc...`
and config `275447...`. R4 receipt `7dfb8d796c0b654f8604f4c485ab61c28912acec0b514b47fe439a22e17428bd`
supplies PostgreSQL 17 `2d2b...` and Trivy 0.71.2 `f5d0...`, including exact child/config
identity and actual Linux/amd64 config fields. PostgreSQL 17 is an explicitly approved
immutable selection replacing a mutable reference; the historical successful run's exact
binary was not recoverable, so historical binary equivalence is unproven. PostgreSQL 16,
16-alpine and 17 remain distinct mappings. Earlier R3 PG17 429 remains failed; R4 is a
separate successful paced observation. Trivy lists [GHCR as an official destination](https://github.com/aquasecurity/trivy/blob/main/docs/getting-started/installation.md).

Gateway's Trivy 0.72.0 index `cffe3f...` and Syft v1.42.3 index `5999d2...`
have exact admitted Linux/amd64 child and config descriptors. The admission's independent
raw recovery receipt `1eb8830984d5e849b9428139db7b95ba754b03ca99c2b642495d65e189abe6b0`
verifies retained source/distribution metadata equality; committed regression fixtures preserve
the observed root, child and config bytes for both. [Anchore publishes Syft at GHCR](https://github.com/anchore/syft/pkgs/container/syft).
Gateway Python reuses the existing `e529...` single-platform tuple, not its unadmitted parent
index. Neither audit admission identifies an earlier failed mutable-tag pull. Core's separately
unresolved Confluent inputs are not admitted by this change.

Core's pinned Bookworm Python index `97b0ea...`, Trivy 0.56.2 index `26245f...`
and Prometheus v2.47.2 index `300293...` retain their exact Linux/amd64 children
and configs. The independent recovery receipt
`2ce38a55832f50b126e74aa9e256c571df8397ce412fcb22d1d9165d50de1044`
binds their retained source/distribution bytes; committed fixtures rehash those bytes in
the native acquisition controls. [Prometheus documents its Quay and DockerHub distributions](https://prometheus.io/docs/prometheus/latest/installation/).
Only `docker.io/prom/prometheus` to `quay.io/prometheus/prometheus` is admitted;
unrelated Quay repositories, hosts, digests and platforms refuse before output.
This exact public repository serves manifests without a token request. ECR/GHCR
anonymous-token behavior and all acquisition budgets remain unchanged. Core PostgreSQL
reuses its existing admitted tuple. Confluent, Grafana and action-managed BuildKit
remain separate unresolved acquisition/capacity inputs; no operator copy is authorized.

From the `lotus-platform` checkout, both PowerShell and Bash support this static admission
check (replace the complete references with a reviewed tuple from the policy):

```text
python automation/validate_technology_governance_policy.py --source-image docker.io/library/python@sha256:e529028263dbe6910a2d96f7d2b8f5266385e917fd45d286ef166977c094a51e --distribution-image public.ecr.aws/docker/library/python@sha256:e529028263dbe6910a2d96f7d2b8f5266385e917fd45d286ef166977c094a51e --platform linux/amd64
```

Add `--verify-distribution` for a live, bounded read of manifest bytes. This reads an
anonymous public token for ECR/GHCR, or directly reads the exact public Prometheus Quay
repository, then the admitted index/manifest and child; it downloads no layers
and retains no token. An absent optional digest header is allowed; a contradictory header
or body hash is refused. Missing, unavailable, rate-limited or mismatched inputs fail closed.
Only HTTP 429 receives paced recovery: at most three attempts per request, nine requests
across the acquisition, a 90-second deadline and at most 20 cumulative seconds waiting.
`Retry-After` seconds or HTTP dates are honored if they fit the remaining budget; absent
headers use two/four-second backoff. Other HTTP errors, impossible delays or exhausted
budgets refuse output. There is no mutable fallback or Docker credential provisioning.
Use `--acquisition-evidence <temporary-directory>` to preserve failed public response bytes
and safe status/attempt/Retry-After metadata. Successful token responses and authorization
headers are never retained. The template uploads failure evidence even when admission fails.

For GitHub, compose the [backend prerequisite fragment](../../platform-standards/templates/workflows/image-acquisition.backend.template.yml)
into the owning workflow and bind `LOTUS_PLATFORM_GOVERNANCE_SHA` to a qualified Platform
commit. Set the reviewed full source and alias references as shown in the fragment.
Run the live check in a job **without services**, then make each acquiring job depend on it.
Use its `image` output for the actual service/base/audit acquisition and explicitly bind
Linux/amd64. Preserve existing job dependencies, service health checks and audit controls.
`--github-output` is available only with successful live verification; acquisition mode
cannot suppress errors with `--report-only`. A login or validation step inside a service
job is too late because service initialization precedes checkout and steps.

Acquisition mode validates the policy without evaluating the historical example exception
register as a current operational register. Pass `--exception-register` for a real consumer
register; its availability and expiry are evaluated normally. This command grants no
vulnerability exception. The default policy-only CLI retains its existing fixture behavior.

The prerequisite proves current manifest availability/content only. The actual hosted
service initialization, build, audit and smoke checks must still pass at the exact adopter
head. Preserve earlier failed cohorts and report later descendants separately. A registry
can become unavailable between preflight and pull; that acquisition must fail normally.

Keep original publisher, distribution repository, immutable index/manifest and platform
child identity distinct in provenance. Existing maturity, support, SBOM, signature,
attestation, scan freshness and runtime-smoke requirements remain in force. This bounded
admission does not promote the wider `report_only` #595 rollout or fill missing evidence.
Amazon documents [public digest acquisition and separate anonymous/authenticated quotas](https://docs.aws.amazon.com/AmazonECR/latest/public/docker-pull-ecr-image.html);
the mapping does not claim unlimited capacity.
