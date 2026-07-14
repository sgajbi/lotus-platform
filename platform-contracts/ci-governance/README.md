# CI Governance Contracts

This directory stores machine-readable CI governance contracts that are enforced by platform
automation.

Current contracts:

1. `auto-merge-releasability-exceptions.v1.json`
   Time-bounded rollout exceptions for the cross-repository auto-merge and exact-main
   releasability validator. Each exception must name the repository, owner, issue URL, reason,
   expiry, and exact validation violations.

Validate with:

```powershell
python automation/validate_auto_merge_releasability.py
```

Exceptions are temporary rollout records, not approval to keep weaker merge or releasability
behavior permanently.
