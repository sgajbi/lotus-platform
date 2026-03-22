# RFC-0069: lotus-ai Shared AI Platform Service

- Status: Proposed
- Date: 2026-03-22
- Owners: lotus-platform governance

## Objective

Introduce `lotus-ai` as a dedicated shared AI platform service for Lotus applications.

`lotus-ai` exists to provide common AI infrastructure, governance, and reusable capabilities without taking ownership of domain business logic from the other Lotus applications.

## Decision

Create `lotus-ai` as a separate repository and bounded context.

`lotus-ai` is the shared AI utility plane for the Lotus estate. It powers AI features used by other Lotus apps, while each domain service remains responsible for its own business semantics, user workflows, and deterministic decision logic.

## Why a Separate Service

Putting all AI code directly into every Lotus app would create:

1. duplicated prompt logic,
2. duplicated safety and redaction logic,
3. inconsistent auditability,
4. inconsistent model routing and cost control,
5. avoidable cross-repo drift.

Putting all AI product behavior into one central service would create the opposite problem:

1. `lotus-ai` would start owning business logic it should not own,
2. domain context would move away from the teams and services that understand it,
3. deterministic decision services would become too dependent on a central AI monolith.

The correct split is:

1. `lotus-ai` owns shared AI infrastructure.
2. Each Lotus app owns its own domain-facing AI behavior.

## lotus-ai Owns

1. LLM provider integration and model routing.
2. Prompt registry and prompt versioning.
3. Shared retrieval over approved Lotus knowledge sources.
4. AI safety controls:
   - redaction
   - role-aware access checks
   - action classification
   - output labeling
5. AI audit logging, usage telemetry, and cost controls.
6. Shared async AI run orchestration.
7. Evaluation and regression tooling for AI features.
8. Reusable AI task APIs such as explanation, summarization, extraction, classification, and structured generation.

## lotus-ai Does Not Own

1. Portfolio construction logic.
2. Trade recommendation truth.
3. Approval or consent truth.
4. Risk or performance calculation truth.
5. Reporting source-of-truth data.
6. UI orchestration or workflow ownership.
7. Canonical portfolio, transaction, valuation, or analytics state.

`lotus-ai` must not become the system of record for business decisions.

## Domain Ownership Model

### lotus-core

May use `lotus-ai` for:

1. supportability summarization,
2. ingestion anomaly triage,
3. lineage and incident explanation.

Still owns:

1. canonical portfolio data,
2. operational truth,
3. ingestion and query semantics.

### lotus-performance and lotus-risk

May use `lotus-ai` for:

1. analytics commentary,
2. explanation of attribution or risk outputs,
3. support-facing diagnostics summaries.

Still own:

1. analytical methods,
2. calculations,
3. domain contracts.

### lotus-advise and lotus-manage

May use `lotus-ai` for:

1. plain-English proposal/rebalance explanations,
2. workflow summaries,
3. reviewer notes,
4. natural-language-to-draft intent capture.

Still own:

1. proposal and rebalance semantics,
2. workflow state,
3. policy and approval rules,
4. deterministic decision outputs.

### lotus-gateway and lotus-workbench

May use `lotus-ai` for:

1. user-facing copilot experiences,
2. cross-service AI explanations,
3. lifecycle-oriented assistant flows.

Still own:

1. product orchestration,
2. UI contract shaping,
3. session and frontend workflow design.

## Integration Model

The preferred pattern is:

1. a Lotus app prepares a structured context payload it owns,
2. that app calls `lotus-ai` for a bounded AI task,
3. `lotus-ai` returns a governed result with audit metadata,
4. the calling app remains accountable for presenting and applying the result.

Cross-service experiences should normally be orchestrated by `lotus-gateway`, not by `lotus-ai` directly reaching into every service without contract ownership.

## Initial lotus-ai Scope

Version 1 of `lotus-ai` should focus on:

1. AI gateway and provider abstraction.
2. Prompt registry and versioned task definitions.
3. Retrieval over Lotus docs, RFCs, standards, and schemas.
4. AI audit logging and evaluation harnesses.
5. Safe explanation-oriented and drafting-oriented APIs.

## Deferred Scope

The following are explicitly deferred:

1. autonomous portfolio decisioning,
2. automatic trade execution,
3. autonomous approval transitions,
4. unrestricted code-execution agents inside production workflows,
5. replacing deterministic business services with LLM-driven logic.

## Repository and Platform Registration

`lotus-ai` is now a registered Lotus repository under `lotus-platform` governance and should be treated like the other backend repos for:

1. automation registration,
2. standards conformance,
3. CI governance,
4. branch protection,
5. cross-repo architecture review.

## Acceptance Criteria

1. `lotus-ai` repository exists locally and remotely.
2. `lotus-ai` is registered in platform automation metadata.
3. `lotus-ai` documents what it does and does not own.
4. The platform architecture explicitly states that domain AI behavior remains owned by the calling Lotus app.
