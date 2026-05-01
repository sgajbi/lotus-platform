# Analytics UI Observability

This page summarizes the current RFC-0108 implementation-backed analytics UI observability posture
for operators, demo preparation, and engineering handoff. Deep technical truth remains in
[`rfcs/RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md`](../rfcs/RFC-0108-front-office-analytics-ui-observability-and-operational-posture.md),
the platform contracts under [`context/contracts/`](../context/contracts/), and the
[Analytics UI Observability Runbook](../docs/operations/analytics-ui-observability-runbook.md).

## Current Supported Scope

| Layer | Implementation-backed status | Primary evidence |
| --- | --- | --- |
| Workbench browser and BFF | Supported Portfolio, Intake, Performance, Risk, reporting operator, archive metadata, legacy advisor Workbench, and Data Products reads emit bounded panel, hydration, API, attention, and supportability posture where implemented. | Workbench PRs #118 through #129, canonical proof for `PB_SG_GLOBAL_BAL_001`, and the governed Workbench runtime flow. |
| Gateway | Selected analytics fan-out paths, protected diagnostics, performance/risk source supportability, portfolio readiness, manage action-register, report evidence-surface, AI advisor-brief, advisory supportability, and advisor-brief caller-context/audit proof are preserved with bounded labels and no sensitive payload fields. | Gateway PRs #166 through #172, Gateway PRs #176 and #177, and protected diagnostics OpenAPI evidence. |
| Performance backend | TWR, MWR, contribution, and attribution supportability emit bounded source-owned supportability state; the RFC-0108 backend freshness metric is implemented; capability publication remains enabled when any implemented performance supportability operation is enabled. | lotus-performance PRs #138, #139, and #140. |
| Risk backend | Risk calculate, drawdown, rolling metrics, historical attribution, and concentration supportability emit bounded source-owned supportability state and the RFC-0108 backend freshness metric. | lotus-risk PRs #107 and #108. |
| Platform observability | Dashboard, alert rules, runbook anchors, ecosystem proof, hardening certification, final closure, and wiki publication requirements are machine-reviewed. | `analytics-ui-observability-contract.json`, ecosystem completion/proof/hardening/final-closure contracts, and platform validators. |

## Runtime Flow

```mermaid
flowchart LR
    Workbench[Workbench observed surfaces] --> BFF[Workbench BFF caller context]
    BFF --> Gateway[Gateway analytics experience APIs]
    Gateway --> Perf[lotus-performance supportability]
    Gateway --> Risk[lotus-risk supportability]
    Gateway --> Other[core/manage/report/render/archive/advise/ai supportability]
    Perf --> Metrics[bounded metric families]
    Risk --> Metrics
    Other --> Metrics
    Metrics --> Platform[Platform dashboards, alerts, runbooks, and proof validators]
    Platform --> Operators[Operators and demo-readiness evidence]
```

## Advisor Brief Review Action Observability

Workbench PR #134 adds implementation-backed observability for the Advisor Brief review-action
mutation. The browser still sends the mutation through the Workbench BFF and Gateway; Workbench
records the mutation as the bounded `performance-advisor-brief-review-action` observed surface with
operation `performance.workspace.advisor-brief.review-action`. Browser-originated metric events are
accepted only by the same-origin Workbench `/api/metrics/events` route and are exported through
`/api/metrics`.

```mermaid
sequenceDiagram
    participant Browser as Advisor browser
    participant Workbench as Workbench UI and BFF
    participant Gateway as Gateway review-action API
    participant MetricsEvents as /api/metrics/events
    participant Metrics as /api/metrics
    participant Logs as Gateway logs and traces

    Browser->>Workbench: Submit Advisor Brief review action
    Workbench->>Gateway: POST review action with caller context
    Gateway-->>Workbench: Bounded success or failure status
    Workbench->>MetricsEvents: Bounded api_request metric event
    MetricsEvents-->>Metrics: In-process metric registry update
    Gateway-->>Logs: correlation_id, request_id, trace_id, bounded operation log
```

The proof excludes portfolio, client, advisor, correlation, free-form reason, request-body, and
response-body values from metric labels. Mutation failures are surfaced through bounded Workbench
API errors instead of raw Gateway response bodies. Local proof included focused Workbench tests,
full Workbench tests, typecheck, lint, live canonical validation for `PB_SG_GLOBAL_BAL_001`,
`/api/metrics` export inspection, Gateway log/trace review, green GitHub CI, and Workbench wiki
publication commit `8bec78e`.

## Gold-Pass Evidence

The 2026-05-01 gold-pass canonical run passed for `PB_SG_GLOBAL_BAL_001` with benchmark
`BMK_PB_GLOBAL_BALANCED_60_40`. The platform evidence bundle is
`output/front-office-qa/canonical-front-office-qa-20260501-140359.json`; the runtime transcript is
`output/front-office-qa/canonical-front-office-qa-20260501-140359.log`; screenshots are under
`output/rfc-0108-gold-pass-transcript-qa/`.

The run proved DNS, Gateway readiness, Workbench portfolio/performance routes, manage/report/
archive/render readiness, integration capabilities, Gateway workspace/capabilities/overview,
performance summary, risk summary, advisor brief, and browser screenshots for seven panels. The
evidence panel is intentionally `truthfully_degraded` because full RFC-0079 evidence scope remains
outside the current implemented RFC-0108 claim.

Canonical QA now writes `output/front-office-qa/latest.log` alongside `latest.json` and
`latest.md`. Use the transcript during demo preparation and production-readiness review to confirm
seed readiness progression, retry warnings, and teardown behavior instead of relying only on the
structured summary.

Critical screenshot review found one product-presentation follow-up: the performance summary driver
content could clip horizontally in the desktop capture. That follow-up is now implementation-backed
by Workbench PR #132, merged at `4285d5c00910e8347f47976a4aec73a45c422724`, with Workbench wiki
publication commit `764f778`. The follow-up hardened the Summary layout, labeled compact Horizon
support values, added truthful partial states for ready-with-empty attribution/contribution detail
contracts, and passed live canonical Workbench validation for `PB_SG_GLOBAL_BAL_001` with refreshed
screenshots under `lotus-workbench/output/rfc-0108-performance-layout-hardening-qa/`.

The certified read-path entitlement gap is now closed for the current RFC-0108 certified paths.
Workbench PR #133, merged at `90a3d54e81a92e6b2bad8584edb25122cf3c2a81`, proves bounded
permission-blocked UI states for performance Summary, Risk Review, and Advisor Brief. The live
proof passed canonical Workbench validation and platform QA on 2026-05-01 with evidence manifest
`output/front-office-qa/canonical-front-office-qa-20260501-155832.md`; Gateway and Performance logs
were inspected for bounded audit/correlation posture. Workbench wiki publication commit `f523dbb`
records the operator-facing permission-blocked analytics proof rules.

## Residual Boundary

RFC-0108 is closed for current implementation-backed claims, not for every possible future
front-office surface. Full RFC-0079 risk/evidence scope and complete Workbench all-supported-surface
promotion remain planned until separately implemented and certified. Do not use
`lotus-platform/platform-stack` as product-surface proof; canonical demo screenshots and populated
front-office validation must use the governed `lotus-workbench` runtime.

The caller-context entitlement certification contract now records implementation evidence for the
current certified Workbench read paths. Gateway PR #159 proves bounded selected analytics
read allow/deny audit records for performance and risk summary paths; Workbench PR #131 proves BFF
caller-context defaults; Gateway PR #174 proves performance-summary caller-context enforcement,
PR #175 proves risk-summary caller-context enforcement, PR #176 proves advisor-brief caller-context
rejection on read and review-action routes, PR #177 proves bounded advisor-brief read allow/deny
audit records, and Workbench PR #133 proves permission-blocked UI behavior. Future new certified
read paths must provide the same implementation-backed proof before promotion.

## Operator Use

Use this page to orient the current supported observability posture, then move to:

- [Operations Runbook](Operations-Runbook) for alert triage and caller-context certification rules.
- [RFC Index](RFC-Index) for RFC ordering, residual boundaries, and linked implementation history.
- [Validation and CI](Validation-and-CI) for platform check lanes and wiki publication gates.
