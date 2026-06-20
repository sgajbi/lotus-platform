# Enterprise Backend Quality Baseline

Generated: `2026-06-20T04:28:21Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `711`
- Total source lines: `300169`
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

- Python functions: `1321`
- Highest measured cyclomatic complexity: `34`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/validate_analytics_ui_rollout_readiness.py | validate_rollout_readiness | 25 | 34 | 134 |
| automation/generate_domain_product_onboarding.py | validate_domain_product_onboarding_bundle | 802 | 32 | 258 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | validate_consumer_contract_with_context | 592 | 31 | 128 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | validate_trust_metadata_registry | 183 | 29 | 105 |
| automation/domain_product_discovery.py | validate_source_manifest | 207 | 29 | 104 |
| automation/validate_mesh_slo_policies.py | validate_mesh_slo_policies | 55 | 29 | 97 |
| automation/validate_analytics_ui_observability_contract.py | _validate_supported_feature_keys | 18 | 28 | 147 |
| automation/validate_analytics_ui_ecosystem_completion.py | _validate_slices | 241 | 26 | 111 |
| automation/validate_mesh_access_policies.py | validate_mesh_access_policies | 53 | 25 | 96 |
| automation/validate_agent_engineering_contracts.py | validate_agent_engineering_contracts | 178 | 24 | 132 |

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
- Collection summary: `510 tests collected in 0.65s`

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
