# Platform End-to-End Validation Coverage Standard

- Status: Active
- Governing RFC: `rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`

## Purpose

Define the minimum contract for platform-owned end-to-end validation profiles so the Lotus system-validation lane stays explicit, reviewable, and extendable.

## Required Profile Source of Truth

`lotus-platform` must keep one machine-readable profile manifest for platform validation coverage:

1. `automation/platform-validation-profiles.json`

The manifest is the source of truth for:

1. supported validation profiles,
2. targets executed by each profile,
3. shared-scenario and MWR-scenario suffix behavior,
4. required retained evidence artifacts for each profile.

## Required Validation Profiles

The current minimum platform validation coverage baseline is:

1. `core-performance-baseline`
2. `core-performance-green-lanes`

## Required Coverage Contract

Each profile entry must declare:

1. `name`
2. `description`
3. `targets`
4. `required_artifacts`

Each target entry must declare:

1. `name`
2. `uses_shared_suffix`
3. `uses_mwr_suffix`

## Workflow and Entrypoint Contract

The following artifacts must stay aligned:

1. `.github/workflows/platform-end-to-end-validation.yml`
2. `automation/Invoke-PlatformValidationLane.ps1`
3. `automation/platform-validation-profiles.json`

Required alignment rules:

1. the workflow dispatch `validation_profile` options must match the manifest profile names,
2. the PowerShell entrypoint must resolve profiles from the manifest instead of keeping a separate hardcoded mapping,
3. required artifact expectations must be traceable from the manifest and produced under `output/cross-app`.

## Evidence Baseline

Every platform validation profile must define retained evidence sufficient for operator review.

At minimum this includes:

1. machine-readable JSON validation outputs,
2. human-readable markdown validation outputs,
3. per-target workflow summary markdown artifacts.

## Scope Boundary

This slice governs the explicit coverage contract for the currently supported platform validation profiles.

It does not yet require:

1. UI screenshot coverage for every profile,
2. cross-domain profiles beyond the current core-performance scope,
3. environment bring-up orchestration inside this same manifest.

Those can be added later, but profile definitions must remain manifest-driven and validator-enforced.
