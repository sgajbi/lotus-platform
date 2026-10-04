# Composite performance documentation

The [complete product target](requirements.md) is LOTUS-CMP-001 v2.0. The [current evidence ledger](implementation-ledger.v1.json) is the single machine-readable authority for requirement status; the human view below is its checked projection. A registered product or route is a bounded observation, not proof of the whole target.

Delivery is governed by [Platform #923](https://github.com/sgajbi/lotus-platform/issues/923); [#924](https://github.com/sgajbi/lotus-platform/issues/924) delivers this foundation only. Correct Performance calculations and operations/support APIs come first, authoritative Excel results next, and UI downstream. Every advanced requirement remains in scope.

| Reader | Start here |
| --- | --- |
| Client or product reviewer | [Concepts, workflow and report interpretation](client-guide.md) |
| Engineer or methodology owner | [RFC-0110: ownership, journey and delivery](../../rfcs/RFC-0110-composite-performance-product-and-delivery-foundation.md) |
| QA or calculation reviewer | [18 worked specification examples](worked-examples.md) |
| Requirement owner | [Full requirements, formulas and options](requirements.md) and [coverage data](implementation-ledger.v1.json) |
| Provenance reviewer | [Source manifest](source-manifest.v1.json) |

## Current evidence and limits

At Platform commit `1315743b23048b58a7eb7cf3d473693130812d25`, `CompositePerformanceAnalytics:v1` and `/performance/composites/twr` are already declared in the [domain product registry](../../platform-contracts/domain-data-products/lotus-performance-products.v1.json). The ledger records exact Performance and Manage committed-source observations. These observations do not promote any complete target requirement. All 321 requirement rows begin `NOT_ASSESSED`; owners must attach a scoped source assessment and independent executable evidence before changing state.

Existing domain truth remains in [Performance's documentation map](https://github.com/sgajbi/lotus-performance/blob/4ffad93e7c57789d3521ace5205bf682a6513995/docs/technical/composite-performance-documentation-map.md) and [bounded materialization guide](https://github.com/sgajbi/lotus-performance/blob/4ffad93e7c57789d3521ace5205bf682a6513995/docs/guides/composite_materialization.md). This foundation preserves proposed methods and supplies traceability; it does not replace those source-owned methods or certify a deployment.

The ledger indexes 321 CMP requirements, 48 individual source requirements, 18 unresolved source decisions, 40 analytics families, 12 report products, 105 acceptance scenarios, 18 numerical oracles, 16 institutional decisions, 10 SLO targets and S/M/L/D/H workloads. Unsupported histories, authority, fees, approvals and samples remain visible; no release exclusion removes them.

## Provenance and editorial boundary

Four neutral inputs are archived byte-for-byte as plain text or JSON. Their original references, instruction language and dated claims are archival content; follow this reader map and RFC for current navigation. The two withheld research/front-door inputs are inventoried by original filename, SHA-256 and withheld status without publishing their content or private locations. Screenshots and the sample workbook were not validated. The public requirements edit only navigation and comparative-claim wording, with every substitution recorded in the manifest. No formula or supported option is removed.

## Updating evidence

A requirement row carries exact origin, repository/component, logical contract/API status, method/policy and dependent decisions, implementation state, source assessment, separate unit/integration/target-environment evidence, migration impact, documentation, risk, owner and next action. `null` API/test references mean no runtime binding has been supplied. Planned issue references identify related work, not proof of full issue scope or completion.

Use only the CMP-TRC-002 states. A source assessment must pin repository, full commit, path, scope and review evidence. `VERIFIED_IN_TEST` requires actual executable test evidence; `VERIFIED_IN_TARGET_ENVIRONMENT` additionally requires scoped target-environment acceptance. `BLOCKED_ON_APPROVED_POLICY_OR_SOURCE` must name the blocking decision/source. Update the single ledger and its human projection together. Register semantic changes before implementation; approval is never inferred from a passing document guard.

## Validation from the Platform repository root

Require Python 3.12 or newer (`python -V`). Install the pinned Platform automation dependencies through the repository-native lane bootstrap. The document guard uses the Python standard library. These checks validate documentation retention and consistency; they do not run a financial engine.

Windows PowerShell:

```powershell
python automation/validate_composite_documentation_foundation.py
python -m pytest tests/unit/test_composite_documentation_foundation.py -q
python automation/validate_engineering_context_system.py
python codex/skills/lotus-readme-wiki-governance/scripts/audit_wiki_quality.py --wiki-dir wiki --changed-page Composite-Performance.md --changed-page RFC-Index.md
powershell -ExecutionPolicy Bypass -File automation/Invoke-PlatformRepoChecks.ps1 -Lane feature
```

Linux/macOS:

```bash
python automation/validate_composite_documentation_foundation.py
python -m pytest tests/unit/test_composite_documentation_foundation.py -q
python automation/validate_engineering_context_system.py
python codex/skills/lotus-readme-wiki-governance/scripts/audit_wiki_quality.py --wiki-dir wiki --changed-page Composite-Performance.md --changed-page RFC-Index.md
pwsh -File automation/Invoke-PlatformRepoChecks.ps1 -Lane feature
```

Repository protected PR and exact-main lanes remain required. Before merge use `automation/Sync-RepoWikis.ps1 -CheckOnly -Repository lotus-platform -AllowUnpublishedSourceChanges`; after merge publish with `-Publish -Repository lotus-platform`, then strict `-CheckOnly -Repository lotus-platform` and committed-blob/full-file-set parity. Do not publish from an unreviewed branch.

## Requirement coverage: generated human view

This projection contains no second authority. Exact source ranges, individual baseline crosswalks, planned test bindings and current observations are in the ledger.

<!-- coverage:start -->
| Requirement | Proposed owner | Implementation state | Related issue |
| --- | --- | --- | --- |
| [CMP-GEN-001](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-002](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-003](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-004](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-005](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-006](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-007](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GEN-008](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-001](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-002](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-003](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-004](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-005](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-006](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-007](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-INV-008](requirements.md#1-product-outcomes-and-invariants) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ARC-001](requirements.md#2-architecture-and-ownership) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ARC-002](requirements.md#2-architecture-and-ownership) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ARC-003](requirements.md#2-architecture-and-ownership) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ARC-004](requirements.md#2-architecture-and-ownership) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ARC-005](requirements.md#2-architecture-and-ownership) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-001](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-002](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-003](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-004](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-005](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DOM-006](requirements.md#3-domain-model-time-and-states) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAT-001](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-002](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-003](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-004](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-005](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-006](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-007](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-008](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-009](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CAT-010](requirements.md#4-composite-catalogue-and-lifecycle) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-CFG-001](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-002](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-003](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-004](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-005](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-006](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-007](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-008](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-009](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-010](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-011](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CFG-012](requirements.md#5-configurable-engines-and-policy-management) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SRC-001](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-002](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-003](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-004](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-005](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-006](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-007](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-008](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-009](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-010](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-011](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-SRC-012](requirements.md#6-external-core-and-hybrid-data) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-001](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-002](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-003](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-004](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-005](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-006](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-007](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-008](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-009](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-010](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-MIG-011](requirements.md#7-migration-and-source-cutover) | lotus-performance | NOT_ASSESSED | [lotus-performance#607](https://github.com/sgajbi/lotus-performance/issues/607), [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540) |
| [CMP-ELG-001](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-002](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-003](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-004](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-005](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-006](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-007](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-008](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-009](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-ELG-010](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-001](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-002](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-003](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-004](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-005](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-FLW-006](requirements.md#8-eligibility-assignment-and-re-entry) | lotus-manage | NOT_ASSESSED | [lotus-manage#714](https://github.com/sgajbi/lotus-manage/issues/714), [lotus-manage#778](https://github.com/sgajbi/lotus-manage/issues/778) |
| [CMP-RET-001](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-002](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-003](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-004](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-015](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-WGT-001](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-WGT-002](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-WGT-003](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-WGT-004](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-WGT-005](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-005](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-006](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-007](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-008](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-009](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-010](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-011](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-012](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-013](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-RET-014](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-performance#540](https://github.com/sgajbi/lotus-performance/issues/540), [lotus-performance#543](https://github.com/sgajbi/lotus-performance/issues/543) |
| [CMP-MWR-001](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MWR-002](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MWR-003](requirements.md#9-return-engines-and-financial-methods) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-BMK-001](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-BMK-002](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-BMK-003](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-BMK-004](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-FX-001](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-FX-002](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-FX-003](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-FEE-001](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-FEE-002](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-FEE-003](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-FEE-004](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-FEE-005](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-FEE-006](requirements.md#10-benchmarks-currencies-and-fees) | lotus-performance | NOT_ASSESSED | [lotus-performance#609](https://github.com/sgajbi/lotus-performance/issues/609) |
| [CMP-CTL-001](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-002](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-003](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-004](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-005](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-006](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-007](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-008](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-009](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-010](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-011](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-012](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-013](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-014](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-015](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-016](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-017](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-018](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-019](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-CTL-020](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-001](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-002](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-003](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-004](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-005](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-ERR-006](requirements.md#11-freezing-overrides-correction-and-restatement) | lotus-performance | NOT_ASSESSED | [lotus-performance#610](https://github.com/sgajbi/lotus-performance/issues/610) |
| [CMP-GIP-001](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-002](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-003](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-004](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-005](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-006](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-007](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-008](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-009](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-010](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-011](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-012](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-013](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-014](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-015](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-016](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-017](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-018](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-019](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-020](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-021](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-022](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-023](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-024](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-GIP-025](requirements.md#12-gips-aware-control-framework) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-001](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-002](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-003](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-004](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-001](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-002](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-003](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-004](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-performance#608](https://github.com/sgajbi/lotus-performance/issues/608) |
| [CMP-AN-005](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-006](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-007](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-008](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-009](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-010](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-011](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-012](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-013](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-014](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-015](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-016](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-017](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-018](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-019](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-020](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-021](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-022](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-023](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-024](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-025](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-026](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-027](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-manage | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-028](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-manage | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-029](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-030](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-031](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-manage | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-032](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-033](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-034](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-risk | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-035](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-036](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-037](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-038](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-039](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-AN-040](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-005](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-006](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-007](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-008](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-009](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-010](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ANA-011](requirements.md#13-composite-analytics-catalogue-and-formulas) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CON-001](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CON-002](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CON-003](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CON-004](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ATT-001](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ATT-002](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ATT-003](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ATT-004](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-ATT-005](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAR-001](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAR-002](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAR-003](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAR-004](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-CAR-005](requirements.md#14-contribution-attribution-and-carve-outs) | lotus-performance | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-001](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-002](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-003](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-004](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-005](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-006](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-007](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-008](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-009](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-LIN-010](requirements.md#15-lineage-and-reproducibility) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-RPT-001](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-002](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-003](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-004](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-005](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-006](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-007](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-008](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-009](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-010](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-011](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-012](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-013](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-RPT-014](requirements.md#16-reports-and-distribution) | lotus-report | NOT_ASSESSED | [lotus-report#417](https://github.com/sgajbi/lotus-report/issues/417) |
| [CMP-API-001](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-002](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-003](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-004](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-005](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-006](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-API-007](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-gateway#820](https://github.com/sgajbi/lotus-gateway/issues/820) |
| [CMP-EVT-001](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-EVT-002](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-EVT-003](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-EVT-004](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-OPS-001](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-OPS-002](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-OPS-003](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-OPS-004](requirements.md#17-api-events-and-operational-workflows) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-001](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-002](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-003](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-004](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-005](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-UX-006](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-workbench | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-001](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-002](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-003](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-004](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-005](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-MNT-006](requirements.md#18-workbench-configuration-experience-and-maintainability) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-001](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-002](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-003](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-004](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-005](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-006](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-007](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-008](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-009](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SCL-010](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SEC-001](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SEC-002](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SEC-003](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SEC-004](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-SEC-005](requirements.md#19-scalability-resilience-and-security) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-001](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-002](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-003](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-004](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-005](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-006](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TST-007](requirements.md#20-acceptance-scenarios-and-numerical-oracles) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TRC-001](requirements.md#21-decision-and-traceability-registers) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TRC-002](requirements.md#21-decision-and-traceability-registers) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-TRC-003](requirements.md#21-decision-and-traceability-registers) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DON-001](requirements.md#22-definition-of-done-and-reference-sources) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DON-002](requirements.md#22-definition-of-done-and-reference-sources) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DON-003](requirements.md#22-definition-of-done-and-reference-sources) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DON-004](requirements.md#22-definition-of-done-and-reference-sources) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
| [CMP-DON-005](requirements.md#22-definition-of-done-and-reference-sources) | lotus-platform | NOT_ASSESSED | [lotus-platform#923](https://github.com/sgajbi/lotus-platform/issues/923) |
<!-- coverage:end -->
