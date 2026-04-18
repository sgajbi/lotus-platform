# Legacy Core Wiki Migration Ledger

## Purpose

This ledger classifies historical pages from the older `lotus-core` wiki so Lotus can cleanly
separate:

- current `lotus-core` repository truth
- cross-cutting Lotus ecosystem material that belongs under `lotus-platform`
- legacy material that should be retired rather than copied forward

The source inventory reviewed came from the harvested `lotus-core.wiki.git` page set.

## Classification rules

- `Move to lotus-platform`
  the page is fundamentally cross-cutting, ecosystem-level, or platform-governance material
- `Keep in lotus-core`
  the page is core-specific technical, operational, or contract documentation
- `Retire or replace`
  the page is stale, duplicative, too sales-collateral-specific for repo docs, or superseded by
  current Lotus docs

## Page-by-page classification

| Legacy page | Classification | Rationale |
| --- | --- | --- |
| `Home.md` | Split | Keep only ecosystem/problem framing under `lotus-platform`; do not keep old PAS-centric repo positioning |
| `API-Endpoints.md` | Keep in `lotus-core` | Core service endpoint inventory is app-specific |
| `Business-Benefits.md` | Move to `lotus-platform` | Cross-cutting platform and ecosystem value narrative |
| `Business-Model-&-GTM.md` | Move to `lotus-platform` | Cross-cutting commercial framing, not core implementation truth |
| `Cashflow-Calculator.md` | Keep in `lotus-core` | Core calculator behavior |
| `Competitive-Landscape.md` | Move to `lotus-platform` | Ecosystem positioning, not core repo ownership |
| `Cost-Calculator-Service.md` | Keep in `lotus-core` | Core service-specific |
| `Customization-and-Extensibility.md` | Split | Keep core-specific extensibility in `lotus-core`; move ecosystem/platform extensibility framing to `lotus-platform` |
| `Data-Models.md` | Keep in `lotus-core` | Core data model ownership |
| `Database-Migrations.md` | Keep in `lotus-core` | Core operational detail |
| `DLQ-Replay.md` | Keep in `lotus-core` | Core runtime and ops detail |
| `Features.md` | Split | Core runtime features stay in core; generalized ecosystem/platform capability framing belongs in `lotus-platform` |
| `Future-Roadmap.md` | Split | App roadmap stays in core; ecosystem roadmap belongs in platform |
| `Infrastructure-&-DevOps.md` | Split | Shared ingress and cross-cutting platform ops belong in platform; app-local infra detail stays in core |
| `Ingestion-Service.md` | Keep in `lotus-core` | Core service-specific |
| `Internal-Architecture.md` | Keep in `lotus-core` | Core system internals |
| `Investor-Pitch.md` | Move to `lotus-platform` | Ecosystem-level commercial narrative |
| `Market-Landscape.md` | Move to `lotus-platform` | Ecosystem-level market framing |
| `Observability-&-Logging.md` | Split | Shared standards belong in platform; core-specific observability detail stays in core |
| `Operational-Runbook.md` | Split | Shared operator rules belong in platform; core incident/runbook detail stays in core |
| `Outbox-Events.md` | Keep in `lotus-core` | Core implementation and contract detail |
| `Performance-Calculator.md` | Keep in `lotus-core` or retire from core if obsolete | Depends on current core ownership after later analytics split; do not migrate to platform |
| `Persistence-Service.md` | Keep in `lotus-core` | Core service-specific |
| `Position-Calculator.md` | Keep in `lotus-core` | Core calculator behavior |
| `Production-Database-Migration-Guide.md` | Keep in `lotus-core` | Core operational detail |
| `Quick-Start-for-New-Developers.md` | Retire or replace | Superseded by platform onboarding plus current repo-specific getting-started docs |
| `Sales-FAQ.md` | Move to `lotus-platform` | Cross-cutting commercial narrative |
| `System-Context-Diagram.md` | Split | Ecosystem context belongs in platform; core service-context detail belongs in core |
| `System-Data-Flow-Diagram.md` | Keep in `lotus-core` unless redrawn as ecosystem-level flow | Current harvested page was core-topology-centric |
| `Technical-Moat-&-Differentiation.md` | Move to `lotus-platform` | Ecosystem and platform-level differentiation |
| `Testing-Guide.md` | Keep in `lotus-core` | Repo-specific testing posture |
| `Timeseries-Generator-Service.md` | Keep in `lotus-core` | Core service-specific |
| `Valuation-Calculator.md` | Keep in `lotus-core` | Core calculator behavior |
| `_Sidebar.md` | Retire | Historical navigation only; replaced by current repo-local sidebars |

## Material already migrated into `lotus-platform`

The following cross-cutting pages are now represented under `lotus-platform/wiki/`:

- [Investor Pitch](Investor-Pitch)
- [Commercial Model and GTM](Commercial-Model-and-GTM)
- [Sales FAQ](Sales-FAQ)

Related ecosystem framing also now lives in:

- [Overview](Overview)
- [Architecture](Architecture)
- [Integrations](Integrations)
- [Roadmap](Roadmap)

## Follow-up work

1. add a matching cleanup ledger or update pass in `lotus-core` so the remaining app-specific wiki
   material is rewritten against current core ownership
2. redraw any ecosystem-level diagrams under `lotus-platform` instead of leaving them implied by
   core-era topology
3. retire or archive obsolete PAS-era wording whenever it still appears in legacy pages or cloned
   wiki repos
