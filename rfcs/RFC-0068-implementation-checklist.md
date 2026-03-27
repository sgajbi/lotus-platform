# RFC-0068 Implementation Checklist

## Goal

Turn RFC-0068 into an explicit ownership migration with concrete file-level moves and cleanup work.

## Phase A: Ownership and documentation baseline

### lotus-platform

1. Keep RFC-0068 as the governing ownership source:
   - `rfcs/RFC-0068-centralized-shared-infrastructure-ownership-and-migration.md`
2. Keep platform-stack as the canonical shared-infra entrypoint:
   - `platform-stack/docker-compose.yml`
   - `platform-stack/README.md`
3. Keep platform observability standards as the cross-app source:
   - `Platform Observability Standards.md`

### lotus-core

1. Remove wording that presents `lotus-core` as the default owner of:
   - Kafka
   - Prometheus
   - Grafana
2. Reclassify:
   - `docker-compose.yml`
   as app-local / isolated-dev, not canonical platform infrastructure.
3. Update operator docs to say that shared Grafana and Prometheus are expected to come from:
   - `lotus-platform/platform-stack`

## Phase B: Shared observability ownership

### Target owner: lotus-platform

Canonical shared observability files:

1. `platform-stack/prometheus/prometheus.yml`
2. `platform-stack/grafana/provisioning/datasources/datasource.yml`
3. `platform-stack/otel-collector/config.yaml`

### Files to review in lotus-core

1. `prometheus/prometheus.yml`
   - decide whether any scrape rules are still platform-owned
   - move shared scrape ownership to `lotus-platform`
2. `grafana/provisioning/datasources/datasource.yml`
   - should not remain the canonical shared datasource bootstrap
3. `grafana/provisioning/dashboards/dashboard.yml`
   - keep only if needed for app-local overlay
4. `grafana/dashboards/portfolio_analytics.json`
   - keep as app-owned dashboard content if still specific to lotus-core

### Desired end state

1. Shared datasource provisioning owned only in `lotus-platform`
2. Shared scrape config owned only in `lotus-platform`
3. App-specific dashboards may still live in app repos
4. App repos must not imply that their Grafana/Prometheus files are platform defaults

## Phase C: Shared messaging ownership

### Target owner split

Shared messaging infrastructure owner:

1. Kafka broker lifecycle
2. supporting infra wiring
3. canonical stack orchestration

Target repository:

1. `lotus-platform`

App-owned messaging responsibilities:

1. topic definitions
2. producer / consumer code
3. event schemas
4. topic bootstrap jobs

Current app-owned file that should remain app-owned:

1. `lotus-core/tools/kafka_setup.py`

### Required clarification

`platform-stack` may invoke app-owned topic bootstrap jobs without changing ownership of:

1. Kafka infra
2. domain topic contracts

## Phase D: Compose model cleanup

### lotus-platform

1. Keep `platform-stack/docker-compose.yml` as the canonical full-platform baseline
2. Make README language explicit that app-owned jobs are orchestrated by, not owned by, platform-stack

### lotus-core

1. Reword `docker-compose.yml` as:
   - app-local stack
   - isolated development stack
   - non-canonical for shared infra
2. Consider later split into:
   - `docker-compose.app-local.yml`
   - app-local overlays

## Phase E: Drift detection

### Add automation in lotus-platform for:

1. docs that describe app repos as shared infra owners
2. duplicate shared Prometheus datasource provisioning outside `lotus-platform`
3. duplicate platform-level scrape ownership outside `lotus-platform`
4. future shared infra additions landing without platform governance updates

## First implementation slice

1. Tighten RFC-0068 wording
2. Update `platform-stack/README.md`
3. Update `Platform Observability Standards.md`
4. Update `lotus-core/README.md`
5. Update `lotus-core` Grafana/ops docs so they refer to platform-stack as canonical

## Later slices

1. Move or reclassify shared Prometheus/Grafana files in app repos
2. Split app-local compose from platform-default compose in `lotus-core`
3. Add drift-detection automation
