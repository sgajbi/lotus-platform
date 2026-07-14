# Validation and CI

## Current Scope

This page maps `lotus-platform` validation lanes to the repo-native commands and evidence surfaces
that engineers, operators, and agents should use before PR merge or production-facing claims. It
summarizes current platform governance checks; it does not by itself certify live production
deployment, client demo readiness, or supported feature promotion.

| Reader | Use This Page To | Evidence Boundary |
| --- | --- | --- |
| Engineers and agents | Pick the correct local lane and focused checks. | Local proof must match the PR diff and issue scope. |
| CI and release owners | Confirm platform gates cover release, mesh, docs, and deployment-promotion contracts. | Main releasability and live deployment proof remain separate. |
| Operators and support | Find the runbooks and output paths behind platform validation claims. | Output artifacts are evidence, not unsupported readiness claims. |

## Lane model

`lotus-platform` uses:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation`

## Repo-native command mapping

- feature lane:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`
- PR merge gate:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge`
- main releasability:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane main-releasability`
- platform validation lane:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformValidationLane.ps1 -ValidationProfile core-performance-green-lanes`
- platform demo-readiness certification, report-only:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformDemoReadinessCertification.ps1 -ScenarioMode fresh_seed`
- mesh certification advisory smoke:
  `python automation\mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --skip-publication-checks`
- mesh certification branch-current repo-native declaration preview:
  `python automation\mesh_certification_gate.py --mode advisory --generated-at-utc 2026-04-20T00:00:00Z --catalog-source current-repo-native --skip-publication-checks`
- mesh certification blocking proof with sibling repos:
  `python automation\mesh_certification_gate.py --mode blocking --generated-at-utc 2026-04-20T00:00:00Z --require-sibling-repos`
- GitHub cross-repo mesh certification gate:
  `.github/workflows/mesh-certification-gate.yml`
- enterprise mesh maturity matrix:
  `python automation\generate_enterprise_mesh_maturity_matrix.py --check --generated-at-utc 2026-04-20T00:00:00Z`
- enterprise mesh operating report check:
  `python automation\generate_enterprise_mesh_operating_report.py --generated-at-utc 2026-04-20T00:00:00Z --check`
- source-data product onboarding scaffold check:
  `python automation\generate_domain_product_onboarding.py --repository lotus-core --product-name ExampleSourceProduct --product-version v1 --output-directory output\domain-product-onboarding\example --check`
- enterprise backend refactor quality baseline:
  `python automation\generate_enterprise_backend_quality_baseline.py --write --check`
- auto-merge and exact-main releasability convergence:
  `python automation\validate_auto_merge_releasability.py`
- digest-based deployment promotion manifest validation:
  `python automation\validate_deployment_promotion_manifest.py`

## What the gates protect

- central context and documentation contract integrity
- workflow and standards drift detection
- automation and validator correctness
- cross-repository governance posture
- auto-merge releasability convergence: `LOTUS_AUTOMERGE_TOKEN` rebase auto-merge, merged-PR
  `main-releasability.yml` dispatch, workflow-dispatch support, and expiring rollout exceptions
- reusable platform validation entrypoints
- RFC-0089 first-wave mesh certification posture for governed domain products
- RFC-0090 GitHub blocking enforcement for the first-wave cross-repo mesh certification gate
- RFC-0091 enterprise maturity controls: telemetry collection, SLO, access, lifecycle, evidence,
  catalog, gateway, and Workbench check families
- RFC-0092 production mesh operations: operating state, limited-history posture, drift trend,
  regression detection, escalation queue, and product operating posture
- source-data product onboarding scaffolds: source API profile, API certification checklist,
  ingestion pipeline checklist, trust telemetry, SLO/access/evidence policy, and repo-owned
  declaration readiness
- enterprise backend refactor quality surface: report-only baseline, scorecard, quality gate rules,
  security review notes, and refactor decisions under `quality/`
- deployment promotion proof: digest-only image references, release-evidence digest reconciliation,
  no rebuild-per-environment promotion, out-of-scope environment reasons, and no production
  certification claim before live deployment proof
- platform demo-readiness certification: report-only `core-performance-green-lanes` evidence that
  seeds deterministic synthetic scenarios, calls real core/performance APIs, asserts domain figures,
  and uploads `output/demo-readiness/platform/platform-demo-readiness-certification.json`

## Mesh certification outputs

`automation\mesh_certification_gate.py` writes:

- `output/mesh-certification/mesh-certification-status.json`
- `output/mesh-certification/mesh-certification-status.md`
- `output/mesh-certification/mesh-certification-issues.json`
- `output/mesh-certification/enterprise-mesh-certification-status.json`
- `output/mesh-certification/enterprise-mesh-certification-status.md`
- `output/mesh-certification/enterprise-mesh-certification-issues.json`
- `output/mesh-certification/enterprise-mesh-operating-report.json`
- `output/mesh-certification/enterprise-mesh-operating-report.md`

## Documentation contract posture

Platform documentation is partially protected by unit contract tests, including context-system and
automation README expectations.

When changing platform docs, run the targeted contract packs rather than assuming prose-only safety.

Before running the pack, classify the documentation change through:

- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](../context/TASK-ROUTING-GUIDE.md)
- [Mesh Certification Gate Runbook](../docs/operations/mesh-certification-gate-runbook.md)

That keeps README, repo-local wiki, deep docs, and platform context from drifting into the wrong
surface even when the tests are green.

## High-signal targeted pack

```powershell
python -m pytest tests/unit/test_engineering_context_system_contract.py tests/unit/test_dev_ingress_status_automation_contract.py tests/unit/test_front_office_runtime_automation_contract.py -q
python automation/validate_engineering_context_system.py
python automation/generate_enterprise_backend_quality_baseline.py --check
```

## Related references

- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](../context/TASK-ROUTING-GUIDE.md)
