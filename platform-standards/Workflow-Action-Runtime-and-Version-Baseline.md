# Workflow Action Runtime and Version Baseline

## Purpose

Define the minimum GitHub Actions action-version baseline for Lotus platform-owned workflows and scaffold templates.

This standard exists to ensure:

1. supported action runtimes are used by default,
2. platform-owned workflows do not drift onto deprecated Node runtimes,
3. scaffolded repositories inherit modern action majors without manual cleanup,
4. GitHub runner deprecation warnings are handled as engineering debt, not ignored noise.

## Scope

Applies to:

1. repository workflows under `.github/workflows/`,
2. platform-owned workflow templates under `platform-standards/templates/workflows/`,
3. platform validators that enforce action-version posture.

## Required Baseline

Platform-owned workflows and scaffold templates must use the approved action majors for core GitHub-maintained actions:

| Action | Required Baseline |
| --- | --- |
| `actions/checkout` | `v6` |
| `actions/setup-python` | `v6` |
| `actions/setup-node` | `v5` |
| `actions/upload-artifact` | `v5` |

## Operating Rules

1. older majors for these actions are not allowed in platform-owned workflows or scaffold templates,
2. introducing a new core GitHub action into the platform baseline requires adding it to the validator contract when it becomes materially relied upon,
3. version drift must be corrected in templates first and then in live platform-owned workflows,
4. a runner deprecation warning for a platform-owned workflow is treated as a governance gap, not an informational-only warning.

## Validator Expectations

The platform validator must fail when:

1. a governed workflow references one of the baseline actions at an older major,
2. a governed workflow references one of the baseline actions without an explicit major tag,
3. platform-owned templates drift away from the approved major versions.

## Acceptance Posture

This standard is satisfied when:

1. the platform owns a workflow action-version validator,
2. the validator runs in platform repo checks,
3. platform-owned workflows and scaffold templates are both covered,
4. platform templates and live workflows both use the approved action majors.
