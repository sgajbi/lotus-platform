# RFC-0076 Slice 5 Evidence: Context, Skills, and Branch Hygiene

- RFC: `RFC-0076-canonical-front-office-demo-data-contract.md`
- Date: `2026-04-11`
- Scope:
  - `lotus-platform`
  - deployed Lotus agent guidance

## What changed

Slice 5 closes RFC-0076 by updating only the context and skill surfaces that materially benefit
from explicit canonical contract guidance.

### Central context updates

The following central context documents now point agents to the RFC-0076 contract files when a task
depends on the governed front-office dataset:

1. `context/AGENTS-OPERATING-CONTRACT.md`
2. `context/LOTUS-ENGINEERING-CONTEXT.md`
3. `docs/onboarding/LOTUS-AGENT-RAMP-UP.md`
4. `context/recent-architectural-decisions-digest.md`

The core change is explicit:

1. `PB_SG_GLOBAL_BAL_001` is not just the default portfolio ID,
2. the machine-readable truth lives in:
   - `context/contracts/canonical-front-office-demo-data-contract.json`
   - `context/contracts/canonical-front-office-demo-data-invariants.json`
3. runtime evidence should preserve contract provenance instead of relying on implicit repo
   convention.

### Skill review outcome

Reviewed skills:

1. `lotus-qa-platform-validator`

Implemented change:

1. the skill now distinguishes backend/runtime QA from governed front-office QA,
2. it points front-office validation work to `Invoke-Canonical-FrontOffice-QA.ps1`,
3. it references the RFC-0076 contract file for canonical dataset work,
4. it records `output/front-office-qa/latest.{json,md}` as governed evidence outputs.

Conscious no-change decisions:

1. `lotus-backend-delivery-governance` did not require an RFC-0076-specific change because slice 2
   and slice 3 adoption lives in repository code and tests rather than in delivery workflow policy.
2. `lotus-frontend-delivery-governance` did not require a change because front-office runtime
   routing already lives in central context and the validator/runbook path is now explicit.
3. `lotus-pr-premerge-gate` did not require a change because RFC-0076 did not alter merge posture,
   only dataset governance and evidence provenance.

## Stale guidance review

No additional stale context encouraging ad hoc smoke portfolio usage remained in the governed
central context after RFC-0075 and RFC-0076 updates. The remaining `PORT_SMOKE_*` references are
intentional historical evidence inside RFC-0075 tests and acceptance artifacts, where they are
needed to prove the prior pollution problem and its removal.

## Branch hygiene posture

Branch hygiene remains an explicit closure requirement:

1. slice work is committed in small, repo-scoped commits,
2. each affected repository has its own branch or PR surface,
3. GitHub is used as the heavy validation engine while targeted local tests provide immediate proof,
4. final merge and branch cleanup happen only after required checks are green.

## Verification

```text
python -m pytest tests\unit\test_rfc_0076_canonical_demo_data_contract.py tests\unit\test_front_office_runtime_automation_contract.py -q
5 passed
```

## Review outcome

This slice is intentionally narrow and in the right shape. It improves future agent effectiveness
without duplicating the contract across many documents or overfitting multiple skills to one RFC.
