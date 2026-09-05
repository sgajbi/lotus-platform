# Security and Governance

## Governance role

`lotus-platform` owns the standards and validators that keep Lotus engineering aligned.

## Key governance surfaces

- CI and validation lane governance
- workflow security and runtime baselines
- repository hygiene and standards conformance
- service addressing and ingress governance
- central context and agent operating contract
- scaffold and validator ownership
- governed dependency, SBOM, vulnerability-scan, and container-image maturity posture
- RFC-0084 domain-product registration, trust metadata governance, and consumer compatibility checks
- RFC-0089 mesh certification gate for first-wave telemetry, live trust certification, gateway
  publication drift, and Workbench discovery consumption drift
- RFC-0090 read-only GitHub cross-repo workflow enforcement for the blocking mesh certification gate
- RFC-0091 enterprise mesh maturity controls for repo-native onboarding, runtime-preferred
  telemetry collection, SLO policies, access policies, evidence-pack policies, broader product
  rollout, maturity scope, and enterprise certification artifacts
- RFC-0092 production mesh operations evidence for current operating state, limited-history
  posture, drift trend, regression detection, product operating posture, escalation ownership, and
  operator guidance

## Mesh governance boundaries

- producer repositories own product declarations and telemetry evidence
- `lotus-platform` owns aggregation, validation, certification, policy, evidence, and operating
  reports
- `lotus-gateway` is the read-only API publication face, not the product registry
- `lotus-workbench` consumes gateway/BFF APIs only and must not read platform files directly
- customer evidence packs must not expose restricted telemetry paths, source artifacts, or
  entitlement details outside their approved audience class

## Important standards

- [Continuous Integration, Validation, and Release Governance Standard](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Continuous%20Integration%2C%20Validation%2C%20and%20Release%20Governance%20Standard.md)
- [Dependency Hygiene and Security Standard](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Dependency%20Hygiene%20and%20Security%20Standard.md)
- [Enterprise Readiness Standard](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Enterprise%20Readiness%20Standard.md)
- [Lotus Data Mesh Standard](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Lotus%20Data%20Mesh%20Standard.md)
- [Lotus Client Demo Certification Standard](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Lotus%20Client%20Demo%20Certification%20Standard.md)
- [Platform Observability Standards](https://github.com/sgajbi/lotus-platform/blob/main/docs/standards/Platform%20Observability%20Standards.md)
- [Platform Integration Architecture Bible](https://github.com/sgajbi/lotus-platform/blob/main/docs/architecture/Platform%20Integration%20Architecture%20Bible.md)

## Dependency and image posture

Application libraries and container images must default to mature, widely deployed,
well-documented, actively maintained technology with broad training, scanner, and operational
tooling support. Beta, preview, experimental, incubating, unsupported, or novelty-driven major
upgrades are excluded from runtime and release-image posture unless an explicit issue-backed,
time-bounded exception records ownership, vulnerability posture, compensating controls, rollback,
expiry, and a planned fix path.

The authored platform contract is
`platform-contracts/vulnerability-exceptions/vulnerability-exception-register.schema.json`.
Run:

```powershell
python automation\validate_vulnerability_exception_register.py --report-only
```

Use report-only mode while dependency/security and release-image baselines, false-positive policy,
and lane placement are still being measured. Remove `--report-only` only for focused blocking proof
after promotion criteria are met. Approved exceptions require scanner evidence, approval evidence,
exposure/exploitability proof for high, critical, or known-exploited findings, and a remediation
path before any production-ready or bank-buyable claim.

## Operating rule

When a pattern matters ecosystem-wide, it should not stop as prose only. Promote it into validators,
templates, automation, or tests where practical.
