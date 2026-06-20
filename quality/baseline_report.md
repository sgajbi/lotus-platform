# Enterprise Backend Quality Baseline

Generated: `2026-06-20T07:24:39Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `711`
- Total source lines: `303152`
- Python files: `153`
- PowerShell files: `62`
- Markdown files: `356`

## Largest Files

| Path | Lines | Type |
| --- | --- | --- |
| platform-contracts/api-vocabulary/lotus-manage-api-vocabulary.v1.json | 79939 | .json |
| platform-contracts/api-vocabulary/lotus-advise-api-vocabulary.v1.json | 36232 | .json |
| platform-contracts/api-vocabulary/lotus-core-api-vocabulary.v1.json | 23952 | .json |
| platform-contracts/api-vocabulary/lotus-performance-api-vocabulary.v1.json | 14219 | .json |
| platform-contracts/api-vocabulary/lotus-risk-api-vocabulary.v1.json | 5120 | .json |
| platform-contracts/domain-data-products/lotus-core-products.v1.json | 2701 | .json |
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2058 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |
| automation/New-Lotus-Service.ps1 | 1801 | .ps1 |
| rfcs/RFC-0104-batch-reporting-scheduler-concurrency-and-recovery.md | 1655 | .md |

## Function And Complexity Hotspots

- Python functions: `1598`
- Highest measured cyclomatic complexity: `14`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/validate_analytics_ui_observability_contract.py | _validate_telemetry_contract | 629 | 14 | 90 |
| platform-contracts/api-vocabulary/validate_api_vocabulary_catalog.py | validate_cross_app | 73 | 14 | 56 |
| automation/validate_repository_hygiene.py | validate_repository_hygiene | 69 | 14 | 52 |
| automation/generate_live_trust_certification.py | _evaluate_snapshot | 67 | 13 | 104 |
| automation/validate_analytics_ui_observability_contract.py | _validate_observation_boundaries | 721 | 13 | 80 |
| automation/heartbeat_sources.py | _delegated_task_ledger_adapter | 892 | 13 | 71 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_product_registry_references | 482 | 13 | 65 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_product_lineage_policy | 549 | 13 | 49 |
| automation/render_cross_app_workflow_summary.py | _render_single | 70 | 13 | 48 |
| automation/validate_analytics_ui_ecosystem_completion.py | _matrix_feature_implementation_rule | 418 | 13 | 37 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `510`
- Collection command return code: `0`
- Collection summary: `510 tests collected in 0.52s`

## Security Baseline

- Sensitive-keyword review candidate sample size: `50`
- Candidate interpretation: `Keyword matches are planning signals and require human review before being treated as findings.`

## OpenAPI And API Governance

`lotus-platform` does not own a business-domain API. API governance improvement applies to service
scaffolding, validators, vocabulary contracts, generated inventories, and cross-repository
certification evidence.

## Baseline Decision

No new scanner dependency is introduced in this slice. The next refactor slices should either
promote a deterministic signal into a blocking gate or record why it remains report-only.
