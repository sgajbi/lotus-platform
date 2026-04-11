# Cross-Repository Alignment RFCs

This folder contains architecture RFCs to align:

- `lotus-advise` (current `lotus-advise`)
- `lotus-performance` (current `lotus-performance`)
- `lotus-risk` (current `lotus-risk`)
- `lotus-core` (current `lotus-core`)
- `lotus-manage` (current `lotus-manage`)
- `lotus-gateway` (current `lotus-gateway`)
- `lotus-report` (current `lotus-report`)
- `lotus-workbench` (current `lotus-workbench`)
- `lotus-platform` (current `lotus-platform`)
- `lotus-ai` (current `lotus-ai`)

Reference baseline:
- `lotus-advise` is the primary engineering standard for automation, testing, and architecture discipline.
- Advanced patterns from the other repositories are absorbed where they improve platform quality.

## RFC Index

- `RFC-0001-repository-strategy-and-target-operating-model.md`
- `RFC-0002-bounded-contexts-and-service-boundaries.md`
- `RFC-0003-canonical-domain-vocabulary.md`
- `RFC-0004-cross-service-api-contract-standard.md`
- `RFC-0005-engineering-baseline-and-delivery-standards.md`
- `RFC-0006-shared-python-platform-libraries.md`
- `RFC-0007-bff-integration-contract-for-ui-platform.md`
- `RFC-0008-phased-migration-roadmap-and-governance.md`
- `RFC-0009-platform-service-topology-and-deduplication.md`
- `RFC-0010-reporting-and-document-generation-service.md`
- `RFC-0011-platform-control-plane-and-configurability.md`

## Principles

- Standardization over compatibility (no production consumers yet).
- No backward compatibility requirements for naming/structure while pre-live.
- Single responsibility per service.
- No duplicated ownership of domain capabilities.
- UI consumes a unified lotus-gateway contract, not raw service contracts.
- Cloud and on-prem deployment parity is required for productization.

## Central Standards

- `Domain Vocabulary Glossary.md`
- `Migration Engineering Quality Standard.md`

## Execution RFC Set (Implementation Start)

- `RFC-0012-refined-long-term-platform-vision.md`
- `RFC-0013-repository-strategy-separate-vs-consolidated.md`
- `RFC-0014-commercial-naming-and-positioning-strategy.md`
- `RFC-0015-domain-boundaries-and-service-ownership.md`
- `RFC-0016-standardization-principles-and-engineering-baseline.md`
- `RFC-0017-ui-bff-first-delivery-strategy.md`
- `RFC-0018-phased-implementation-roadmap.md`
- `RFC-0019-pragmatic-unification-plan-now-vs-later.md`
- `RFC-0020-sprint-1-lotus-workbench-vertical-slice.md`
- `RFC-0021-authn-authz-foundation-deferred.md`
- `RFC-0022-performance-analytics-engineering-alignment-to-dpm-standard.md`
- `RFC-0023-performance-analytics-quality-hardening-coverage-and-docker-smoke.md`
- `RFC-0024-lotus-workbench-ui-stack-alignment-and-bff-proxy-hardening.md`
- `RFC-0025-lotus-workbench-proposal-workflow-ux-hardening.md`
- `RFC-0026-lotus-workbench-proposal-operations-workspace.md`
- `RFC-0027-dpm-feature-parity-program-for-lotus-workbench.md`
- `RFC-0028-dpm-parity-phase-2-proposal-version-management.md`
- `RFC-0029-suite-architecture-pas-pa-dpm-and-ui-bff-evolution.md`
- `RFC-0030-ui-suite-storyboard-with-mocked-pas-pa-and-live-dpm.md`
- `RFC-0031-ui-enterprise-workflow-language-and-lineage-visibility.md`
- `RFC-0032-advisor-workflow-shell-phase-1-client-and-task-centric-command-center.md`
- `RFC-0033-advisor-workflow-shell-phase-2-role-based-operating-views.md`
- `RFC-0034-pas-ingestion-integration-for-real-portfolio-creation-from-ui.md`
- `RFC-0035-private-banking-intake-console-ux-hardening.md`
- `RFC-0036-intake-entity-list-operations-and-enterprise-ux-structure.md`
- `RFC-0037-intake-governed-selectors-via-pas-lookups.md`
- `RFC-0038-intake-production-ux-hardening-with-enterprise-form-patterns.md`
- `RFC-0039-ui-responsive-scaling-and-overlap-hardening.md`
- `RFC-0040-ui-browser-qa-remediation-and-enterprise-ux-hardening.md`
- `RFC-0041-platform-integration-architecture-bible-governance.md`
- `RFC-0042-capabilities-governed-ux-contract-and-current-state-assessment.md`
- `RFC-0043-pas-core-snapshot-provenance-and-governance-contract.md`
- `RFC-0044-platform-capability-policy-visibility-in-bff-and-ui.md`
- `RFC-0045-pas-policy-diagnostics-orchestration-in-bff-and-ui.md`
- `RFC-0046-platform-reference-dataset-and-route-identity-alignment.md`
- `RFC-0047-automated-demo-data-pack-bootstrap-and-targeted-service-refresh.md`
- `RFC-0047-domain-driven-product-experience-portfolio-advisory-dpm-lifecycles.md`
- `RFC-0048-shared-automation-and-agent-toolkit.md`
- `RFC-0049A-portfolio-360-and-live-proposal-sandbox.md`
- `RFC-0050-core-data-analytics-and-reporting-service-boundaries.md`
- `RFC-0051-cross-platform-vocabulary-normalization.md`
- `RFC-0052-reporting-and-aggregation-service-v1-bootstrap.md`
- `RFC-0053-pa-authoritative-advanced-analytics-cutover.md`
- `RFC-0054-ras-reporting-endpoint-ownership-cutover.md`
- `RFC-0055-api-driven-service-integration-and-dual-mode-execution.md`
- `RFC-0056-ras-summary-review-phase2-orchestration.md`
- `RFC-0057-test-pyramid-and-meaningful-coverage-governance.md`
- `RFC-0058-coverage-policy-command-alignment-after-99-enforcement.md`
- `RFC-0059-backend-foundation-standardization-wave-1.md`
- `RFC-0060-phase-2-shared-standards-and-automated-conformance.md`
- `RFC-0061-openapi-contract-quality-and-conformance-automation.md`
- `RFC-0062-domain-vocabulary-conformance-automation.md`
- `RFC-0063-platform-wide-rounding-and-precision-standard.md`
- `RFC-0064-lotus-platform-rebrand-and-enterprise-productization-baseline.md`
- `RFC-0065-lotus-performance-to-lotus-performance-and-lotus-risk-split.md`
- `RFC-0066-lotus-advise-to-lotus-advise-and-lotus-manage-split.md`
- `RFC-0067-centralized-api-vocabulary-inventory-and-openapi-documentation-governance.md`
- `RFC-0068-centralized-shared-infrastructure-ownership-and-migration.md`
- `RFC-0069-lotus-ai-shared-ai-platform-service.md`
- `RFC-0070-gold-standard-product-experience-foundation-and-ownership-model.md`
- `RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
- `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
- `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
- `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
- `RFC-0022-platform-target-operating-model-and-service-additions.md`
- `RFC-0023-pas-api-product-and-governance-principles.md`
- `RFC-0024-pas-pa-dpm-integration-and-boundary-model.md`
- `RFC-0025-backend-driven-configurability-entitlements-and-workflow-control.md`
- `RFC-0026-synchronous-vs-asynchronous-integration-patterns.md`
- `RFC-0027-reporting-and-analytics-separation-strategy.md`
- `RFC-0028-ui-bff-integration-model-and-responsibility-rules.md`
- `RFC-0029-phased-integration-roadmap-pas-pa-dpm.md`
- `RFC-0030-adr-governance-and-decision-traceability.md`




