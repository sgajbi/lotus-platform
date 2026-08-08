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
