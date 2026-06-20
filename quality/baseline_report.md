# Enterprise Backend Quality Baseline

Generated: `2026-06-20T09:27:51Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `717`
- Total source lines: `305386`
- Python files: `158`
- PowerShell files: `63`
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

- Python functions: `1743`
- Highest measured cyclomatic complexity: `12`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/review_analytics_ui_canonical_proof.py | _resolve_live_summary | 95 | 12 | 28 |
| automation/validate_heartbeat_contracts.py | validate_heartbeat_suppressions | 624 | 12 | 28 |
| automation/review_analytics_ui_ecosystem_proof.py | review_ecosystem_proof | 531 | 11 | 100 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | validate_producer_contract | 753 | 11 | 80 |
| automation/heartbeat_sources.py | _collect_delegated_task_attention | 778 | 11 | 73 |
| automation/validate_analytics_ui_hardening_review.py | _validate_telemetry_field_review | 82 | 11 | 57 |
| tests/unit/test_domain_product_rollout_closure.py | test_rfc_0086_catalog_and_certification_use_repo_native_sources | 59 | 11 | 53 |
| automation/validate_analytics_ui_ecosystem_completion.py | _validate_gap_matrix | 603 | 11 | 47 |
| automation/domain_product_discovery.py | find_products | 64 | 11 | 45 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_dependency_migration_posture | 932 | 11 | 44 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `526`
- Collection command return code: `0`
- Collection summary: `526 tests collected in 0.58s`

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
