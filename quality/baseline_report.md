# Enterprise Backend Quality Baseline

Generated: `2026-06-20T03:02:58Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `684`
- Total source lines: `295785`
- Python files: `149`
- PowerShell files: `62`
- Markdown files: `334`

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
| automation/New-Lotus-Service.ps1 | 1747 | .ps1 |
| rfcs/RFC-0104-batch-reporting-scheduler-concurrency-and-recovery.md | 1655 | .md |

## Function And Complexity Hotspots

- Python functions: `1271`
- Highest measured cyclomatic complexity: `83`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/validate_engineering_context_system.py | validate_engineering_context_system | 32 | 83 | 365 |
| automation/validate_analytics_ui_observability_contract.py | validate_contract | 18 | 50 | 324 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | validate_producer_contract | 290 | 50 | 213 |
| automation/validate_heartbeat_contracts.py | validate_heartbeat_status | 153 | 46 | 138 |
| automation/validate_analytics_ui_ecosystem_completion.py | _validate_supported_features | 309 | 44 | 202 |
| automation/validate_supported_claim_register.py | validate_supported_claim_register | 47 | 39 | 129 |
| automation/heartbeat_sources.py | _lotus_ai_adapter | 885 | 38 | 226 |
| automation/heartbeat_sources.py | _delegated_task_ledger_adapter | 557 | 35 | 140 |
| automation/validate_analytics_ui_rollout_readiness.py | validate_rollout_readiness | 25 | 34 | 134 |
| automation/generate_domain_product_onboarding.py | validate_domain_product_onboarding_bundle | 802 | 32 | 258 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `502`
- Collection command return code: `0`
- Collection summary: `502 tests collected in 1.19s`

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
