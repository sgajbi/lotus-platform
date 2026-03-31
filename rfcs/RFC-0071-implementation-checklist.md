# RFC-0071 Implementation Checklist

- Rollout Status: Not started
- Governing RFC: `rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`

## Goal

Turn RFC-0071 into an explicit, app-by-app rollout that removes canonical localhost/port coupling
from Lotus runtime contracts and replaces it with stable, environment-scoped service addressing.

## Canonical environment model

### Public hostname pattern

- `https://{service}.{environment}.lotus`

Examples:

- `https://workbench.dev.lotus`
- `https://gateway.dev.lotus`
- `https://workbench.uat.lotus`
- `https://gateway.uat.lotus`
- `https://workbench.prod.lotus`
- `https://gateway.prod.lotus`

### Local dev rule

Local development must use the same `dev` hostnames, resolved locally through hosts-file or local
DNS mapping and one central local proxy.

## Cross-app rollout tracker

| App | Role | Exposure class | Current state | Target state | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `lotus-platform` | Governance and platform runtime owner | N/A | No RFC/tracker yet for service addressing | Own hostname rules, local proxy standard, validation automation, and rollout tracker | In progress | This RFC and checklist establish ownership |
| `lotus-workbench` | Frontend workspace | Public | README and runtime defaults still reference direct host:port BFF targets | Uses only env-driven canonical `gateway.{env}.lotus` style URLs; no implicit localhost fallback | Not started | Highest-priority app because browser and BFF paths are user-visible |
| `lotus-gateway` | Experience API / BFF | Public | README and local examples still present direct ports as primary integration addresses | Public gateway exposed via canonical environment hostname; docs and config updated | Not started | Must align with workbench first |
| `lotus-core` | Canonical data platform | Internal | Local docs and examples still port-centric for some integration paths | Internal discovery or env-driven base URLs only; docs stop treating ports as canonical integration identities | Not started | Internal exposure only unless explicitly approved |
| `lotus-performance` | Performance analytics | Internal | README examples are port-centric | Internal discovery or env-driven base URLs only; docs stop treating ports as canonical identities | Not started | Depends on gateway/internal runtime alignment |
| `lotus-risk` | Risk analytics | Internal | Quickstart is port-based | Internal discovery or env-driven base URLs only | Not started | Review after performance because both are analytics services |
| `lotus-advise` | Advisory lifecycle | Internal | To be audited | Internal discovery or env-driven base URLs only | Not started | Advisory-side workflow repo |
| `lotus-manage` | Discretionary lifecycle | Internal | To be audited | Internal discovery or env-driven base URLs only | Not started | Management-side workflow repo |
| `lotus-report` | Reporting and aggregation | Internal | README uses direct service port | Internal discovery or env-driven base URLs only | Not started | Reporting integration path |
| `lotus-ai` | Shared AI platform | Internal | To be audited | Internal discovery or env-driven base URLs only | Not started | Shared service; must follow platform standard from inception |

## Phase A: Platform ownership baseline

### lotus-platform

1. Keep RFC-0071 as the governing addressing source:
   - `rfcs/RFC-0071-centralized-environment-scoped-service-addressing-and-ingress-governance.md`
2. Keep this checklist as the rollout source of truth:
   - `rfcs/RFC-0071-implementation-checklist.md`
3. Update platform architecture docs and local runbook to describe:
   - central ingress ownership
   - public hostname convention
   - internal-only service discovery model
   - local dev hostname mapping model
4. Add platform automation for detecting obvious localhost/port drift in app-local source and docs.

## Phase B: Public-entry app rollout

### lotus-workbench

1. Remove canonical fallback defaults such as `http://localhost:8100` from runtime paths where
   environment configuration is mandatory.
2. Require explicit environment-driven gateway addressing for SSR/BFF proxy paths.
3. Update README and quickstart docs so canonical examples use stable environment URLs, not raw
   ports.
4. Ensure browser-visible routes and proxy behavior are validated against the canonical hostname
   model.

### lotus-gateway

1. Update README and quickstart docs so public integration identity is the environment hostname, not
   the bound port.
2. Keep port bindings as implementation detail only.
3. Align public API examples with `gateway.{env}.lotus`.
4. Ensure upstream service addressing uses env-driven or service-discovery-driven configuration.

## Phase C: Internal service normalization

### lotus-core

1. Audit config, README, and integration docs for direct cross-app host:port assumptions.
2. Replace canonical integration examples with env-driven or discovery-driven service identities.
3. Keep local app-local ports only as runtime implementation detail.

### lotus-performance

1. Audit config, README, and integration docs for direct cross-app host:port assumptions.
2. Replace canonical integration examples with env-driven or discovery-driven service identities.
3. Align first-use and gateway integration guidance to the central addressing model.

### lotus-risk

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

### lotus-advise

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

### lotus-manage

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

### lotus-report

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

### lotus-ai

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

## Phase D: Local ingress standard

### Target owner: lotus-platform

1. Define one local proxy standard.
2. Define one hostname mapping standard.
3. Define one source of truth for public-entry dev hostnames.
4. Document how app-local ports map behind the proxy without becoming canonical addresses.

## Phase E: Enforcement

### Validation automation targets

1. Detect obvious `localhost:<port>` cross-app URL literals in source.
2. Detect README drift that presents raw ports as canonical service identities.
3. Detect missing env-configured base URL seams for known cross-app callers.
4. Track app rollout state in this checklist until every row is complete.

## Completion rule

This rollout is complete only when:

1. `lotus-platform` owns the addressing standard and validation automation,
2. `lotus-workbench` and `lotus-gateway` use canonical environment-scoped service identities,
3. all internal services are documented and configured with env-driven or discovery-driven
   addressing,
4. no Lotus repository still presents raw localhost+port mappings as the canonical cross-app
   integration model.
