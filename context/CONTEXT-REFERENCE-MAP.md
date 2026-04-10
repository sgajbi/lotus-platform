# Context Reference Map

Use this file to route quickly to the right Lotus context source without loading unnecessary material.

Start with:

1. [Lotus Quickstart Context](./LOTUS-QUICKSTART-CONTEXT.md)
2. [Lotus Engineering Context](./LOTUS-ENGINEERING-CONTEXT.md)
3. [lotus-context-manifest.json](./lotus-context-manifest.json)

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

The manifest currently carries:

1. application registry,
2. domain authority map,
3. standards registry,
4. active RFC registry,
5. canonical reading order,
6. context document path map.

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

## Active Governance RFCs

The most operationally important current RFCs are:

1. [RFC-0071](../rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md)
2. [RFC-0072](../rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md)
3. [RFC-0073](../rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md)

Use [rfcs/README.md](../rfcs/README.md) for the full RFC inventory.

## Task Routing Guidance

### For frontend and product-surface work

Read:

1. the quickstart context,
2. the engineering context,
3. the `lotus-workbench` repository context once it exists,
4. RFC-0070 and RFC-0072 where delivery or UI-platform governance matters,
5. the platform validation references when end-to-end proof is required.

### For backend API or domain-service work

Read:

1. the engineering context,
2. the owning repo context once it exists,
3. RFC-0067 and related vocabulary or contract standards,
4. RFC-0072 for CI and validation expectations.

### For cross-app runtime and validation work

Read:

1. the engineering context,
2. RFC-0071,
3. RFC-0072,
4. the local development and ingress runbooks,
5. the manifest to identify participating services and canonical paths.

### For platform standards and governance work

Read:

1. the engineering context,
2. RFC-0072,
3. RFC-0073,
4. the relevant standard documents under `platform-standards/`,
5. the platform engineering ledger and recent architectural decisions digest.

## Runbooks And Operations

1. [Local Development Runbook](../Local%20Development%20Runbook.md)
2. `docs/` and `automation/README.md` in `lotus-platform`
3. platform validation and ingress automation under `automation/`

## Repository-Local Context Documents

These will become the implementation truth for each repo:

1. `lotus-platform/REPOSITORY-ENGINEERING-CONTEXT.md`
2. `lotus-workbench/REPOSITORY-ENGINEERING-CONTEXT.md`
3. `lotus-gateway/REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-core/REPOSITORY-ENGINEERING-CONTEXT.md`
5. `lotus-performance/REPOSITORY-ENGINEERING-CONTEXT.md`
6. `lotus-risk/REPOSITORY-ENGINEERING-CONTEXT.md`
7. `lotus-advise/REPOSITORY-ENGINEERING-CONTEXT.md`
8. `lotus-manage/REPOSITORY-ENGINEERING-CONTEXT.md`
9. `lotus-report/REPOSITORY-ENGINEERING-CONTEXT.md`
10. `lotus-ai/REPOSITORY-ENGINEERING-CONTEXT.md`

Slice 1 defines the central system. Repository-local rollout happens in later RFC-0073 slices.
