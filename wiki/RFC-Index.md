# RFC Index

## Most operationally important current RFCs

- `RFC-0071`
  centralized environment-scoped service addressing and ingress governance
- `RFC-0072`
  platform-wide multi-lane CI validation and release governance
- `RFC-0073`
  Lotus ecosystem engineering context and agent guidance system
- `RFC-0074`
  repeatable developer and agent bootstrap system

## Important repo-specific references

- [rfcs/README.md](../rfcs/README.md)
- [RFC-0071](../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
- [RFC-0072](../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
- [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
- [RFC-0074](../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md)
- [RFC-0089](../rfcs/RFC-0089-mesh-certification-merge-gate-and-operational-trust-enforcement.md)
  mesh certification merge gate and operational trust enforcement
- [RFC-0090](../rfcs/RFC-0090-cross-repo-mesh-certification-pr-merge-gate.md)
  cross-repo mesh certification PR Merge Gate enforcement
- [RFC-0091](../rfcs/RFC-0091-enterprise-data-mesh-maturity-and-production-readiness.md)
  enterprise data mesh maturity and production readiness

## Local meaning

- RFC-0071 governs canonical local hostnames and ingress posture
- RFC-0072 governs lane structure and validation expectations
- RFC-0073 governs the central context system and operating contract
- RFC-0074 governs onboarding, bootstrap, and skill distribution posture
- RFC-0089 governs the first-wave mesh certification gate, operator artifacts, and
  fix-forward workflow for trust telemetry, gateway publication, and Workbench discovery drift
- RFC-0090 governs the GitHub cross-repo workflow that runs RFC-0089 in blocking mode with sibling
  producer, gateway, and Workbench checkouts
- RFC-0091 governs the final enterprise mesh maturity program; Slice 0 adds the generated maturity
  matrix that classifies repository participation and candidate expansion before implementation
  continues; Slice 1 adds the self-service onboarding scaffold and validation command for new
  repo-native product bundles; Slice 2 adds runtime-preferred trust telemetry collection with
  explicit static fixture fallback evidence; Slice 3 adds first-wave mesh SLO policy enforcement
  into certification; Slice 4 adds first-wave access governance policies and certification checks;
  Slice 5 adds certification-history records and audience-filtered evidence-pack manifests
