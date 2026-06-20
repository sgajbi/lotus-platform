# Enterprise Backend Quality Baseline

Generated: `2026-06-20T08:18:06Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `716`
- Total source lines: `304326`
- Python files: `157`
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

- Python functions: `1671`
- Highest measured cyclomatic complexity: `13`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/delegation_task_ledger.py | update_delegated_task_status | 180 | 13 | 35 |
| automation/core_performance_returns_series_validation.py | _run_validation | 22 | 12 | 225 |
| automation/domain_product_certification.py | _build_consumer_certification | 105 | 12 | 108 |
| automation/validate_mesh_slo_policies.py | evaluate_mesh_slo_violations | 235 | 12 | 102 |
| automation/heartbeat_sources.py | _lotus_ai_queue_item_attention | 1300 | 12 | 77 |
| automation/core_performance_cross_app_validation.py | _evaluate_expected_posture | 417 | 12 | 68 |
| automation/review_analytics_ui_canonical_proof.py | review_canonical_proof | 393 | 12 | 67 |
| automation/review_analytics_ui_ecosystem_proof.py | _validate_journeys | 140 | 12 | 54 |
| automation/validate_analytics_ui_entitlement_certification.py | _validate_implementation_evidence | 274 | 12 | 42 |
| automation/validate_analytics_ui_ecosystem_hardening.py | _validate_api_and_proof | 143 | 12 | 39 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `518`
- Collection command return code: `0`
- Collection summary: `518 tests collected in 0.52s`

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
