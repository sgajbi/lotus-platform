# Enterprise Backend Quality Baseline

Generated: `2026-06-21T12:04:07Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `720`
- Total source lines: `309662`
- Python files: `158`
- PowerShell files: `63`
- Markdown files: `359`

## Largest Files

| Path | Lines | Type |
| --- | --- | --- |
| platform-contracts/api-vocabulary/lotus-manage-api-vocabulary.v1.json | 79939 | .json |
| platform-contracts/api-vocabulary/lotus-advise-api-vocabulary.v1.json | 36232 | .json |
| platform-contracts/api-vocabulary/lotus-core-api-vocabulary.v1.json | 23952 | .json |
| platform-contracts/api-vocabulary/lotus-performance-api-vocabulary.v1.json | 14219 | .json |
| platform-contracts/api-vocabulary/lotus-risk-api-vocabulary.v1.json | 5120 | .json |
| automation/New-Lotus-Service.ps1 | 3253 | .ps1 |
| platform-contracts/domain-data-products/lotus-core-products.v1.json | 2701 | .json |
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2148 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |
| automation/heartbeat_sources.py | 1735 | .py |

## Function And Complexity Hotspots

- Python functions: `1848`
- Highest measured cyclomatic complexity: `10`
- Largest Python function length: `525`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_registry_entry_list | 81 | 10 | 37 |
| automation/generate_enterprise_backend_quality_baseline.py | validate_quality_surface | 928 | 10 | 34 |
| automation/validate_analytics_ui_ecosystem_completion.py | _validate_supported_feature_milestones | 368 | 10 | 29 |
| automation/delegation_task_ledger.py | _validate_output_evidence_refs | 287 | 10 | 20 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | validate_contract_directory | 1381 | 9 | 102 |
| automation/core_performance_cross_app_validation.py | _evaluate_performance_requests | 306 | 9 | 75 |
| automation/validate_dev_ingress_smoke.py | validate_dev_ingress_smoke | 94 | 9 | 64 |
| automation/domain_product_certification.py | _append_dependency_issues | 148 | 9 | 57 |
| automation/heartbeat_sources.py | _wiki_publication_adapter | 1085 | 9 | 56 |
| automation/prune_merged_remote_branches.py | classify_branch | 58 | 9 | 52 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `553`
- Collection command return code: `0`
- Collection summary: `553 tests collected in 1.08s`

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
