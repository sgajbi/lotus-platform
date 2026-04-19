# Context Reference Map

Use this file to route quickly to the right Lotus context source without loading unnecessary material.

Start with:

1. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
3. [Task Routing Guide](./TASK-ROUTING-GUIDE.md)
4. [lotus-context-manifest.json](./lotus-context-manifest.json)

## Central Memory Layer

1. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
   Fast orientation for a new session.
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
   Canonical ecosystem truth and engineering posture.
3. [Platform Engineering Ledger](./platform-engineering-ledger.md)
   Curated record of patterns, fixes, and recurring quality lessons.
4. [Recent Architectural Decisions Digest](./recent-architectural-decisions-digest.md)
   High-signal summary of recent decisions affecting implementation reality.

## Structured Context And Registries

1. [lotus-context-manifest.json](./lotus-context-manifest.json)
   Machine-readable ecosystem inventory and doc routing layer.
2. [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md)
   Human-readable registry view derived from the manifest.

The manifest currently carries:

1. application registry,
2. domain authority map,
3. standards registry,
4. active RFC registry,
5. canonical reading order,
6. context document path map.

The registry companion currently exposes:

1. application registry,
2. domain authority map,
3. standards registry,
4. active RFC registry.

Important machine-readable platform contract families now include:

1. `../platform-contracts/api-vocabulary/`
2. `../platform-contracts/domain-vocabulary/`
3. `../platform-contracts/domain-data-products/`
4. `../generated/domain-product-catalog.json`
5. `../generated/domain-product-dependency-graph.json`

For RFC-0084 work, the highest-signal machine-readable files are:

1. [Domain Data Product Contracts](../platform-contracts/domain-data-products/README.md)
2. [Domain Data Product Semantics Registry](../platform-contracts/domain-vocabulary/domain-data-product-semantics.v1.json)
3. [Domain Data Product Trust Metadata Registry](../platform-contracts/domain-vocabulary/domain-data-product-trust-metadata.v1.json)
4. [Generated Domain Product Catalog](../generated/domain-product-catalog.json)
5. [Generated Domain Product Dependency Graph](../generated/domain-product-dependency-graph.json)
6. [Domain Product Source Manifest](../platform-contracts/domain-data-products/domain-product-source-manifest.v1.json)
7. [Generated Domain Product Certification Report](../generated/domain-product-certification-report.json)
8. `../automation/query_domain_product_discovery.py`
   Read-only self-serve query CLI for generated catalog, consumer dependency, and graph-neighborhood
   discovery.
9. `../automation/generate_domain_product_certification.py`
   Generates trust-certification evidence over the catalog and dependency graph without redefining
   product ownership or dependency truth.
10. `../automation/generate_domain_product_discovery.py`
    Reads the governed source manifest, validates included repo-native declarations from sibling
    repositories as one federated source set, and regenerates the catalog and dependency graph.
11. [Trust Telemetry Contracts](../platform-contracts/trust-telemetry/README.md)
    Runtime telemetry schema and validation entrypoint for RFC-0087 live trust evidence.
12. `../automation/validate_trust_telemetry.py`
    Validates product trust telemetry snapshots against the generated product catalog and governed
    trust vocabulary before certification logic consumes them.
13. `../automation/generate_live_trust_certification.py`
    Generates deterministic RFC-0087 live trust certification artifacts from validated telemetry
    snapshots.
14. `../../lotus-core/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `PortfolioStateSnapshot`.
15. `../../lotus-performance/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `ReturnsSeriesBundle`.
16. `../../lotus-risk/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `RiskMetricsReport`.
17. `../../lotus-advise/contracts/trust-telemetry/`
    First-wave producer telemetry snapshot for `AdvisoryProposalLifecycleRecord`.
18. `../tests/unit/test_domain_product_rollout_closure.py`
    Protects RFC-0086 closure posture: first-wave repo-native source ownership, active catalog source
    paths, `lotus-ai` exclusion rationale, and transitional platform mirror retention.

## Task Routing

1. [Task Routing Guide](./TASK-ROUTING-GUIDE.md)
   Primary task-first routing for frontend, backend, cross-app validation, and governance work.
2. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
   Fast orientation and high-signal working posture.
3. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
   Canonical architecture and delivery rules that explain why the task-routing paths exist.

## Procedural Memory

1. [Procedural Memory Index](./PROCEDURAL-MEMORY-INDEX.md)
   Navigation layer for governed operating playbooks.
2. [Change Playbooks](./playbooks/CHANGE-PLAYBOOKS.md)
   Task-type delivery sequences.
3. [PR Loop Playbook](./playbooks/PR-LOOP-PLAYBOOK.md)
   Push, GitHub monitoring, merge, and cleanup guidance.
4. [Validation Playbook](./playbooks/VALIDATION-PLAYBOOK.md)
   Validation depth and evidence selection.
5. [Fix-Forward Patterns](./playbooks/FIX-FORWARD-PATTERNS.md)
   Repeatable response patterns for CI and runtime failures.
6. [TWR Investigation Playbook](./playbooks/TWR-INVESTIGATION-PLAYBOOK.md)
   Investigation sequence for time-weighted return defects, implausible economics, and upstream reconciliation issues.

## Platform Standards

Key standards to use frequently:

1. [Continuous Integration, Validation, and Release Governance Standard](../Continuous%20Integration%2C%20Validation%20and%20Release%20Governance%20Standard.md)
2. [Testing Pyramid and Coverage Standard](../Testing%20Pyramid%20and%20Coverage%20Standard.md)
3. [Dependency Hygiene and Security Standard](../Dependency%20Hygiene%20and%20Security%20Standard.md)
4. [Enterprise Readiness Standard](../Enterprise%20Readiness%20Standard.md)
5. [Scalability and Availability Standard](../Scalability%20and%20Availability%20Standard.md)
6. [Platform Observability Standards](../Platform%20Observability%20Standards.md)
7. [Domain Vocabulary Glossary](../Domain%20Vocabulary%20Glossary.md)
8. [Platform Integration Architecture Bible](../Platform%20Integration%20Architecture%20Bible.md)
9. [Domain Data Product Contracts](../platform-contracts/domain-data-products/README.md)

## Active Governance RFCs

The most operationally important current RFCs are:

1. [RFC-0071](../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
2. [RFC-0072](../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
3. [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)
4. [RFC-0074](../rfcs/RFC-0074-repeatable-developer-and-agent-bootstrap-system.md)

Use [rfcs/README.md](../rfcs/README.md) for the full RFC inventory.

## Task Routing Guidance

### For frontend and product-surface work

Read:

1. the quickstart context,
2. the engineering context,
3. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
4. the `lotus-workbench` repository context,
5. RFC-0070 and RFC-0072 where delivery or UI-platform governance matters,
6. the platform validation references when end-to-end proof is required.

### For backend API or domain-service work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. the owning repo context,
4. RFC-0067 and related vocabulary or contract standards,
5. RFC-0072 for CI and validation expectations.

### For cross-app runtime and validation work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. RFC-0071,
4. RFC-0072,
5. the local development and ingress runbooks,
6. the manifest and [Ecosystem Registries](./ECOSYSTEM-REGISTRIES.md) to identify participating services and canonical paths.

### For platform standards and governance work

Read:

1. the engineering context,
2. the [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
3. RFC-0072,
4. RFC-0073,
5. the relevant standard documents under `platform-standards/`,
6. the platform engineering ledger and recent architectural decisions digest.

### For README, wiki, and documentation-system work

Read:

1. the engineering context,
2. the target repo context,
3. [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md),
4. [Task Routing Guide](./TASK-ROUTING-GUIDE.md),
5. [Lotus Skill Routing Map](./LOTUS-SKILL-ROUTING-MAP.md) when a documentation skill boundary matters,
6. only the target repo `README.md`, `wiki/`, and deeper `docs/` pages needed to keep the docs truthful.

## Runbooks And Operations

1. [Lotus Developer Onboarding](../docs/onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
2. [Lotus Agent Ramp-Up](../docs/onboarding/LOTUS-AGENT-RAMP-UP.md)
3. [Local Development Runbook](../Local%20Development%20Runbook.md)
4. `docs/` and `automation/README.md` in `lotus-platform`
5. platform validation and ingress automation under `automation/`

## Repository-Local Context Documents

These are now the implementation-truth entrypoints for each repo:

1. [lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md](../REPOSITORY-ENGINEERING-CONTEXT.md)
2. `lotus-workbench/REPOSITORY-ENGINEERING-CONTEXT.md`
3. `lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`
6. `lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`
7. `lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`
8. `lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`
9. `lotus-report/REPOSITORY-ENGINEERING-CONTEXT.md`
10. `lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md`

Use [Repository Engineering Context Contract](./Repository-Engineering-Context-Contract.md) and [the template](./templates/REPOSITORY-ENGINEERING-CONTEXT.template.md) when updating or extending the repo-local context set.
