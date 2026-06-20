# Enterprise Backend Quality Baseline

Generated: `2026-06-20T10:46:23Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `717`
- Total source lines: `306214`
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
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2148 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |
| automation/New-Lotus-Service.ps1 | 1801 | .ps1 |
| automation/heartbeat_sources.py | 1672 | .py |

## Function And Complexity Hotspots

- Python functions: `1802`
- Highest measured cyclomatic complexity: `11`
- Largest Python function length: `406`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| tests/unit/test_domain_product_rollout_closure.py | test_rfc_0086_catalog_and_certification_use_repo_native_sources | 59 | 11 | 53 |
| automation/validate_trust_telemetry.py | _validate_freshness_age | 236 | 11 | 27 |
| automation/validate_shared_infra_ownership.py | _validate_lotus_core | 127 | 10 | 98 |
| automation/heartbeat_sources.py | _mesh_certification_adapter | 1194 | 10 | 75 |
| automation/validate_analytics_ui_hardening_review.py | _validate_dashboard_review | 231 | 10 | 51 |
| automation/validate_trust_telemetry.py | _validate_lineage_and_blocking | 304 | 10 | 39 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_registry_entry_list | 81 | 10 | 37 |
| automation/generate_enterprise_backend_quality_baseline.py | validate_quality_surface | 912 | 10 | 34 |
| automation/validate_repository_governance.py | normalize_actual_governance | 51 | 10 | 34 |
| automation/validate_analytics_ui_ecosystem_completion.py | _validate_supported_feature_milestones | 368 | 10 | 29 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `542`
- Collection command return code: `0`
- Collection summary: `542 tests collected in 0.56s`

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
