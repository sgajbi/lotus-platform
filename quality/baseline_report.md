# Enterprise Backend Quality Baseline

Generated: `2026-06-20T08:51:10Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `717`
- Total source lines: `304865`
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

- Python functions: `1706`
- Highest measured cyclomatic complexity: `12`
- Largest Python function length: `393`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/review_analytics_ui_canonical_proof.py | review_canonical_proof | 393 | 12 | 67 |
| automation/review_analytics_ui_ecosystem_proof.py | _validate_journeys | 140 | 12 | 54 |
| automation/validate_analytics_ui_entitlement_certification.py | _validate_implementation_evidence | 274 | 12 | 42 |
| automation/validate_analytics_ui_ecosystem_hardening.py | _validate_api_and_proof | 143 | 12 | 39 |
| automation/heartbeat_sources.py | _append_delegated_task_overlap_attention | 853 | 12 | 37 |
| automation/review_analytics_ui_ecosystem_proof.py | _validate_screenshots | 216 | 12 | 37 |
| automation/validate_engineering_context_system.py | _validate_agents_operating_contract | 197 | 12 | 34 |
| automation/validate_mesh_access_policies.py | _validate_allowed_consumer | 231 | 12 | 33 |
| automation/validate_supported_claim_register.py | _validate_register_header | 47 | 12 | 31 |
| automation/review_analytics_ui_canonical_proof.py | _resolve_live_summary | 95 | 12 | 28 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `523`
- Collection command return code: `0`
- Collection summary: `523 tests collected in 0.57s`

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
