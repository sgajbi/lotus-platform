# Enterprise Backend Quality Baseline

Generated: `2026-09-05T23:34:48Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `906`
- Total source lines: `366417`
- Python files: `237`
- PowerShell files: `69`
- Markdown files: `413`

## Largest Files

| Path | Lines | Type |
| --- | --- | --- |
| platform-contracts/api-vocabulary/lotus-manage-api-vocabulary.v1.json | 79939 | .json |
| platform-contracts/api-vocabulary/lotus-advise-api-vocabulary.v1.json | 36232 | .json |
| platform-contracts/api-vocabulary/lotus-core-api-vocabulary.v1.json | 23952 | .json |
| platform-contracts/api-vocabulary/lotus-performance-api-vocabulary.v1.json | 16326 | .json |
| automation/New-Lotus-Service.ps1 | 5950 | .ps1 |
| platform-contracts/api-vocabulary/lotus-risk-api-vocabulary.v1.json | 5120 | .json |
| platform-contracts/domain-data-products/lotus-core-products.v1.json | 3138 | .json |
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2525 | .py |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | 1908 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |

## Function And Complexity Hotspots

- Python functions: `3118`
- Highest measured cyclomatic complexity: `55`
- Largest Python function length: `903`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/gate_liveness_audit.py | _make_invoked_targets | 208 | 55 | 142 |
| automation/validate_bank_readiness_control_catalog.py | _validate_controls | 250 | 24 | 72 |
| automation/gate_liveness_audit.py | blocking_workflow_invocations | 492 | 22 | 69 |
| codex/skills/gh-address-comments/scripts/fetch_comments.py | fetch_all | 204 | 22 | 69 |
| automation/resolve_canonical_cash_evidence.py | cash_evidence_from_overview | 37 | 20 | 69 |
| automation/validate_platform_stack.py | _validate_security | 273 | 18 | 63 |
| automation/validate_workflow_pipeline_exit_codes.py | iter_steps | 60 | 18 | 63 |
| codex/skills/gh-fix-ci/scripts/inspect_pr_checks.py | render_results | 466 | 18 | 43 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_dependency_failure_posture_conditions | 1319 | 17 | 66 |
| automation/validate_platform_stack.py | _validate_observability | 183 | 16 | 88 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `1243`
- Collection command return code: `0`
- Collection summary: `1243 tests collected in 1.19s`

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
