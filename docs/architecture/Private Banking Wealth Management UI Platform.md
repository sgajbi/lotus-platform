# Private Banking Wealth Management Platform Vision and Architecture

- Last updated: 2026-02-23
- Owner: Platform Architecture
- Status: Active working draft

## 1. Mission

Build a production-grade wealth management platform that can be sold as SaaS and also deployed in client-controlled environments (on-prem or preferred cloud), while delivering a unified advisor experience through a single UI.

## 2. Product Goal

Deliver a Unified Advisor Workbench backed by independent domain services and composed through a Python lotus-gateway.

Current repositories:
- `lotus-advise`
- `lotus-performance`
- `lotus-core`

Planned repositories:
- `advisor-ui`
- `advisor-bff`
- `wealth-platform-shared`
- `reporting-service`
- optional `platform-control-plane`

## 3. Guiding Principles

1. Standardization first
- No backward-compatibility constraints at this stage.
- Uniform architecture, naming, tooling, and deployment conventions are mandatory.

2. Pragmatic incrementalism
- Do not boil the ocean.
- Build forward in slices that demonstrate visible product progress while hardening architecture as integration surfaces emerge.

3. Single responsibility per service
- Every service owns a clear bounded context.
- Overlap is removed, not preserved.

4. Workflow-first product design
- UI is organized by advisor workflows, not backend boundaries.

5. Configurability by default
- Features, workflow gates, policy behavior, and integration settings must be tenant-configurable.

6. Operability and auditability
- Correlation IDs, lineage, deterministic artifacts, and supportability are first-class.

7. Deployment portability
- Same service contracts and architecture shape for SaaS and client-hosted modes.

## 4. Target Product Architecture

```text
[advisor-ui (Next.js)]
        |
        v
[advisor-bff (FastAPI)]
        |
        |--- [rebalance-advisory service] (lotus-advise)
        |--- [performance-analytics service] (lotus-performance)
        |--- [portfolio-core service] (lotus-core query APIs)
        |--- [reporting-service] (PDF/Excel/statements)
        |
        +--- [shared platform libraries]
              - contracts
              - observability
              - idempotency
              - configuration
```

## 5. Domain Service Responsibilities

### 5.1 Rebalance Advisory Service
- Rebalance simulation and what-if analysis
- Proposal lifecycle and approvals
- Workflow gate decisions
- Deterministic run artifacts and supportability

### 5.2 Performance Analytics Service
- TWR, MWR, contribution, attribution
- Multi-period and multi-currency analytics
- Reproducibility metadata for analytical outputs

### 5.3 Portfolio Core Service
- Ingestion and persistence
- Event-driven state processing
- Reprocessing and timeseries generation
- Foundational portfolio, position, transaction, and valuation queries

### 5.4 Reporting Service (new)
- PDF client statements
- Excel export packs
- Advisory and compliance report generation
- Template-driven rendering and artifact lineage

### 5.5 lotus-gateway
- Canonical UI contracts
- Cross-service composition and normalization
- Partial failure handling
- Caching and query shaping
- AuthN/AuthZ enforcement for UI flows

## 6. UI Module Map (Retained and Refined)

### 6.1 Advisor Workbench (MVP)
- Client context selector
- Portfolio overview cards
- Positions grid
- Performance snapshot
- Recent transactions
- Rebalance status indicator

### 6.2 Performance Analytics
- Multi-period returns
- Contribution drilldowns
- Attribution analysis
- Multi-currency decomposition

### 6.3 Advisory and Rebalance
- Simulation requests and results
- Scenario analysis
- Diagnostics and policy violations
- Proposal lifecycle, approvals, and evidence

### 6.4 Portfolio and Transactions
- Holdings transparency
- Transaction history
- Valuation and timeseries summaries

### 6.5 Reporting and Statements
- Export center
- Scheduled statement generation
- Template/version tracking

## 7. Strategic Naming and Commercial Positioning

Working external product umbrella:
- `Private Banking Wealth Platform` (working)

Recommended service/product-facing names:
- `lotus-manage Rebalance Engine` -> `Portfolio Decisioning Service`
- `lotus-performance` -> `Performance Intelligence Service`
- `lotus-core` -> `Portfolio Data Platform`
- `advisor-bff` -> `Advisor Experience API`
- `advisor-ui` -> `Advisor Workbench`
- `reporting-service` -> `Client Reporting Service`
- `wealth-platform-shared` -> `Platform Foundations`

Naming rules:
- Product-facing name for commercial materials
- Internal technical name for repository/package/runtime
- One-to-one mapping documented in architecture docs and runbooks

## 8. Standardization Program

### 8.1 Canonical Vocabulary
- `portfolio_id`, not `portfolio_number`
- `X-Correlation-Id` everywhere
- snake_case API fields
- shared status enums

### 8.2 API and Contract Standards
- shared problem-details error envelope
- shared response metadata (`correlation_id`, `as_of_date`, `contract_version`)
- cursor pagination pattern

### 8.3 Engineering Standards
- Python 3.11+
- Ruff + mypy + pytest + pre-commit
- CI pipelines in every repository
- contract testing mandatory for external API surfaces

### 8.4 DevOps Standards
- Docker-first local execution
- environment profiles: `local`, `staging`, `production`, `client-hosted`
- health checks, metrics, structured logs, tracing

## 9. Configurability Strategy

- Tenant-level feature flags
- Policy-pack based business rule controls
- Workflow and approval policy configuration
- Pluggable adapters for DB, queue, storage, and auth

Evolution:
- Phase A: shared config library
- Phase B: optional control-plane service

## 10. SaaS and Client-Hosted Model

### 10.1 SaaS
- Managed operations and upgrades
- Multi-tenant controls and observability
- Standardized deployment templates

### 10.2 Client-hosted
- Same APIs and architecture shape
- Deployable into client infrastructure
- Environment and security integration adapters

## 11. Start Strategy: lotus-gateway + UI First (Recommended)

Recommendation:
- Start with lotus-gateway and UI now, while applying backend standardization incrementally as each integration surface is touched.

Why:
- fastest visible product progress
- immediate validation of cross-service composition
- forces early decisions on auth, authorization, contracts, and config
- avoids massive upfront backend refactor before user-visible value

First workflow to implement:
- `Advisor Workbench - Portfolio Overview + Positions + Performance Snapshot + Rebalance Status`

Why this first workflow:
- touches all three backend domains
- demonstrates unified UI value quickly
- exposes core integration risks early
- gives a concrete baseline for reusable architecture patterns

## 12. Pragmatic Unification Plan (Now vs Later)

### Now (must do before/with first slice)
- lock canonical naming for new contracts
- implement lotus-gateway canonical DTOs for first workflow
- add correlation/idempotency propagation standards
- align minimum CI/tooling baseline across repos

### Next (as integration expands)
- remove overlapping endpoint ownership
- migrate shared contract/observability libraries
- add reporting service and export workflows

### Later (after core slices are stable)
- centralized control plane for multi-tenant configuration
- advanced rollout controls and policy governance
- deeper platform-wide optimization and packaging

## 13. Execution Roadmap

### Phase 0
- Approve architecture RFCs and ownership map
- lock canonical naming and API standards

### Phase 1
- scaffold `advisor-bff` and `advisor-ui`
- deliver first Advisor Workbench slice
- implementation playbook: `docs/rfcs/RFC-0020-sprint-1-lotus-workbench-vertical-slice.md`

### Phase 2
- standardize CI/CD and tooling across all repos
- introduce shared platform libraries

### Phase 3
- expand advisory workflows and deep analytics screens
- launch reporting-service MVP

### Phase 4
- introduce optional control-plane patterns
- harden SaaS and client-hosted deployment packaging

## 14. Living Document Rules

- This file is the source of truth for platform vision and architecture.
- Every major architectural decision updates this file and references the corresponding RFC.
- Changes must include rationale and implementation impact.
- Significant implementation decisions must be captured as repository-level ADRs (see RFC-0030).
- Day-to-day startup and troubleshooting commands live in:
  - `docs/operations/Local Development Runbook.md`

## 14.1 Current Strategy RFC Set (Latest)

- `RFC-0023-pas-api-product-and-governance-principles.md`
- `RFC-0024-pas-pa-dpm-integration-and-boundary-model.md`
- `RFC-0025-backend-driven-configurability-entitlements-and-workflow-control.md`
- `RFC-0026-synchronous-vs-asynchronous-integration-patterns.md`
- `RFC-0027-reporting-and-analytics-separation-strategy.md`
- `RFC-0028-ui-bff-integration-model-and-responsibility-rules.md`
- `RFC-0029-phased-integration-roadmap-pas-pa-dpm.md`
- `RFC-0030-adr-governance-and-decision-traceability.md`

## 15. Recommended Tech Stack

## 4) Recommended tech stack

## 4.1 UI (Frontend)

Core
- Next.js (App Router)
- React
- TypeScript

Data/API state
- TanStack Query

UI framework
- MUI for shell/layout/forms/common enterprise components
- AG Grid for heavy data tables (positions, transactions, exceptions, proposal lists)

Charts
- ECharts (or AG Charts if tighter AG ecosystem alignment is preferred)

Forms/validation
- React Hook Form
- Zod


