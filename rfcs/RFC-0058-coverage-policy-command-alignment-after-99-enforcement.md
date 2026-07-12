# RFC-0058 Coverage Policy Command Alignment After 99% Enforcement

## Problem Statement
Cross-repository coverage policy automation in `automation/test-coverage-policy.json` is not fully aligned with currently enforced repository gates.

## Root Cause
Service-level CI/local gates were tightened incrementally, but the centralized policy command map was not updated in lockstep.

## Proposed Solution
Align centralized coverage commands with active service gates:
1. Set lotus-manage coverage command fail-under to `99`.
2. Set lotus-performance coverage command fail-under to `99`.
3. Keep lotus-core command via `python scripts/quality/coverage_gate.py` (already enforced at 99 in lotus-core).

## Architectural Impact
No runtime behavior change. Improves governance and automation consistency for cross-platform quality measurement.

## Risks and Trade-offs
- Any hidden service-level drift now surfaces faster in platform policy checks.
- Slightly higher short-term friction when coverage regresses.

## High-Level Implementation Approach
1. Update `automation/test-coverage-policy.json`.
2. Use updated policy file in automation runs and PR monitoring.
3. Keep policy and service gates synchronized as a required governance practice.
