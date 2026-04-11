# Fix-Forward Patterns

Use these patterns when real execution evidence reveals a failure after a push.

## Stale Expectation Pattern

When a test or validator fails because the product contract changed but the expectation did not:

1. confirm the current product or contract truth,
2. update the stale expectation,
3. add regression coverage so the updated contract is explicit,
4. do not preserve obsolete assertions just because they used to be green.

## Validator Overreach Pattern

When a validator is technically green locally but semantically wrong or too broad:

1. narrow it to the truthful governed scope,
2. add coverage for the corrected scope,
3. avoid broad suppressions that hide real defects.

## Local-Only Assumption Pattern

When automation works locally but fails on GitHub or another machine:

1. remove workstation-specific assumptions,
2. prefer environment-derived paths and portable defaults,
3. degrade gracefully on shared runners when the local-only artifact does not exist,
4. keep the local stronger check where it is still truthful and valuable.

## Heavy-Check Offload Pattern

When a fix would take too long to prove fully on the workstation:

1. run the smallest truthful local proof,
2. push promptly,
3. let GitHub execute the expensive matrix,
4. debug using the real failure logs rather than guessing.

## Wrong-Layer Fix Pattern

When a user-visible defect is caused upstream:

1. identify the authoritative owner,
2. fix the owning layer first,
3. update downstream composition only where necessary,
4. avoid burying the defect in a page-local or consumer-local workaround.

## Documentation Drift Pattern

When code, commands, or operating behavior change:

1. update the central context if platform truth changed,
2. update the repo-local context if local truth changed,
3. update both if both changed,
4. add or extend validators when the pattern is durable enough to enforce.
