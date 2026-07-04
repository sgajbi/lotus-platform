# Private Banking Analytics UI

Use this reference when building or reviewing Lotus Workbench product surfaces, especially portfolio overview, performance, risk, advisory, reporting, observability, and operational panels. It adapts the useful finance/dashboard guidance from UI UX Pro Max into Lotus-specific, gateway-backed private banking UI rules.

## Contents

1. [Design Posture](#design-posture)
2. [Workbench Screen Anatomy](#workbench-screen-anatomy)
3. [Layout Patterns](#layout-patterns)
4. [Visual System](#visual-system)
5. [Analytics And Chart Selection](#analytics-and-chart-selection)
6. [Data Display Rules](#data-display-rules)
7. [State And Evidence](#state-and-evidence)
8. [Interaction Quality](#interaction-quality)

## Design Posture

- Optimize for advisor trust, decision clarity, supportability, and auditability over visual novelty.
- Prefer restrained, information-dense enterprise layouts: navigation, filters, primary workspace, secondary context, and evidence drawer.
- Use private banking language: portfolio, mandate, benchmark, allocation, exposure, attribution, drawdown, contribution, proposal, evidence, lineage, supportability, and readiness.
- Avoid fintech spectacle: glassmorphism, neon, generic AI purple gradients, decorative glow, excessive dark-mode drama, and marketing hero copy inside product surfaces.
- Let density come from hierarchy and alignment, not from small unreadable text. Dense must still be scannable.

## Workbench Screen Anatomy

Every analytics screen or panel should make these items visible or one click away:

1. portfolio identity, client/household context where supported, governed portfolio id, and selected scope,
2. as-of date, reporting period, benchmark, currency, and mandate or policy context,
3. primary metric or exception, with trend/variance and clear unit,
4. explanation path: contribution, attribution, exposure, drawdown, concentration, or lifecycle cause,
5. source/evidence posture: freshness, lineage, supportability, calculation status, partial/unavailable reason,
6. allowed next action: drill down, review proposal, export evidence, rerun, acknowledge, or resolve.

## Layout Patterns

- Use a stable shell with persistent portfolio context and predictable global navigation.
- Start each route with operational context, not a marketing hero.
- Prefer a summary-to-detail structure: headline metrics, analytical breakdown, holdings/events table, evidence or diagnostics.
- Use a 12-column grid or equivalent predictable layout for desktop analytics; collapse to a single-column workflow on mobile.
- Keep filters close to the data they affect and preserve filter state when navigating back.
- Use drawers or detail panes for evidence and lineage so the primary workspace remains readable.
- Avoid dashboards made only of unrelated cards. Repeated cards are acceptable only for comparable KPIs or repeated portfolio/holding rows.

## Visual System

- Default to neutral light surfaces for front-office analytics unless the existing Workbench theme requires dark mode.
- Suitable palette direction: trust navy, professional blue, slate neutrals, restrained gold/amber for attention, semantic red/green only for loss/risk/success where domain-correct.
- Test dark mode separately when present; do not invert light tokens mechanically.
- Use one enterprise-grade sans family from the product system. If choosing anew, prefer Inter, IBM Plex Sans, Source Sans 3, or an existing Workbench font before decorative pairings.
- Use tabular numerals for values, deltas, currencies, weights, returns, risk figures, dates, and ranks.
- Keep iconography functional and consistent. Use icons to improve scanning, not to decorate headings.

## Analytics And Chart Selection

- Use line charts for time-series returns, drawdowns, rolling risk, NAV, and value history.
- Use bar charts for allocation, contribution, attribution, comparison, and ranked exposures.
- Use waterfall charts for contribution, attribution, cash-flow, and variance decomposition when order and sign matter.
- Use bullet charts for KPI-versus-target, benchmark, mandate, supportability, or SLA-style compact comparisons.
- Use heat maps only for matrix relationships such as sector/region/risk bucket concentration; include readable labels and table fallback.
- Use decomposition tree or expandable hierarchy only when parent-child contribution is real and sourced.
- Avoid gauges for portfolio analytics unless a single target/threshold is central; bullet charts usually scale better.
- Avoid pie/donut charts for more than five categories or when precise comparison matters.
- Avoid 3D charts, decorative radar charts, and color-only risk maps in production product UI.

## Data Display Rules

- Always show units and basis: currency, percent, basis points, weight, count, date, period, or benchmark.
- Round consistently and preserve domain meaning. Do not mix decimal precision across comparable figures.
- Show positive/negative direction with sign, label, and icon or shape; do not rely on red/green alone.
- Use locale-aware number, currency, and date formatting through the existing stack utilities.
- For large tables, support sorting, filtering, sticky headers, column sizing, and horizontal handling without breaking page layout.
- Pair charts with exact values through labels, tooltips, details panes, or accessible table alternatives.
- Distinguish no data, not entitled, not supported, stale, partial, calculation failed, and upstream unavailable states.

## State And Evidence

Each Workbench panel should intentionally handle:

- loading: skeleton shaped like the final content, not a generic spinner-only blank,
- ready: data, context, and supported action visible,
- empty: explain the missing business condition and what can be done,
- partial: show available data and name the missing source or capability,
- stale: show freshness and safe interpretation,
- error: show recovery path, correlation id or support reference where available,
- permission blocked: state entitlement or workflow gate without leaking restricted data.

For governed screenshots and canonical surfaces, do not capture demo-ready evidence until canonical API, calculation, and panel validation pass.

## Interaction Quality

- Keep primary actions explicit: review, drill down, compare, export, rerun, approve, reject, acknowledge, resolve.
- Provide visible drill-down paths from summary figures to holdings, transactions, methodology, or evidence.
- Preserve scroll, tab, filter, and selected-row state on return.
- Put destructive or compliance-sensitive actions behind confirmation and show audit/supportability outcome.
- Make rows, charts, and controls keyboard accessible. Hover-only explanations are not enough.
- For live or refreshing operational views, show last refresh, connection/degraded posture, and pause/refresh control when motion or streaming is present.

## Accessibility And Responsiveness

- Keep normal text at WCAG AA contrast or better; financial red/green must meet contrast and have redundant labels.
- Ensure touch targets are at least 44px by 44px for primary mobile interactions.
- Do not hide critical context on mobile; reorder into a workflow, then allow drill-down.
- Avoid truncating portfolio names, instrument names, exception causes, or action labels unless full text is accessible.
- Respect reduced motion. Animations should clarify state changes, not add ambience.

## Anti-Patterns To Reject

- UI figures without as-of date, benchmark, currency/unit, or source posture.
- Generic headings such as "Stats", "Insights", "Overview", or "Widget" when a domain term exists.
- Decorative trust badges or AI/trust state not backed by gateway or platform evidence.
- Chart galleries that do not answer an advisor workflow question.
- Positive/negative meaning encoded by color alone.
- Dark dashboards that reduce table readability or make financial red/green ambiguous.
- Local UI mocks of unsupported backend behavior.
