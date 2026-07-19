# Release Evidence and Deployable Image Provenance Standard

- Status: Active
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Define the minimum releasability evidence that every newly scaffolded Lotus backend service must
emit from the `Main Releasability Gate`, and define the target deployable-image provenance posture
that Lotus services should converge on before production promotion.

This standard exists so newly created services inherit enterprise-grade release evidence by default, instead of adding SBOM and release-manifest behavior later as one-off repo fixes.

## Dependency SBOM Baseline

Every scaffolded backend `Main Releasability Gate` workflow must generate a dependency SBOM artifact from the installed Python environment after repository-native installation has completed.

Required behavior:

1. install dependencies through the repository-native `make install` command,
2. generate a CycloneDX JSON SBOM named `sbom.cdx.json`,
3. retain the SBOM as part of the main releasability evidence artifact set.

Required command contract:

```text
./.venv/bin/cyclonedx-py environment --output-format JSON --output-file sbom.cdx.json
```

## Release Metadata Manifest Baseline

Every scaffolded backend `Main Releasability Gate` workflow must generate a release metadata manifest named `release-evidence.json`.

The manifest must capture enough context to tie the retained evidence back to the exact workflow execution that produced it.

Minimum manifest fields:

1. `repository`
2. `commit_sha`
3. `ref`
4. `workflow`
5. `run_id`
6. `dockerfile_path`
7. `image_digest` when an image is pushed
8. `image_tag` when an image is pushed
9. `version` when a service version is declared

## Required Retained Artifacts

Every scaffolded backend `Main Releasability Gate` must retain:

1. `main-releasability-coverage-data`
2. `main-releasability-release-evidence`

The `main-releasability-release-evidence` artifact must contain:

1. `sbom.cdx.json`
2. `release-evidence.json`

## Deployable Image Provenance Target

Every Lotus repository that builds or deploys a container image must converge on a deterministic
image provenance chain. A repository may roll this out in stages, but gaps must be visible in its
issue-discovery ledger, quality scorecard, release evidence, or follow-up backlog.

Container images inherit the same vulnerability and technology-maturity posture as application
libraries. Release images should be based on mature, widely deployed, actively maintained base
images with broad scanner, hardening, and operational support. Beta, preview, experimental, novelty
runtime, or unsupported base-image families are excluded by default. A base-image or runtime-family
exception must be issue-backed, time-bounded, and tied to explicit vulnerability, supportability,
and rollback evidence.

The target control set is:

1. the image is tagged with the Git commit SHA,
2. OCI labels include commit, Git branch/ref, repository URL, version, build time, and CI
   pipeline/run ID,
3. release images are built and pushed by CI only, not from developer workstations,
4. the pushed image digest is captured in `release-evidence.json` or an equivalent release
   manifest,
5. an SBOM is generated for the image or runtime dependency set,
6. vulnerability scanning passes or records an approved, time-bounded exception,
7. the image is signed,
8. a provenance attestation is generated,
9. Kubernetes, Helm, or deployment manifests deploy by digest, not mutable tags,
10. the `/version` or version/build metadata endpoint exposes the same commit, Git branch/ref,
    repository, version, build time, pipeline/run ID, and image digest metadata,
11. the same immutable image is promoted across environments; later environments do not rebuild
    from source, and
12. build secrets do not leak through Dockerfile `ARG`, Dockerfile `ENV`, image history, build
    logs, OCI labels, release manifests, or runtime version metadata.

Vulnerability posture is release evidence, not a best-effort note. A passing release lane must
either include dependency and image vulnerability scans with no unowned policy-breaking findings, or
carry approved time-bounded exceptions that identify severity, affected package or layer, fix
availability, owner, expiry, and compensating controls. Permanent suppressions, unscoped scanner
output, and "scanner unavailable" claims are not production-certification evidence.

## Deployment Promotion Manifest Baseline

Service-owned release evidence proves that CI produced an immutable image digest and retained the
required SBOM, scan, signature, and attestation artifacts. Platform-owned deployment promotion
evidence proves that an environment consumes that exact digest.

Lotus deployment promotion manifests live under
`platform-contracts/deployment-promotion/` and are validated by:

```text
python automation/validate_deployment_promotion_manifest.py
```

Required behavior:

1. all included deployment environments reference images as `image@sha256:<digest>`, without
   mutable tags,
2. every included environment's deployed digest matches the service release-evidence digest,
3. later environments promote the same immutable digest instead of rebuilding from source,
4. out-of-scope environments record a concrete reason and follow-up evidence, and
5. production certification remains false until approved live deployment proof exists.

## Evaluation Conditions

Use these checks when reviewing or promoting the control set:

1. `docker image inspect`, registry metadata, or equivalent OCI proof shows the required labels.
2. The CI run that pushed the image also retained the digest-bearing release manifest.
3. SBOM, vulnerability scan, signature, and provenance attestation artifacts are linked to the same
   commit SHA, CI run ID, and image digest.
4. Deployment manifests reference the digest form, not a mutable tag.
5. A `/version` or version/build metadata endpoint contract test compares runtime metadata with the
   release manifest or image label source.
6. The deployment promotion manifest reconciles release-evidence digest, deployed digest, and
   same-digest environment promotion without claiming production certification ahead of live proof.
7. Secret scanning covers Dockerfile `ARG`/`ENV`, image history, build logs, labels, release
   manifests, and version metadata.

## Scope Boundary

The dependency SBOM and release metadata manifest are the minimum retained evidence for newly
scaffolded backend services. The deployable-image provenance target is the production hardening
direction for all containerized Lotus services; existing repositories should adopt it through
bounded issues and CI gates once the measured baseline is deterministic and low-noise.
