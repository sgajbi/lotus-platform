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

- [Continuous Integration, Validation, and Release Governance Standard](../docs/standards/Continuous%20Integration%2C%20Validation%2C%20and%20Release%20Governance%20Standard.md)
- [Dependency Hygiene and Security Standard](../docs/standards/Dependency%20Hygiene%20and%20Security%20Standard.md)
- [Enterprise Readiness Standard](../docs/standards/Enterprise%20Readiness%20Standard.md)
- [Platform Observability Standards](../docs/standards/Platform%20Observability%20Standards.md)
- [Platform Integration Architecture Bible](../docs/architecture/Platform%20Integration%20Architecture%20Bible.md)

## Operating rule

When a pattern matters ecosystem-wide, it should not stop as prose only. Promote it into validators,
templates, automation, or tests where practical.
