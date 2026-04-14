# RFC-0081 Slice 5: Gateway Composition Foundation and Contract Hardening Evidence

- RFC: `RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md`
- Slice: `Slice 5: Gateway Composition Foundation and Contract Hardening`
- Date: 2026-04-12
- Status: Completed and reviewed

## Scope implemented

Slice 5 implemented the first gateway-side composition hardening for the shell bootstrap contract in
`lotus-gateway`.

The implementation stayed intentionally narrow:

1. extend the existing `/api/v1/platform/capabilities` experience contract instead of creating a
   parallel bootstrap route,
2. add explicit shell-bootstrap metadata for:
   - shell structure,
   - workspace supportability,
   - freshness posture,
   - evidence posture,
   - versioning posture,
   - caching posture,
3. keep existing capability, workflow-flag, and policy-diagnostic behavior intact,
4. avoid any `lotus-workbench` UI wiring change because the new fields are additive and truthful.

## Gateway implementation evidence

- Repo: `lotus-gateway`
- Branch: `codex/rfc-0081-slice-5-gateway-composition-foundation`
- Commit: `7aae028ee1fac574a0b02e26a7d5313b15e36347`
- Commit message: `Harden shell bootstrap capability contract`

## Files changed

1. `src/app/contracts/platform_capabilities.py`
2. `src/app/services/platform_capabilities_service.py`
3. `tests/contract/test_platform_capabilities_contract.py`
4. `tests/integration/test_platform_capabilities_router.py`
5. `tests/unit/test_platform_capabilities_service.py`

## What changed

### 1. Added a typed `shellBootstrap` contract to the normalized platform-capabilities payload

The normalized payload now includes a structured `shellBootstrap` object with:

1. shell-level supportability,
2. shell-level freshness metadata,
3. shell-level evidence metadata,
4. shell-level versioning metadata,
5. shell-level caching posture,
6. a governed `workspaces` list for:
   - `Portfolio`
   - `Performance`
   - `Risk`
   - `Proposal`
   - `Advisory`

### 2. Added workspace descriptors with truthful shell-facing metadata

Each workspace descriptor now carries:

1. `id`, `label`, and `href`,
2. `enabled`,
3. `supportability`,
4. `freshness`,
5. `evidence`,
6. `versioning`,
7. `caching`

This gives the shell a governed composition contract without forcing it to infer banker-facing
readiness from coarse lower-level capability flags alone.

### 3. Preserved explicit degradation semantics

When an upstream source is unavailable:

1. shell bootstrap reports `partial`,
2. affected workspace descriptors report `partial`,
3. evidence metadata preserves the failing source identity,
4. versioning still exposes known policy versions from healthy sources.

This keeps the gateway aligned with RFC-0081’s requirement for truthful supportability and partial
state delivery.

### 4. Kept routing and UI behavior unchanged

No `lotus-workbench` change was required in slice 5 because:

1. the route stayed `/api/v1/platform/capabilities`,
2. the new gateway fields are additive,
3. no shell or workspace action semantics changed.

## Validation commands run

In `C:\Users\Sandeep\projects\lotus-gateway`:

1. `python -m pytest tests/unit/test_platform_capabilities_service.py tests/integration/test_platform_capabilities_router.py tests/contract/test_platform_capabilities_contract.py`
2. `python -m mypy src`
3. `python -m ruff check .`
4. `git diff --check`

All passed.

## Consciously not changed

1. no workbench UI consumer change,
2. no new gateway route,
3. no route rename,
4. no backend business workflow change,
5. no cache implementation was introduced; only contract posture was made explicit.

## Follow-up implications

Slice 6 and later shell consumers can now adopt the gateway `shellBootstrap` contract incrementally
without relying on transitional navigation inference.
