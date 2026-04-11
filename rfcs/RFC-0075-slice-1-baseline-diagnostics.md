# RFC-0075 Slice 1 Baseline Diagnostics

- RFC: `RFC-0075-canonical-front-office-portfolio-seed-and-demo-validation-system.md`
- Slice: 1, RFC approval and baseline diagnostics
- Status: Complete for slice-1 approval scope
- Captured: 2026-04-11
- Captured by: Codex local diagnostics

## Approval And Decision Record

The user approved moving ahead with Slice 1 on 2026-04-11 and explicitly requested that existing unstaged platform changes be included.

Approved or recorded for implementation planning:

1. Canonical portfolio ID: `PB_SG_GLOBAL_BAL_001`.
2. Canonical benchmark ID: `BMK_PB_GLOBAL_BALANCED_60_40`.
3. Default date policy: fixed-date demo seed, with `2026-04-10` proposed as the canonical as-of date pending final confirmation during Slice 2/3 implementation.
4. Cleanup posture: full Docker cleanup is allowed when explicitly requested; current local Docker state has already been cleaned to no containers, images, or volumes.
5. Screenshot posture: demo-ready screenshots must be blocked until backend and UI validation pass; diagnostic screenshots may be captured with a `diagnostic-` prefix.
6. Unsupported panels must not be faked; they must be implemented through backend contracts or shown as truthful partial/unavailable states.
7. `lotus-manage`, `lotus-report`, `lotus-advise`, and `lotus-ai` participate in canonical startup and backend checks even if workbench does not consume every capability yet.

## Environment Baseline

Current Docker state after approved cleanup:

1. containers: none
2. local images: none
3. volumes: none

Implication: the next implementation slice starts from a clean local runtime baseline and must rebuild state through governed startup and seed automation, not through stale Docker artifacts.

## GitHub CI And PR Pulse

A lightweight `gh pr list` pulse was run across:

- `sgajbi/lotus-platform`
- `sgajbi/lotus-core`
- `sgajbi/lotus-performance`
- `sgajbi/lotus-risk`
- `sgajbi/lotus-gateway`
- `sgajbi/lotus-workbench`
- `sgajbi/lotus-advise`
- `sgajbi/lotus-manage`
- `sgajbi/lotus-report`
- `sgajbi/lotus-ai`

Result: no open PRs were returned during this pulse, so there were no active PR checks to fix-forward in this slice.

## Baseline Failure Register

| Finding | Current Evidence | Owning Repository | Slice To Resolve |
|---|---|---|---|
| Timestamped smoke portfolios polluted lookup data | Prior live-stack investigation found repeated `PORT_SMOKE_*` portfolios caused by timestamped smoke IDs and missing cleanup. Current Docker cleanup removed local persisted pollution. | `lotus-core` | Slice 3 |
| Derived state readiness can pass too early | Prior investigation found position timeseries reached the current window while portfolio analytics reference still resolved a stale `performance_end_date`. | `lotus-core` | Slice 4 |
| Gateway/workbench performance detail can be empty while upstream performance has rows | Prior direct `lotus-performance` workspace-summary call returned contribution and attribution rows for the canonical portfolio, while gateway-facing workbench details returned empty detail rows. | `lotus-gateway`, `lotus-workbench` | Slice 5 and Slice 6 |
| Optional manage posture can degrade overview | Prior workbench overview returned `DPM_SUPPORTABILITY_POSTGRES_DSN_REQUIRED` from `lotus-manage`. | `lotus-manage`, `lotus-platform` | Slice 2 and Slice 6 |
| Stale stack ambiguity can confuse canonical hostnames | Prior Docker state had both canonical `lotus-*` containers and older `pbwm-platform-*` containers. Current Docker cleanup removed both. | `lotus-platform`, `lotus-workbench` | Slice 2 |
| Evidence surface support is not fully contract-backed | Prior investigation found gateway evidence capability reported unavailable because lineage/evidence surfaces are not exposed by the current gateway contract. | `lotus-gateway`, `lotus-performance`, `lotus-workbench` | Slice 6 |

## Panel Classification Baseline

| Workbench Surface | Baseline Classification | Notes |
|---|---|---|
| Portfolio summary | Supported and must be populated | Canonical seed must populate portfolio, positions, cash, allocation, activity, and readiness cards. |
| Performance summary | Supported and must be populated | Requires current portfolio timeseries, benchmark data, and summary workspace contract. |
| Performance analysis | Supported and must be populated | Contribution and attribution detail must be non-empty where the backend contract says supported. |
| Advisor brief | Supported or partial pending service checks | Slice 1 has not restarted services after Docker cleanup; Slice 2 must validate advisory startup. |
| Risk summary and sub-panels | Supported and must be populated | Requires risk snapshot, drawdown, concentration, rolling risk, and historical attribution validation. |
| Evidence | Partial or unavailable until contract decision | Must remain truthful; no UI-only fake evidence. |
| Manage/report/AI product-adjacent checks | Startup and backend health required | Workbench consumption may be partial, but startup checks are in scope. |

## Slice 1 Review

This slice intentionally does not implement seed economics or cross-repository product fixes. It records the implementation baseline, confirms the governed runtime direction, and keeps later work assigned to the correct owning slices.

Quality improvements made before closing Slice 1:

1. Existing unstaged platform work was reviewed, tested, and committed separately as governed front-office runtime routing.
2. RFC-0075 baseline diagnostics are now captured as a durable artifact instead of remaining chat-only memory.
3. Docker state was verified clean before moving into future startup and seed work.
4. GitHub PR status was checked without blocking slice progress.

## Next Slice Readiness

Slice 2 may start after this baseline is accepted. Slice 2 should standardize Docker cleanup, ingress, startup, DSN posture, and startup evidence before changing seed economics.

