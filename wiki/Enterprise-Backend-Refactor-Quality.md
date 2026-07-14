# Enterprise Backend Refactor Quality

`lotus-platform` uses a measured quality baseline for enterprise backend refactor work.

This baseline complements the Lotus Bank-Buyable Engineering Contract. The refactor instructions
define the measurement-heavy execution path; the bank-buyable contract defines the standing
non-degradation bar that Lotus skills apply to everyday app work.

## Source Artifacts

- `quality/baseline_report.md`
- `quality/baseline_report.json`
- `quality/quality_scorecard.md`
- `quality/refactor_health_report.md`
- `quality/architecture_rules.md`
- `quality/api_governance_rules.md`
- `quality/ci_quality_gates.md`
- `quality/security_findings.md`
- `quality/refactor_decisions.md`

## Commands

```powershell
python automation\generate_enterprise_backend_quality_baseline.py --write --check
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

## Current Posture

The baseline is report-only. It records source size, largest files, Python function size and
complexity hotspots, quality-tool availability, unit test collection count, security keyword review
signals, and the current OpenAPI ownership boundary.

The baseline is also freshness-checked. `generate_enterprise_backend_quality_baseline.py --check`
compares stable material metrics in `quality/baseline_report.json` with the current repository:
source/Python file counts, Python function count, maximum complexity, maximum function length, and
collected unit tests. It intentionally does not gate exact total source-line count because that
proved noisy during write/check sequencing.

Promote a quality signal to a blocking gate only after it is measured, deterministic, low-noise,
locally runnable, covered by focused tests, and reflected in README, wiki source, repo context,
central context, the scorecard, and relevant skill guidance.

For RFC-driven refactor slices, use a slice closure manifest before moving on. Record blockers
cleared, blockers preserved, proof artifacts, commands, docs/wiki and supported-feature decisions,
merge method, post-merge validation, and branch cleanup evidence. Branches should be deleted only
after merge, diff, or cherry-pick evidence proves no code or durable governance truth is stranded.

New services created with `automation/New-Lotus-Service.ps1` should start with the same posture:
service-profile-aware README/repo-context/wiki references, quality scorecard, architecture rules,
CI-quality notes, refactor decisions, a layered `src/app/api|application|domain|ports|infrastructure|runtime|observability|security|resilience`
skeleton with runtime composition boundary protection, report-only architecture-boundary and quality-baseline commands, and baseline gates for
maintainability thresholds, OpenAPI, supported features, endpoint certification,
no-sensitive-content, coverage, health/readiness, observability, and workflow lanes.

## Baseline Snapshot

Use `quality/baseline_report.json` for exact machine-readable evidence,
`quality/baseline_report.md` for human-readable current-state metrics, and
`quality/quality_scorecard.md` for before/after PR summary.
