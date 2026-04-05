# Canonical Simulation Authority and Domain Evaluation Pattern

- Status: Proposed target state
- Date: 2026-04-05
- Owners: lotus-platform architecture
- Applies To: `lotus-core`, `lotus-advise`, `lotus-risk`, downstream consumer apps

## Summary

The Lotus platform should operate with one canonical simulation authority for projected portfolio state.

That authority is `lotus-core`.

Domain services may still expose domain-facing simulation APIs, but they should not maintain separate engines for the underlying projected portfolio state.

This note defines the target pattern:

1. `lotus-core` owns canonical scenario execution and projected state generation.
2. `lotus-risk` consumes canonical baseline and projected state to run risk analytics.
3. `lotus-advise` owns advisory proposal orchestration, decisioning, suitability, workflow gating, artifact generation, and lifecycle control.
4. Domain services compile intent into canonical scenario inputs and evaluate domain rules on top of canonical projected state rather than re-owning a second state engine.

## Current Reality

### `lotus-core`

`lotus-core` already owns:

1. simulation sessions,
2. simulation change persistence,
3. projected positions and summary endpoints,
4. generic baseline and simulation snapshot contracts for downstream services.

Evidence:

- `src/services/query_control_plane_service/app/routers/simulation.py`
- `src/services/query_service/app/services/simulation_service.py`
- `src/services/query_service/app/services/core_snapshot_service.py`
- `docs/RFCs/RFC 046A - Lotus Core Simulation Session Contract for Proposal Sandbox.md`
- `docs/RFCs/RFC 058 - Generic Core Snapshot Contract for Stateful and Simulation Consumers.md`

### `lotus-risk`

`lotus-risk` already follows the intended platform pattern in simulation mode.

It does not maintain an independent portfolio-state simulator. It creates or reuses a `lotus-core` simulation session, applies changes there, requests a projected snapshot, and then runs risk analytics on the returned canonical state.

Evidence:

- `src/app/services/concentration_engine.py`
- `src/app/integrations/lotus_core_client.py`

### `lotus-advise`

`lotus-advise` owns the right domain-facing contract but still carries a local advisory simulation engine for canonical state projection and valuation behavior.

That local engine currently performs:

1. trade and cash-flow application,
2. funding and FX intent generation,
3. before/after portfolio state construction,
4. reconciliation,
5. rule evaluation,
6. drift and suitability scanning,
7. workflow gate input generation.

Evidence:

- `src/core/advisory_engine.py`
- `src/core/advisory/orchestration.py`
- `src/api/services/advisory_simulation_service.py`
- `docs/rfcs/RFC-0006-lotus-advise-target-operating-model-and-integration-architecture.md`
- `docs/rfcs/RFC-0007-advisory-proposal-simulate-mvp.md`

## Problem

The platform currently risks keeping two separate authorities for projected portfolio state:

1. `lotus-core` for generic simulation and risk-driven simulation workflows,
2. `lotus-advise` for advisory proposal evaluation.

That is the wrong long-term banking-grade pattern.

If multiple engines independently own projected state semantics, the estate will eventually drift on:

1. cash and FX handling,
2. valuation totals,
3. projected positions,
4. replay evidence,
5. deterministic parity across advisory and risk workflows.

## Decision

The Lotus platform standard is:

1. one canonical projected-state simulation authority: `lotus-core`,
2. many domain evaluators on top of canonical state: `lotus-risk`, `lotus-advise`, and future domain apps.

### Ownership boundaries

#### `lotus-core` owns

1. canonical scenario input execution,
2. projected portfolio state,
3. projected positions, totals, and valuation context,
4. deterministic replay/versioning of scenario execution,
5. platform simulation governance and integration contracts.

#### `lotus-advise` owns

1. advisory proposal APIs,
2. proposal and workspace orchestration,
3. stateful context resolution for advisory workflows,
4. advisory-only intent construction and funding policy decisions,
5. suitability interpretation,
6. workflow gates,
7. proposal artifacts, approvals, and lifecycle evidence.

#### `lotus-risk` owns

1. risk analytics,
2. concentration, scenario, factor, and other risk measures,
3. interpretation of canonical projected state into risk outputs.

## Required pattern for domain simulation APIs

A domain app may expose a simulation endpoint when the consumer contract is domain-specific.

That is valid.

What is not valid is duplicating the underlying projected-state engine.

Therefore:

1. `lotus-advise` may keep `/advisory/proposals/simulate` as the advisory-facing contract.
2. `lotus-risk` may keep simulation mode in its risk APIs.
3. Both must use `lotus-core` for canonical projected state.

## Execution model

The target model for advisory workflows is:

1. `lotus-advise` resolves stateless or stateful advisory context into a canonical advisory simulation request.
2. `lotus-advise` compiles advisory proposal intent into canonical scenario semantics.
3. `lotus-core` executes canonical advisory simulation and returns projected state plus deterministic lineage.
4. `lotus-advise` applies advisory-only interpretation and workflow policy on top of the returned canonical result.
5. `lotus-risk`, when invoked, runs analytics on the same canonical projected state or compatible canonical snapshot lineage.

## Design rules

1. No second portfolio-state engine in domain apps.
2. No compatibility aliases for simulation ownership language.
3. Canonical projected-state semantics must be replayable and auditable from `lotus-core` lineage.
4. Domain apps may add domain interpretation, not silent valuation divergence.
5. Parity tests are mandatory before cutover from a legacy local engine.
6. Cutover is complete only when runtime authority has moved and fallback drift is no longer the default posture.

## Delivery standard

Migration from a local domain engine to `lotus-core` authority should follow this sequence:

1. document the target state and ownership,
2. enhance `lotus-core` to cover the missing domain-grade simulation semantics,
3. run parity tests against the incumbent domain engine,
4. cut over the domain app to `lotus-core`,
5. retire or quarantine the old local engine so it no longer acts as runtime authority.

## Acceptance criteria

This architecture pattern is achieved when:

1. `lotus-core` is the only runtime authority for projected portfolio state,
2. `lotus-advise` no longer relies on a default local projected-state engine in normal runtime,
3. `lotus-risk` and `lotus-advise` can trace their simulation-driven behavior to compatible `lotus-core` lineage,
4. parity evidence exists for the advisory cutover,
5. docs, capabilities, and operational readiness language across repos reflect the same ownership model.

## Follow-On RFC

The detailed remaining work to reach the full gold-standard architecture is defined in:

- [RFC-canonical-simulation-authority-golden-standard-completion.md](C:/Users/Sandeep/projects/lotus-platform/docs/architecture/RFC-canonical-simulation-authority-golden-standard-completion.md)
