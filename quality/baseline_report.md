# Enterprise Backend Quality Baseline

Generated: `2026-08-25T04:11:10Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `894`
- Total source lines: `359082`
- Python files: `228`
- PowerShell files: `69`
- Markdown files: `410`

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
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2425 | .py |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | 1854 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |

## Function And Complexity Hotspots

- Python functions: `2868`
- Highest measured cyclomatic complexity: `24`
- Largest Python function length: `903`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| automation/validate_bank_readiness_control_catalog.py | _validate_controls | 250 | 24 | 72 |
| codex/skills/gh-address-comments/scripts/fetch_comments.py | fetch_all | 204 | 22 | 69 |
| automation/validate_platform_stack.py | _validate_security | 273 | 18 | 63 |
| codex/skills/gh-fix-ci/scripts/inspect_pr_checks.py | render_results | 466 | 18 | 43 |
| automation/validate_platform_stack.py | _validate_observability | 183 | 16 | 88 |
| tests/unit/test_lotus_platform_standards_docs.py | test_client_demo_certification_standard_is_audience_ready_and_evidence_backed | 52 | 15 | 74 |
| platform-contracts/domain-data-products/validate_domain_data_product_contracts.py | _validate_dependency_failure_posture_conditions | 1273 | 15 | 58 |
| automation/validate_deployment_promotion_manifest.py | _validate_environments | 122 | 15 | 50 |
| automation/validate_auto_merge_releasability.py | _merged_pr_dispatch_violations | 226 | 15 | 30 |
| codex/skills/lotus-app-issue-discovery/scripts/validate_issue_discovery_skill.py | validate | 64 | 14 | 124 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `1011`
- Collection command return code: `0`
- Collection summary: `1011 tests collected in 1.46s`

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
