# Profile Reference

Profiles are defined in `automation/task-profiles.json`.

## Commonly Used Profiles

| Profile | Purpose | Typical Trigger |
|---|---|---|
| `platform-alignment` | Fast sync + PR health + core standards checks + shared infra ownership guard | Daily alignment pass |
| `qa-platform-readiness` | Governed front-office runtime bring-up and populated UI proof | Pre-release demo and product-surface readiness gate |
| `qa-platform-readiness-clean-core` | Governed front-office runtime proof after targeted lotus-core state reset and deterministic lotus-ai provider-disabled posture | Stale core state after load/performance data runs |
| `qa-platform-readiness-clean-core-build` | Clean-core front-office proof with local service image rebuilds and deterministic lotus-ai provider-disabled posture | RFC proof when local branch changes must be in Docker images |
| `fast-feedback` | Fast lint/type/test checks in parallel | Developer inner loop |
| `ci-parity` | Host-based CI parity checks | Pre-PR confidence |
| `docker-ci-parity` | Dockerized parity checks | Reduce host env drift |
| `autonomous-foundation` | Broader governance + quality sweep, including shared infra ownership drift detection | Scheduled deep audits |

## Specialized Profiles

- `bootstrap-env`: initial dependency bootstrap across repos
- `docker-build`: docker image/build readiness checks
- `pas-data-smoke`: lotus-core + upstream smoke checks
- `migration-quality`: strict migration quality checks
- `coverage-pyramid-baseline`: test pyramid/coverage baseline evidence
- `backend-standards-conformance`: backend standards validation only
- `openapi-conformance-baseline`: OpenAPI quality baseline only
- `domain-vocabulary-conformance`: vocabulary policy baseline only
- `repo-metadata-validation`: metadata/default branch/preflight command validation
- `automation-integrity`: automation config + local-vs-CI parity hard-fail gate
- `change-test-impact`: detects source changes without test updates across repos
- `rfc-conformance-baseline`: RFC inventory + backlog
- `pr-lifecycle`: PR monitor/auto-merge/cleanup loop task
- `enforce-repository-governance`: branch protection + governance application
- `platform-alignment`: includes repository-governance drift validation indirectly through the shared standards sweep

## Choosing Max Parallel

- `1`: strict sequencing, easier diagnostics
- `2-3`: balanced throughput and readability
- `4+`: use only when machine/network capacity is sufficient

## Suggested Defaults

- Daily: `platform-alignment` at `-MaxParallel 3`
- Pre-release: `autonomous-foundation` at `-MaxParallel 1`
- Active coding: `fast-feedback` at `-MaxParallel 3`

## Verify Profile Integrity

Run:

```powershell
powershell -ExecutionPolicy Bypass -File automation/Validate-Automation-Config.ps1
```
