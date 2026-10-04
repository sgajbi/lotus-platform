# Understanding composite performance and reports

A composite groups actual portfolios managed under a defined strategy and approved membership policy. A report should explain who was assessed, why portfolios were included or excluded, which financial method was used and which versions were approved. A research cohort or model track has a separate identity; it does not silently become an actual investment record.

This guide describes the full product target and the current evidence boundary. The [reader map and ledger](README.md) identify current committed-source observations and unassessed requirements. The complete configurable external/Core/hybrid product, 40 analytical families and 12 report products are required outcomes, not a statement that all are available today. Institutional policies need approval before official activation.

## Intended close workflow

1. Identify the firm, strategy/composite, reporting month, native/display currency, fee view and intended audience.
2. Obtain the complete expected population and approved source/policy versions. Missing source rows remain unresolved; they are not quietly treated as excluded portfolios.
3. Review membership and all applicable reasons. A normal policy exclusion is a business outcome; missing facts for an eligible portfolio can block the result.
4. Calculate using the approved method, validate the source and population, and reconcile weights and contributions.
5. Review and approve the exact result/series versions. Freeze the selected authority without stopping later periods.
6. Assemble Excel from one retained report manifest. Show as-of/source-cut dates, fee/currency, method, approved/provisional status, unavailable values and retained version references.
7. If a correction is required, review the affected periods/metrics/reports and issue a new approved version and recipient notice. Previous publications remain retrievable.

Delivery prioritizes Performance correctness and operations/support APIs, then Excel. UI and PDF are downstream capabilities; every full-target requirement remains indexed in the [specification](requirements.md).

## What the numbers mean

Two eligible portfolios with beginning assets 100 and 300 earn +10% and −2%. Their weights are 25% and 75%, with +2.5 and −1.5 percentage-point contributions. The composite return is **+1%**. A subsequent +2% month produces **3.02%** cumulatively: 1.01 × 1.02 − 1. These are [OR-01 and OR-02 specification examples](worked-examples.md#or-01), not a claim of executed API or deployed support.

If a mandatory middle month is missing, the full requested return is **unavailable**. Combining only two surviving months into 3.02% would misrepresent the requested interval. [OR-18](worked-examples.md#or-18) specifies a null result with `REQUIRED_PERIOD_UNAVAILABLE`; the deployed API's typed response needs its own verified contract.

Annual member dispersion measures the spread across full-year portfolio returns; volatility measures variation through time in a series. Year-end count, full-year population and risk sample count are different. Gross, actual-net and model-net returns have distinct approved fee authority. Native-currency translation is not hedged performance. [Worked examples](worked-examples.md) explain these distinctions; implemented formulas and APIs stay with Performance/Risk.

## Interpreting source and availability

| Report condition | Required interpretation |
| --- | --- |
| Provisional | Observation windows or approval remain incomplete; identify evaluated-through date and outstanding actions. |
| Frozen / approved | Exact period/result/fee/currency/method/version selected; do not infer that all other periods are approved. |
| Policy-excluded | Explain the rule and period; valid earlier historical contribution remains preserved. |
| Missing eligible-member source | Data-blocked or undetermined; do not calculate an official survivor-only result. |
| Imported composite-only history | Reproduce the attested composite series at its declared depth; authentic historical member analytics are unavailable. |
| Insufficient risk history | Show the metric-specific reason and sample; do not turn an unavailable statistic into zero. |
| Restated | Identify replacement authority, reason, affected reports and earlier retained publication. |

## API and Excel boundaries

The Platform registry currently names the existing Performance composite product. It does not establish every proposed operations API as supported. Use the [committed Performance guide](https://github.com/sgajbi/lotus-performance/blob/4ffad93e7c57789d3521ace5205bf682a6513995/docs/guides/composite_materialization.md) for the bounded existing materialization surface and its limits. New external imports, annual dispersion, model fees, official freeze operations and Excel families require their issue-backed implementation and independent acceptance evidence.

Logical examples in the target and this guide are not requests to send to an invented endpoint. Actual API examples must match source-owned route/serializer behavior. Excel cells must carry authoritative numeric results and the same manifest/availability used by API outputs; embedded analytical formulas are labelled separately and cannot silently change official returns.

## Approval and evidence

Firm methodology/compliance owners approve applicable GIPS policies and disclosures. Passing software tests does not establish firm compliance, and independent professional verification is separate. Capacity and recovery targets need deployment-specific evidence. This documentation foundation reports neither production readiness nor institutional acceptance.
