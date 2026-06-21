# Workflow Security and Permissions Standard

## Purpose

Define the minimum GitHub Actions workflow-security baseline for Lotus repositories and platform-owned workflow templates.

This standard exists to ensure:

1. least-privilege workflow permissions,
2. explicit governance around `pull_request_target`,
3. no silent escalation of write-capable automation,
4. reproducible review of workflow trust boundaries.

## Scope

Applies to:

1. repository workflows under `.github/workflows/`,
2. platform-owned workflow templates under `platform-standards/templates/workflows/`,
3. platform validators that enforce workflow-security posture.

## Required Baseline

Every governed workflow must:

1. declare top-level `permissions`,
2. avoid implicit GitHub token defaults,
3. avoid `pull_request_target` unless the workflow is explicitly approved for it,
4. remain read-only unless a write-capable workflow is intentionally required and documented.

## Permission Rules

### Read-only default

The default workflow posture is read-only.

Typical allowed baseline:

1. `contents: read`

Additional read-only scopes may be allowed when required by the workflow, but write scopes must not appear without an explicit policy exception.

### Write-capable workflows

Approved write-capable workflows are exception-only platform assets.

Write permissions are allowed only for explicitly approved workflow files with a documented platform purpose.

Current approved exception:

1. `platform-standards/templates/workflows/pr-auto-merge.template.yml`
2. `platform-standards/templates/workflows/merged-pr-main-releasability.template.yml`

`pr-auto-merge.template.yml` is allowed to request:

1. `contents: write`
2. `pull-requests: write`

`merged-pr-main-releasability.template.yml` is allowed to request:

1. `actions: write`

No other workflow may request write permissions unless this standard and the validator allowlist are updated intentionally.

## Event Rules

### `pull_request_target`

`pull_request_target` is prohibited by default because it executes with elevated repository context.

It is allowed only for explicitly approved workflow files whose behavior is narrowly constrained and whose permissions are intentionally reviewed.

Current approved exception:

1. `platform-standards/templates/workflows/pr-auto-merge.template.yml`
2. `platform-standards/templates/workflows/merged-pr-main-releasability.template.yml`

## Allowed Action Source Pattern

This slice does not yet require SHA pinning across all workflows, but workflow actions must still be:

1. official GitHub actions,
2. approved third-party actions already owned by the platform baseline,
3. versioned explicitly rather than floating on an unversioned ref.

Future rollout may tighten this to provenance-backed or SHA-pinned policy.

## Validator Expectations

The platform validator must fail when:

1. a workflow file has no top-level `permissions`,
2. a non-allowlisted workflow uses `pull_request_target`,
3. a non-allowlisted workflow requests write permissions,
4. an allowlisted write-capable workflow drifts away from its approved permission set.

## Current Allowlist

| Workflow Path | Allowed Event Exception | Allowed Write Permissions |
| --- | --- | --- |
| `platform-standards/templates/workflows/pr-auto-merge.template.yml` | `pull_request_target` | `contents: write`, `pull-requests: write` |
| `platform-standards/templates/workflows/merged-pr-main-releasability.template.yml` | `pull_request_target` | `actions: write` |

## Acceptance Posture

This standard is satisfied when:

1. the platform owns a workflow-security validator,
2. the validator runs in platform repo checks,
3. the validator covers both live platform workflows and platform-owned templates,
4. the allowlist is explicit, minimal, and tested.
