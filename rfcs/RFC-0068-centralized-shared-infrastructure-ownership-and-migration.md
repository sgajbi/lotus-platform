# RFC-0068: Centralized Shared Infrastructure Ownership and Migration

- Status: Proposed
- Date: 2026-03-22
- Owners: lotus-platform governance

## Objective

Move ownership of shared platform infrastructure to `lotus-platform` and stop treating any domain service repository as the operational home for cross-cutting infrastructure such as Kafka, Prometheus, and Grafana.

## Problem

Several Lotus repositories currently carry some combination of local infrastructure setup, observability wiring, and service-adjacent Docker assets. That is acceptable for standalone development, but it becomes a boundary leak when one domain repository becomes the de facto owner of infrastructure required by many others.

If shared infrastructure stays effectively "owned" by `lotus-core` or any other application repository, the platform takes on avoidable coupling:

1. Domain boundaries become operationally blurred.
2. New services inherit accidental dependencies on another business service repo.
3. Shared observability and messaging standards drift by repo.
4. Local and platform bring-up become harder to reason about.

## Decision

`lotus-platform` owns shared platform infrastructure.

This includes the canonical platform-level development and validation stack for:

1. Kafka and required supporting services.
2. Prometheus.
3. Grafana.
4. OpenTelemetry collector and future shared telemetry plumbing.
5. Other cross-cutting infrastructure introduced for multi-service use.

The primary implementation home for this shared infrastructure is:

- `lotus-platform/platform-stack`

### Canonical ownership meaning

For the purpose of this RFC, "canonical" means:

1. `lotus-platform/platform-stack` is the default documented bring-up path for shared infrastructure.
2. Shared infrastructure configuration is versioned under `lotus-platform`.
3. Application repositories may still provide app-owned images, bootstrap jobs, and isolated-dev overlays.
4. Application repositories are not the owner of the shared infrastructure product lifecycle.

This distinction matters because `platform-stack` may orchestrate app-owned bootstrap tasks such as:

1. database migrations,
2. topic bootstrap jobs,
3. application service containers.

Those tasks remain app-owned even when they are consumed by the platform stack.

## Responsibilities

### lotus-platform owns

1. Central platform-stack definitions for shared multi-service infrastructure.
2. Shared Docker Compose orchestration for full-platform local bring-up.
3. Shared observability bootstrapping:
   - Prometheus scrape configuration
   - Grafana datasources
   - baseline dashboards
   - alerting and telemetry conventions
4. Shared messaging bootstrapping:
   - Kafka broker and supporting services
   - topic bootstrap conventions
   - platform-wide eventing standards
5. Documentation and governance for how backend services attach to shared infrastructure.
6. Migration planning and deprecation guidance when infra currently lives in service repos.
7. Drift detection for shared infra ownership where practical.

### Lotus application repos keep

1. Their own service instrumentation, metrics, and traces.
2. Their own service-specific dashboards and alert definitions.
3. Their own Kafka topic contracts, producer/consumer code, and event schemas.
4. Their own app-specific Docker Compose overlays for isolated development when needed.
5. Their own service health checks, readiness behavior, scaling policy, and operational runbooks.
6. App-owned bootstrap tasks consumed by platform-stack, such as:
   - topic bootstrap jobs
   - migration runners
   - service containers

## Non-Goals

`lotus-platform` does not become the owner of:

1. Domain business logic.
2. Service-local persistence schemas.
3. Service-specific ingestion/replay semantics.
4. Per-service dashboards that encode business-specific behavior.
5. Topic payload ownership for domain events.

## Governance Rules

1. No Lotus application repo is the canonical owner of a cross-service infrastructure product.
2. Shared infrastructure contracts must be documented in `lotus-platform`.
3. Every backend service must integrate with shared infra through explicit standards, not repo-local conventions.
4. Standalone dev stacks are allowed, but they are subordinate to the canonical platform stack.
5. Any future shared infra addition must land in `lotus-platform` first or concurrently with platform governance updates.
6. App repositories may keep isolated-dev compose overlays, but they must be labeled as non-canonical.
7. Shared Prometheus/Grafana/telemetry bootstrap files must not be described as platform-owned outside `lotus-platform`.

## Migration Plan

### Phase 1: Canonical ownership declaration

1. Adopt this RFC.
2. Update platform docs to state that `lotus-platform` owns shared infrastructure.
3. Keep current service-local assets functioning during transition.

### Phase 2: Platform-stack hardening

1. Ensure `platform-stack` is the canonical local bring-up path for:
   - Kafka
   - Prometheus
   - Grafana
   - telemetry collector
2. Align shared configuration and naming conventions.
3. Move platform-level dashboards and scrape configuration under `lotus-platform`.
4. Make platform docs explicit about which bootstrap tasks remain app-owned even when orchestrated by `platform-stack`.

### Phase 3: Service repo cleanup

1. Remove any implication that `lotus-core` or another app owns shared infrastructure.
2. Retain only service-local overlays and isolated-dev conveniences in app repos.
3. Update runbooks to point to `lotus-platform/platform-stack` for shared infra bring-up.
4. Reclassify app-local Docker Compose files so they are clearly isolated-dev overlays rather than platform defaults.

### Phase 4: Ongoing governance

1. Validate new services against shared infrastructure standards during bootstrap.
2. Keep observability and messaging conventions versioned centrally.
3. Use `lotus-platform` automation to detect drift where practical.

## Consequences

### Benefits

1. Cleaner service boundaries.
2. Easier onboarding for new Lotus services.
3. Consistent platform observability and messaging setup.
4. Less accidental operational coupling to `lotus-core`.

### Trade-offs

1. `lotus-platform` takes on more operational governance responsibility.
2. Platform-stack maintenance becomes a first-class workstream.
3. Service teams must distinguish shared infra ownership from service-local operational ownership.

## Acceptance Criteria

1. `lotus-platform` is documented as the owner of shared infrastructure.
2. `platform-stack` is treated as the canonical shared local/runtime baseline.
3. Service repos retain only service-local responsibilities for metrics, topics, and overlays.
4. No platform documentation describes `lotus-core` as the owner of Kafka, Prometheus, or Grafana for the rest of Lotus.
5. Shared Prometheus scrape configuration, Grafana datasource provisioning, and telemetry collector configuration are owned in `lotus-platform`.
6. `lotus-core` documentation describes its Docker Compose stack as app-local or isolated-dev, not as the canonical shared infrastructure baseline.
7. `platform-stack` can orchestrate the shared infra baseline without implying that app-owned bootstrap jobs transfer infra ownership.
