# Enterprise Backend Quality Baseline

Generated: `2026-07-13T12:12:10Z`

Repository: `lotus-platform`

This is the pre-refactor measurement baseline for the enterprise backend refactor. It is generated
from repository source files and is report-only until individual signals are proven deterministic,
low-noise, and suitable for a blocking CI lane.

## Scope

Included roots: `automation, codex, context, docs, platform-contracts, platform-stack, platform-standards, rfcs, tests, wiki`

Excluded parts: `.git, .mypy_cache, .pytest_cache, .ruff_cache, .venv, .venv-platform-automation, __pycache__, generated, output`

## Code Size

- Source files: `789`
- Total source lines: `328554`
- Python files: `181`
- PowerShell files: `66`
- Markdown files: `384`

## Largest Files

| Path | Lines | Type |
| --- | --- | --- |
| platform-contracts/api-vocabulary/lotus-manage-api-vocabulary.v1.json | 79939 | .json |
| platform-contracts/api-vocabulary/lotus-advise-api-vocabulary.v1.json | 36232 | .json |
| platform-contracts/api-vocabulary/lotus-core-api-vocabulary.v1.json | 23952 | .json |
| platform-contracts/api-vocabulary/lotus-performance-api-vocabulary.v1.json | 16326 | .json |
| automation/New-Lotus-Service.ps1 | 5393 | .ps1 |
| platform-contracts/api-vocabulary/lotus-risk-api-vocabulary.v1.json | 5120 | .json |
| platform-contracts/domain-data-products/lotus-core-products.v1.json | 3072 | .json |
| tests/unit/test_rfc_0084_domain_data_product_contracts.py | 2227 | .py |
| rfcs/RFC-0081-lotus-workbench-ui-uplift-and-advisory-lifecycle-integration.md | 1818 | .md |
| automation/heartbeat_sources.py | 1735 | .py |

## Function And Complexity Hotspots

- Python functions: `2043`
- Highest measured cyclomatic complexity: `30`
- Largest Python function length: `884`

| Path | Function | Line | Complexity | Lines |
| --- | --- | --- | --- | --- |
| codex/skills/lotus-skill-context-governance/scripts/audit_lotus_skills.py | audit | 60 | 30 | 97 |
| automation/validate_lifecycle_authority_contracts.py | validate_decision | 97 | 22 | 89 |
| codex/skills/lotus-readme-wiki-governance/scripts/audit_wiki_quality.py | audit_wiki | 199 | 19 | 64 |
| automation/validate_lifecycle_authority_contracts.py | validate_key_discovery | 188 | 19 | 33 |
| tests/unit/test_lotus_platform_standards_docs.py | test_client_demo_certification_standard_is_audience_ready_and_evidence_backed | 52 | 15 | 74 |
| automation/mesh_certification_gate.py | _iter_default_telemetry_paths | 170 | 14 | 34 |
| codex/skills/lotus-ci-enforcement-governance/scripts/endpoint_example_parity.py | _resolve_pointer | 199 | 12 | 17 |
| codex/skills/lotus-ci-enforcement-governance/scripts/endpoint_example_parity.py | _compare | 239 | 11 | 77 |
| codex/skills/lotus-ci-enforcement-governance/scripts/endpoint_example_parity.py | _parse_normalization_rule | 105 | 11 | 55 |
| automation/mesh_certification_gate.py | _issue_from_live_certification | 416 | 11 | 38 |

## Tooling Baseline

| Tool | Available | Return Code | Summary |
| --- | --- | --- | --- |
| ruff | no | None | tool not installed |
| mypy | no | None | tool not installed |
| bandit | no | None | tool not installed |
| pip_audit | no | None | tool not installed |

## Test Baseline

- Unit tests collected: `662`
- Collection command return code: `0`
- Collection summary: `662 tests collected in 0.88s`

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
