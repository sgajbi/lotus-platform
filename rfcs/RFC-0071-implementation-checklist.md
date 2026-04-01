# RFC-0071 Implementation Checklist

- Rollout Status: Complete
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

### Identity rule

Each tracker row represents an app-owned consumed product or API surface, not every internal
microservice in that app by default.

Create separate rollout sub-items only when:

1. an app intentionally exposes multiple distinct public or cross-app API products,
2. those products have materially different contracts, ownership, auth, or lifecycle,
3. the split is a platform boundary, not an internal implementation seam.

## Cross-app rollout tracker

| App | Role | Exposure class | Current state | Target state | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| `lotus-platform` | Governance and platform runtime owner | N/A | RFC, validator, docs, and local ingress tooling are in place | Own hostname rules, local proxy standard, validation automation, and rollout tracker | Complete | Hosts-file application remains an operator setup step, not an RFC gap |
| `lotus-workbench` | Frontend workspace | Public | Runtime base URL resolution centralized; docs no longer treat localhost as canonical | Uses only env-driven canonical `gateway.{env}.lotus` style URLs; no implicit localhost fallback | Complete | Canonical browser entry path validated live |
| `lotus-gateway` | Experience API / BFF | Public | Public docs and runtime-facing examples use canonical gateway identity | Public gateway exposed via canonical environment hostname; docs and config updated | Complete | Public entry path validated live |
| `lotus-core` | Canonical data platform | Internal | README examples now use canonical core ingress identities; platform-owned docs/automation align to canonical core surfaces | Internal discovery or env-driven base URLs only; docs stop treating ports as canonical integration identities | Complete | Query/control splits remain explicit only where they are genuine platform surfaces |
| `lotus-performance` | Performance analytics | Internal | README setup and cross-app guidance use canonical performance/core identities; platform-owned automation defaults align | Internal discovery or env-driven base URLs only; docs stop treating ports as canonical identities | Complete | Canonical performance surface validated live |
| `lotus-risk` | Risk analytics | Internal | Runtime upstream defaults now use canonical core/performance identities; compose remains app-local | Internal discovery or env-driven base URLs only | Complete | Remaining loopback probes are implementation-local healthchecks |
| `lotus-advise` | Advisory lifecycle | Internal | Demo/operator README now uses canonical advise identity | Internal discovery or env-driven base URLs only | Complete | Remaining historical app-local port examples are non-canonical debug paths only |
| `lotus-manage` | Discretionary lifecycle | Internal | Demo/operator README now uses canonical manage identity; historical validation notes scoped as debug-only | Internal discovery or env-driven base URLs only | Complete | Canonical cross-app guidance is normalized; validation evidence remains historical by design |
| `lotus-report` | Reporting and aggregation | Internal | Runtime upstream defaults and README now use canonical report/core/performance/risk identities | Internal discovery or env-driven base URLs only | Complete | Canonical report surface validated live |
| `lotus-ai` | Shared AI platform | Internal | First-use-case demo now defaults its cross-app dependency to canonical performance identity and makes AI base URL explicit | Internal discovery or env-driven base URLs only | Complete | AI self-addressing remains an explicit local seam until a shared ingress surface is required |

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
5. Implement one central local ingress in `platform-stack` and publish the required hosts-file entries.

Current posture:
- complete:
  - RFC and checklist exist
  - central local ingress is implemented with Caddy in `platform-stack`
  - hosts-file management tooling exists
  - ingress smoke validation exists
  - ingress status explainer exists
  - ingress-first contracts, CLI behavior, and operator-doc coverage are under test
  - platform-owned runbooks now describe DNS/hosts, ingress bring-up, and validation sequencing

## Phase B: Public-entry app rollout

### lotus-workbench

1. Remove canonical fallback defaults such as `http://localhost:8100` from runtime paths where
   environment configuration is mandatory.
2. Require explicit environment-driven gateway addressing for SSR/BFF proxy paths.
3. Update README and quickstart docs so canonical examples use stable environment URLs, not raw
   ports.
4. Ensure browser-visible routes and proxy behavior are validated against the canonical hostname
   model.

Current posture:
- complete:
  - runtime base URL resolution was centralized
  - public docs no longer treat localhost as the canonical gateway identity
  - local bring-up paths have been validated against the canonical ingress model end to end

### lotus-gateway

1. Update README and quickstart docs so public integration identity is the environment hostname, not
   the bound port.
2. Keep port bindings as implementation detail only.
3. Align public API examples with `gateway.{env}.lotus`.
4. Ensure upstream service addressing uses env-driven or service-discovery-driven configuration.

Current posture:
- complete:
  - public-facing docs and examples now align to canonical gateway identity
  - public-entry behavior has been validated against the canonical ingress model end to end

## Phase C: Internal service normalization

### lotus-core

1. Audit config, README, and integration docs for direct cross-app host:port assumptions.
2. Replace canonical integration examples with env-driven or discovery-driven service identities.
3. Keep local app-local ports only as runtime implementation detail.

Current posture:
- complete:
  - README examples no longer present localhost ports as the canonical query/ingestion integration contract
  - README now uses `core-query.dev.lotus` and `core-ingestion.dev.lotus` for cross-app and operator-facing examples
  - platform-owned automation and validation now target canonical core surfaces

### lotus-performance

1. Audit config, README, and integration docs for direct cross-app host:port assumptions.
2. Replace canonical integration examples with env-driven or discovery-driven service identities.
3. Align first-use and gateway integration guidance to the central addressing model.

Current posture:
- complete:
  - README setup and compose guidance no longer present localhost or `host.docker.internal` as the canonical operator contract
  - README now uses `performance.dev.lotus` and `core-query.dev.lotus` for local RFC-0071 guidance
  - platform-owned automation and validation now target the canonical performance surface

### lotus-risk

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

Current posture:
- complete:
  - runtime defaults now use `core-query.dev.lotus` and `performance.dev.lotus`
  - unit tests lock the canonical upstream defaults

### lotus-advise

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

Current posture:
- complete:
  - demo README now treats `advise.dev.lotus` as the canonical local service identity

### lotus-manage

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

Current posture:
- complete:
  - demo README now treats `manage.dev.lotus` as the canonical local service identity
  - live demo runner help text now points operators to `manage.dev.lotus`
  - historical manual validation notes are explicitly scoped as debug/process evidence, not canonical cross-app guidance

### lotus-report

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

Current posture:
- complete:
  - runtime upstream defaults now use canonical `core-query.dev.lotus`, `performance.dev.lotus`, and `risk.dev.lotus`
  - README now advertises `report.dev.lotus` as the canonical local service identity
  - unit tests lock the canonical runtime defaults

### lotus-ai

1. Audit runtime defaults, docs, and compose manifests for cross-app localhost assumptions.
2. Replace with env-driven or discovery-driven identities.

Current posture:
- complete:
  - first-use-case demo now uses the canonical performance service identity by default
  - AI base URL is now an explicit configurable seam instead of being repeated through the demo scripts

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

App-local healthchecks, container-internal loopback probes, and historical validation evidence may
still use direct process ports where they are explicitly scoped as implementation-local or
debug-only and are not presented as the canonical cross-app contract.
