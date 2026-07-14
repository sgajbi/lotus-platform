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

Validate with:

```powershell
python automation/validate_auto_merge_releasability.py
python automation/validate_mainline_commit_provenance.py
```

Exceptions are temporary rollout records, not approval to keep weaker merge or releasability
behavior permanently.
