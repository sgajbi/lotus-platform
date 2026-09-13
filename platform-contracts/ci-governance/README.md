# CI Governance Contracts

This directory stores machine-readable CI governance contracts that are enforced by platform
automation.

Current contracts:

1. `auto-merge-releasability-exceptions.v1.json`
   Time-bounded rollout exceptions for the cross-repository auto-merge and exact-main
   releasability validator. Each exception must name the repository, owner, issue URL, reason,
   expiry, and exact validation violations.
2. `mainline-commit-provenance-exceptions.v1.json`
   Exact-commit exceptions for mainline commit verification loss. Each exception must be scoped to
   one repository and commit SHA, name the GitHub verification reason, include owner and issue
   evidence, and expire.
3. `sibling-source-manifest.v1.json`
   The exact revision of every registered sibling repository that the per-commit lanes (feature,
   PR merge, main releasability) read. The manifest is committed, so a lane verdict is a function
   of the `lotus-platform` commit it certifies and a re-run reproduces the original inputs. Each
   lane publishes the pins as step outputs, binds every sibling checkout's `ref:` to them, and
   measures the checkouts against the manifest afterwards. A pin moves only through a reviewed
   pull request; the scheduled Fleet Conformance lane reads sibling default branches on purpose
   and reports how far each pin lags.

Validate with:

```powershell
python automation/validate_auto_merge_releasability.py
python automation/validate_mainline_commit_provenance.py
python automation/validate_sibling_source_manifest.py
python automation/validate_sibling_source_manifest.py --report-drift
```

Exceptions are temporary rollout records, not approval to keep weaker merge or releasability
behavior permanently. Sibling pins are release inputs, not exceptions: a stale pin is reported by
the fleet lane and refreshed deliberately, never by a lane at run time.
