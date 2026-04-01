# RFC-0071: Centralized Environment-Scoped Service Addressing and Ingress Governance

- Status: Complete
- Date: 2026-03-31
- Owners: lotus-platform governance
- Related:
  - `RFC-0007-bff-integration-contract-for-ui-platform.md`
  - `RFC-0028-ui-bff-integration-model-and-responsibility-rules.md`
  - `RFC-0041-platform-integration-architecture-bible-governance.md`
  - `RFC-0068-centralized-shared-infrastructure-ownership-and-migration.md`

## Objective

Eliminate direct `localhost` and port-based service addressing from Lotus application runtime
contracts and replace it with stable, environment-scoped service URLs governed centrally in
`lotus-platform`.

The target outcome is that application code, runbooks, automation, and UI clients refer to stable
service identities that vary only by environment, such as `dev`, `uat`, and `prod`, while ingress,
reverse-proxy, and internal routing details stay outside application source code.

## Problem

The current Lotus estate still relies heavily on direct host-and-port addressing in runtime defaults,
README examples, local bring-up notes, and in some cases application fallback logic.

Examples observed across the suite included:

1. `lotus-workbench` defaulting `BFF_BASE_URL` to `http://localhost:8100`.
2. README and local runbook examples coupling UI, gateway, and backend services to explicit ports.
3. Local restarts breaking applications when the required shell environment is not preserved.
4. Application repositories carrying environment-specific address assumptions that should be owned by
   platform runtime configuration instead.

This created avoidable risk:

1. Local dev is brittle because app behavior depends on shell-scoped env state.
2. UAT/prod promotion requires rewriting or overriding app-local assumptions rather than relying on
   one stable addressing model.
3. Browser and BFF code risk leaking infrastructure topology concerns into product code.
4. Shared operational patterns such as TLS termination, auth forwarding, CORS policy, and
   observability become fragmented across repos.

## Decision

Lotus will adopt centralized, environment-scoped service addressing with one shared ingress /
reverse-proxy tier per environment.

Implementation status:

- complete for the governed Lotus cross-app contract surface
- canonical `*.{env}.lotus` identities are now the documented and validated default across the platform-owned ingress path
- remaining direct `localhost` and raw port references are limited to implementation-local healthchecks, test fixtures, and explicitly scoped debug-only or historical evidence paths

### Naming decision rule

Public and cross-app service identities must represent the consumed product or API surface, not the
internal microservice split behind that surface, unless there is a real contract reason to expose
multiple identities.

Default rule:

1. one consumed product or API surface gets one stable public or cross-app identity,
2. internal query/control/worker splits remain implementation detail,
3. separate public identities are allowed only when contracts, ownership, auth, consumer group, or
   lifecycle are materially different.

This means a repository or domain may internally run multiple services without forcing those
implementation seams into canonical public naming.

### Recommended canonical hostname pattern

Every environment must expose stable service identities using:

- `https://{service}.{environment}.lotus`

Examples:

- `https://workbench.dev.lotus`
- `https://gateway.dev.lotus`
- `https://workbench.uat.lotus`
- `https://gateway.uat.lotus`
- `https://workbench.prod.lotus`
- `https://gateway.prod.lotus`

For local development, the same `dev` hostnames must be used, resolved locally through hosts-file or
local DNS mapping and terminated by a local central proxy.

### Why this pattern is recommended

`{service}.{environment}.lotus` is the recommended default because it preserves the right
operational properties for a multi-app platform:

1. service or API identity is explicit in the hostname,
2. environment is explicit and easy to reason about,
3. ingress, TLS, observability, ownership, and support workflows map cleanly to the same service
   identity,
4. browser-facing apps and API products can use the same naming policy without coupling everything
   to one shared path host.

### Allowed alternatives

This RFC governs the addressing model and ownership rules more than one literal hostname shape.

Alternative hostname conventions are acceptable only if they preserve the same properties:

1. stable service identity,
2. explicit environment identity,
3. central ingress ownership,
4. no leakage of internal microservice topology by default.

Examples of acceptable alternatives in principle:

1. `https://{environment}.{service}.lotus`
2. `https://{environment}-{service}.lotus`

Path-only environment models such as one shared hostname with service and environment hidden in
paths are not the preferred default for Lotus because they weaken service identity, operational
clarity, and long-term separation of browser-facing products and API products.

### Ownership rule

`lotus-platform` owns the canonical environment-addressing model and ingress governance.

This includes:

1. hostname and URL conventions,
2. local proxy / ingress patterns,
3. cross-app documentation of which services are public-entry services versus internal-only services,
4. validation automation that detects app-local port assumptions where practical.

Application repositories do **not** own:

1. public host naming conventions,
2. ingress topology,
3. environment hostname selection logic,
4. browser-visible port mapping.

## Target runtime model

### External entrypoints

Browser-visible and operator-visible entrypoints are exposed through the central ingress tier:

1. `lotus-workbench`
2. `lotus-gateway`
3. any future externally reachable product UI or operator-facing API explicitly approved for public
   exposure

### Internal-only service addressing

Backend-to-backend traffic must use stable service discovery identities, not browser hostnames and
not port literals embedded in source.

Examples:

1. Compose service names in app-local or platform-local Docker environments
2. Kubernetes service DNS names in clustered environments
3. centrally injected base URLs for non-clustered environments

### Local development model

Local development must mirror the same addressing contract:

1. `workbench.dev.lotus` routes to local `lotus-workbench`
2. `gateway.dev.lotus` routes to local `lotus-gateway`
3. backend services remain reachable through proxy rules or internal service discovery as required
4. browser clients never need to know backend ports

## Application inventory and addressing posture

The current Lotus application estate in scope for this rollout is:

| App | Primary role | Address posture target |
| --- | --- | --- |
| `lotus-workbench` | Unified frontend workspace | Public environment hostname |
| `lotus-gateway` | Experience API / BFF | Public environment hostname |
| `lotus-core` | Canonical data and query platform | Internal stable service identity |
| `lotus-performance` | Performance analytics service | Internal stable service identity |
| `lotus-risk` | Risk analytics service | Internal stable service identity |
| `lotus-advise` | Advisory lifecycle service | Internal stable service identity; public only if explicitly exposed later |
| `lotus-manage` | Discretionary management workflow service | Internal stable service identity; public only if explicitly exposed later |
| `lotus-report` | Reporting and aggregation service | Internal stable service identity |
| `lotus-ai` | Shared AI platform service | Internal stable service identity |
| `lotus-platform` | Governance, platform stack, automation | Canonical owner of ingress/addressing standards |

## Governance rules

1. No Lotus application may rely on `localhost` or raw port literals as the canonical runtime
   address of another Lotus application.
2. Environment-specific service endpoints must be supplied through platform configuration, not
   hardcoded in app source.
3. Public-facing hostnames are owned centrally in `lotus-platform`.
4. One shared ingress / reverse-proxy tier per environment is the default model.
5. Per-app reverse proxies are allowed only as internal implementation details behind the central
   ingress, not as the source of public URL governance.
6. Browser code must not carry direct knowledge of internal backend port mappings.
7. Backend services must prefer stable internal discovery identities over public hostnames when
   calling one another.
8. Canonical service identities must describe consumed product/API boundaries, not internal runtime
   topology, unless multiple identities are justified by materially distinct contracts or operating
   concerns.

## Required implementation model

### 1. Configuration discipline

Every app must consume named base URLs from configuration only.

Examples:

1. `BFF_BASE_URL`
2. `GATEWAY_BASE_URL`
3. `PERFORMANCE_BASE_URL`
4. `CORE_QUERY_BASE_URL`
5. `REPORT_BASE_URL`
6. `AI_BASE_URL`

Application code must not silently fall back to an arbitrary localhost port in production-facing
paths.

### 2. Central ingress pattern

Each environment must have one shared ingress / reverse-proxy owner.

Responsibilities:

1. TLS termination
2. hostname routing
3. cross-origin policy
4. forwarded headers
5. request logging and edge observability
6. path-based routing where applicable

### 3. Local dev parity

`lotus-platform` must define the canonical local dev ingress pattern so developers do not manually
invent hostnames or ports.

The local model must support:

1. hosts-file or local DNS mapping,
2. one local proxy on standard ports,
3. routing from canonical `*.dev.lotus` hostnames to local service ports,
4. platform-level docs and automation for bring-up.

### 4. Validation automation

Platform automation should detect:

1. hardcoded `localhost:<port>` service URLs in source,
2. README/runbook drift that presents ports as canonical identities,
3. missing env-driven base URL configuration where cross-app calls exist.

## Non-Goals

This RFC does not require:

1. immediate migration of every internal service to a public hostname,
2. full production ingress implementation details for every environment in this document,
3. replacing legitimate app-local port bindings used by local process managers or container runtime,
4. collapsing all services behind one monolith endpoint.

The goal is stable addressing abstraction and central ownership, not the removal of ports from the
infrastructure layer itself.

## Rollout phases

### Phase 1: Governance and inventory baseline

1. Adopt this RFC.
2. Create and maintain the implementation checklist for all Lotus apps.
3. Define the canonical hostname scheme and exposure class per app.
4. Document the local-dev ingress model in `lotus-platform`.

### Phase 2: Public-entry services

1. Remove raw host:port assumptions from `lotus-workbench`.
2. Remove raw host:port assumptions from `lotus-gateway` public-facing guidance and runtime defaults
   where inappropriate.
3. Ensure `lotus-workbench` and `lotus-gateway` can run cleanly against canonical environment URLs.

### Phase 3: Internal service normalization

1. Review `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`,
   `lotus-report`, and `lotus-ai` for app-local port assumptions in cross-app runtime config.
2. Convert service-to-service addressing to stable env-configured URLs or internal discovery names.
3. Remove misleading documentation that treats raw port bindings as canonical integration addresses.

### Phase 4: Automation and enforcement

1. Add platform drift checks.
2. Add rollout status visibility to platform docs.
3. Treat app-local regressions back to direct localhost assumptions as governance failures.

## Consequences

### Benefits

1. Stable environment promotion model across dev, UAT, and prod.
2. Fewer local runtime failures caused by missing shell env.
3. Cleaner separation between product code and infrastructure topology.
4. Easier TLS, auth, CORS, and observability management.
5. Better support for app-by-app rollout tracking.

### Trade-offs

1. `lotus-platform` takes on more runtime governance responsibility.
2. Local dev setup becomes slightly more opinionated because hostnames and ingress are standardized.
3. Existing docs and quickstart examples across the suite will need cleanup.

## Acceptance criteria

1. `lotus-platform` documents the canonical environment-scoped hostname scheme.
2. `lotus-platform` owns the rollout checklist for all Lotus apps in scope.
3. `lotus-workbench` no longer depends on implicit localhost port fallback for BFF routing.
4. Public-facing Lotus apps use environment-scoped stable URLs.
5. Internal service integration defaults are env-driven or service-discovery-driven, not hardcoded raw
   localhost ports.
6. Platform documentation and automation can track which apps are complete versus pending.

## Implementation tracker

Rollout tracking is maintained in:

- `rfcs/RFC-0071-implementation-checklist.md`

Current implementation posture on 2026-03-31:

1. `lotus-platform` Phase A is materially in progress:
   - canonical local ingress is implemented in `platform-stack`
   - hosts-file sync, ingress smoke validation, and ingress status explanation tooling are implemented
   - ingress-first output contracts and operator-doc contracts are covered by tests
2. `lotus-workbench` public-entry cleanup is in progress:
   - service resolution was centralized and public-entry documentation was aligned to canonical identities
3. `lotus-gateway` public-entry cleanup is in progress:
   - public-facing guidance was aligned to canonical gateway identities
4. Internal service normalization remains largely pending across `lotus-core`, `lotus-performance`, `lotus-risk`, `lotus-advise`, `lotus-manage`, `lotus-report`, and `lotus-ai`.
