# Ecosystem Registries

This file is generated from [lotus-context-manifest.json](./lotus-context-manifest.json) by `automation/render_context_registries.py`.

- Last reviewed on: `2026-04-11`

## Application Registry

| Repository | Category | Business Role | Runtime | Repo Context | Quality Commands | Platform E2E |
| --- | --- | --- | --- | --- | --- | --- |
| `lotus-platform` | `platform-governance` | Shared standards, automation, ingress, validation, and governance owner | `python-and-powershell-tooling` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `repo_checks: powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`, `validation_lane: powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformValidationLane.ps1 -ValidationProfile core-performance-green-lanes` | Yes |
| `lotus-workbench` | `product-ui` | Primary product UI for portfolio, performance, risk, advisory, and evidence workflows | `node-react-nextjs` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make check`, `browser_smoke: make test-e2e` | Yes |
| `lotus-gateway` | `experience-api` | Unified client contract and composition layer for Lotus product experiences | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci-local-docker` | Yes |
| `lotus-core` | `domain-service` | Authoritative portfolio, booking, account, and transaction service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-performance` | `domain-service` | Authoritative performance analytics and review service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-risk` | `domain-service` | Authoritative risk analytics service for drawdown, attribution, concentration, and rolling risk | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-advise` | `domain-service` | Advisory workflow and recommendation service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-manage` | `domain-service` | Discretionary mandate portfolio-management execution and operational supportability service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci-local` | Yes |
| `lotus-report` | `domain-service` | Reporting and document-generation service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-render` | `domain-service` | Deterministic document rendering service for Lotus reporting | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-ai` | `shared-capability-service` | Shared AI capability service for governed AI-backed flows | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |
| `lotus-archive` | `shared-capability-service` | Generated-document archive, retrieval, retention, legal hold, access audit, and document lifecycle service | `python-fastapi` | `REPOSITORY-ENGINEERING-CONTEXT.md` | `quality: make ci` | Yes |

## Domain Authority Map

| Domain | Authoritative Repository | Composition Layers |
| --- | --- | --- |
| `portfolio-management-and-transactions` | `lotus-core` | lotus-gateway, lotus-manage, lotus-report |
| `performance-analytics` | `lotus-performance` | lotus-gateway |
| `risk-analytics` | `lotus-risk` | lotus-gateway |
| `advisory-workflows` | `lotus-advise` | lotus-gateway |
| `management-and-operations` | `lotus-manage` | lotus-gateway |
| `reporting-and-document-generation` | `lotus-report` | lotus-gateway, lotus-render |
| `generated-document-archive-retrieval-retention-and-legal-hold` | `lotus-archive` | lotus-gateway, lotus-report |
| `ai-capabilities` | `lotus-ai` | lotus-gateway |

## Standards Registry

| Standard | Scope | Source Path |
| --- | --- | --- |
| Continuous Integration, Validation, and Release Governance Standard | `platform-wide` | `docs/standards/Continuous Integration, Validation, and Release Governance Standard.md` |
| Testing Pyramid and Coverage Standard | `platform-wide` | `docs/standards/Testing Pyramid and Coverage Standard.md` |
| Dependency Hygiene and Security Standard | `platform-wide` | `docs/standards/Dependency Hygiene and Security Standard.md` |
| Platform Observability Standards | `platform-wide` | `docs/standards/Platform Observability Standards.md` |
| Enterprise Readiness Standard | `platform-wide` | `docs/standards/Enterprise Readiness Standard.md` |
| Lotus Bank-Buyable Engineering Contract | `platform-wide` | `platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md` |
| Scalability and Availability Standard | `platform-wide` | `docs/standards/Scalability and Availability Standard.md` |
| Domain Vocabulary Glossary | `platform-wide` | `docs/standards/Domain Vocabulary Glossary.md` |
| Platform Integration Architecture Bible | `platform-wide` | `docs/architecture/Platform Integration Architecture Bible.md` |

## Active RFC Registry

| RFC | Status | Implementation Posture | Title |
| --- | --- | --- | --- |
| `RFC-0071` | `active` | implemented and governed | Centralized environment-scoped service addressing and ingress governance |
| `RFC-0072` | `active` | partially implemented; continuation resumes after current fix-forward and RFC-0074 proposal work | Platform-wide multi-lane CI, validation, and release governance |
| `RFC-0073` | `active` | implemented and governed | Lotus ecosystem engineering context and agent guidance system |
| `RFC-0074` | `active` | implemented and governed | Repeatable developer and agent bootstrap system |
| `RFC-0093` | `active` | implemented on main | Lotus context assembly and compaction hardening for agentic development |
| `RFC-0094` | `active` | implemented on main | Durable background engineering task ledger and governed delegation model |
| `RFC-0095` | `active` | implemented | Heartbeat-driven monitoring and attention surfacing |
| `RFC-0096` | `active` | implemented | Governed multi-agent delegation model |
| `RFC-0103` | `active` | implemented for supported first-wave archive scope; Workbench retrieval and production certification deferred | Document archive, retrieval, retention, and legal hold |
