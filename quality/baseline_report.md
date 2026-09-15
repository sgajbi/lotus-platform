# Enterprise Backend Quality Baseline

Generated: `2026-09-15T05:38:28Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `976`
- Total source lines: `388612`
- Python files: `263`
- PowerShell files: `69`
- Markdown files: `419`

## Largest Files

| Path | Lines | Type |
| --- | --- | --- |
| platform-contracts/api-vocabulary/lotus-manage-api-vocabulary.v1.json | 79939 | .json |
| platform-contracts/api-vocabulary/lotus-advise-api-vocabulary.v1.json | 36232 | .json |
| platform-contracts/api-vocabulary/lotus-core-api-vocabulary.v1.json | 23952 | .json |
| platform-contracts/api-vocabulary/lotus-performance-api-vocabulary.v1.json | 16326 | .json |
| automation/New-Lotus-Service.ps1 | 6046 | .ps1 |
| platform-contracts/api-vocabulary/lotus-risk-api-vocabulary.v1.json | 5120 | .json |
| platform-contracts/domain-data-products/lotus-core-products.v1.json | 3138 | .json |
| tests/unit/test_engineering_context_system_contract.py | 2823 | .py |
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2525 | .py |
| tests/unit/test_auto_merge_releasability_validator.py | 1915 | .py |

## Function And Complexity Hotspots

- Python functions: `3880`
- Highest measured cyclomatic complexity: `82`
- Largest Python function length: `903`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/validate_auto_merge_releasability.py | _main_releasability_has_source_pinned_assertion | 721 | 82 | 258 |
| automation/validate_auto_merge_releasability.py | has_fatal_main_fetch | 754 | 55 | 152 |
| automation/gate_liveness_audit.py | _make_invoked_targets | 208 | 55 | 142 |
| automation/validate_workflow_pipeline_exit_codes.py | _scan_shell | 440 | 53 | 215 |
| automation/check_branch_protection_policy.py | validate_policy_document | 82 | 35 | 75 |
| automation/audit_main_gate_coverage.py | main | 259 | 31 | 179 |
| automation/validate_bank_readiness_control_catalog.py | _validate_controls | 250 | 24 | 72 |
| automation/verify_principal_credential.py | resolve_principal | 245 | 22 | 106 |
| automation/gate_liveness_audit.py | blocking_workflow_invocations | 492 | 22 | 69 |
| codex/skills/gh-address-comments/scripts/fetch_comments.py | fetch_all | 204 | 22 | 69 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `1872`
- Collection command return code: `0`
- Collection summary: `1872 tests collected`

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
