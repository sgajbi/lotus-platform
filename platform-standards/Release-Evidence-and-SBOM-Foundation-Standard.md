# Release Evidence and SBOM Foundation Standard

- Status: Active
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Define the minimum releasability evidence that every newly scaffolded Lotus backend service must emit from the `Main Releasability Gate`.

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

## Required Retained Artifacts

Every scaffolded backend `Main Releasability Gate` must retain:

1. `main-releasability-coverage-data`
2. `main-releasability-release-evidence`

The `main-releasability-release-evidence` artifact must contain:

1. `sbom.cdx.json`
2. `release-evidence.json`

## Scope Boundary

This is a foundation standard, not the final release-security posture.

This slice does not yet require:

1. signed provenance attestation,
2. image signing,
3. container vulnerability scanning,
4. dependency-license policy enforcement.

Those controls can layer on later, but newly scaffolded services must at minimum retain deterministic SBOM and release-manifest evidence.
