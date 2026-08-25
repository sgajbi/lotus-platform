# Platform Stack

`platform-stack` is the canonical shared-infrastructure and local integration baseline for Lotus.
It is not the canonical populated front-office demo runtime; that flow is owned by
`lotus-workbench`.

The stack containerises:

- `lotus-core` ingestion, query, and control-plane services, with Kafka and PostgreSQL
- `lotus-manage`, `lotus-performance`, `lotus-report`, `lotus-idea`, `lotus-gateway`, and
  `lotus-workbench`
- Prometheus, authenticated Grafana, the OpenTelemetry Collector, and Tempo
- Caddy-based local ingress

The ingress and Prometheus configuration bridge to host-run `lotus-risk`, `lotus-advise`,
`lotus-ai`, `lotus-archive`, and `lotus-render` through `host.docker.internal`. Containerized
`lotus-idea` also consumes the host-run Risk, Advise, and AI services through that governed bridge.
Those applications are observed and routed here but are not started by this Compose project.

## Ownership boundaries

`lotus-platform` owns the shared infrastructure definitions and baseline configuration in this
directory. Application repositories own their images, migrations, bootstrap jobs, instrumentation,
and application-specific dashboard content. Grafana provisioning and the shared Prometheus scrape
inventory are platform-owned; application-local observability stacks remain valid for isolated
development but are not this shared baseline.

Cross-cutting rules are defined by
[`Platform Observability Standards`](../docs/standards/Platform%20Observability%20Standards.md) and
[`cross-cutting-platform-contract.yaml`](../platform-contracts/cross-cutting-platform-contract.yaml).

## Bootstrap

Generate `platform-stack/.env` once. The bootstrap derives repository paths from the workspace and
generates independent 256-bit secrets. It fills missing or empty values and never overwrites a
non-empty operator value. `.env` is ignored by Git; do not copy credentials back into
`.env.example` or Compose.

Windows:

```powershell
cd lotus-platform
./platform-stack/bootstrap.ps1 -WorkspaceRoot ..
```

macOS or Linux:

```sh
cd lotus-platform
./platform-stack/bootstrap.sh ..
```

Run either bootstrap again after pulling new variables. It safely adds only missing values. The
tracked `.env.example` contains non-secret defaults and blank path/secret placeholders only.
Bootstrap rejects the former tracked Core database password before changing the environment file.
Clear that value only when initializing a fresh database; when legacy data matters, follow the
dump/restore migration path below and set an operator-managed secret explicitly. Database
usernames, passwords, and database names are embedded in PostgreSQL connection URIs and must use
only letters, numbers, dot, underscore, tilde, and hyphen; bootstrap rejects other characters
before changing the file. Tracked service environments in the base file and every supported overlay
use mapping form; list-form environments are validator-rejected so credential and DSN scanning
cannot be bypassed through alternate Compose syntax or profiles.

### Upgrade from the pre-hardening stack

PostgreSQL applies database, role, and password initialization only when a volume is empty. Do not
attach a volume created by the earlier stack identities to this profile and assume bootstrap has
migrated it. The renamed Compose project otherwise creates fresh sibling volumes. The complete
pre-hardening inventory is `pbwm-platform_lotus-core-postgres-data`,
`pbwm-platform_lotus-manage-postgres-data`, `pbwm-platform_lotus-report-postgres-data`, and
`pbwm-platform_grafana-data`. The explicit `lotus-manage-postgres-identity-v2-data` key always
creates a fresh Manage database because that database identity changed; legacy Manage state remains
untouched and must be migrated through a database-level dump and restore.

Before starting the renamed project, inspect every exact legacy target and choose one explicit
recovery path. Take a backup before either migration or adoption.

1. **Migrate to fresh volumes (required for Manage, recommended for databases whose credentials
   changed):** start the old project from its old revision, create logical `pg_dump` backups for
   Core, Manage, and Report, export any operator-authored Grafana dashboards, stop the old project,
   bootstrap this stack, restore into the new databases, and verify the owning application
   contracts. Do not byte-copy PostgreSQL storage across identities or versions.
2. **Adopt unchanged Core, Report, and Grafana volumes:** first stop the old project. Before adoption,
   remember that PostgreSQL and Grafana initialization variables do not rename identities in
   existing volumes. Unless you explicitly rename and verify the persisted identities first, set
   `LOTUS_CORE_POSTGRES_USER=user` and `GRAFANA_ADMIN_USER=admin` in the new untracked `.env`;
   Report retains `LOTUS_REPORT_POSTGRES_USER=lotus_report`. Rotate the Core and Report
   database-role passwords in the old databases to the exact new `.env` values, reset the persisted
   Grafana admin password to `GRAFANA_ADMIN_PASSWORD`, and validate database and Grafana login while
   the old project is still available. Then start with the governed adoption overlay:

   ```powershell
   docker compose -f docker-compose.yml -f docker-compose.legacy-volumes.yml config --quiet
   docker compose -f docker-compose.yml -f docker-compose.legacy-volumes.yml up -d --build
   ```

   The overlay maps all three unchanged logical volumes to their exact `pbwm-platform_*` names. Its
   validator permits only those aliases and rejects every service-mount override, so it cannot
   attach legacy Manage state indirectly. Continue using the overlay on every subsequent command
   until the data is migrated to fresh canonical volumes.
3. **Discard disposable state:** inspect and remove only the intended exact legacy volume, for
   example `docker volume inspect pbwm-platform_lotus-manage-postgres-data` followed by
   `docker volume rm pbwm-platform_lotus-manage-postgres-data`. Repeat explicitly for another
   disposable volume; never build a broad deletion command from discovered names.

Do not use a current Compose model with `down --volumes` to retire the old project: it can delete
declared sibling data while leaving undeclared legacy state untouched. Never attach the legacy
Manage volume to the new service identity. Bootstrap migrates environment variables only; it never
rewrites database users, Grafana credentials, or stored data.

Add the entries from `dev-ingress/hosts.example` to the local hosts file. On Windows, the governed
helper can stage or apply the managed block:

```powershell
./automation/Sync-Dev-Ingress-Hosts.ps1
./automation/Sync-Dev-Ingress-Hosts.ps1 -Apply
```

If applying without elevation fails, use `output/hosts-preview/hosts.merged`.

## Start and validate

From `platform-stack`:

```powershell
docker compose config --quiet
docker compose up -d --build
```

The base profile exposes only Caddy and OTLP receiver ports, all bound to `127.0.0.1`. For
debug-only direct service ports, add the host-port profile:

```powershell
docker compose -f docker-compose.yml -f docker-compose.host-ports.yml up -d --build
```

Port conflicts are resolved with the corresponding `.env` value, for example
`DEV_INGRESS_HTTP_PORT`, `OTEL_HTTP_PORT`, or `LOTUS_GATEWAY_PORT`.

Run the ingress checks from the repository root:

```powershell
./automation/Validate-Dev-Ingress-Smoke.ps1
./automation/Explain-Dev-Ingress-Status.ps1
```

The explainer distinguishes DNS, HTTP, connection-refused, timeout, and transport failures and
names the exact Compose services to inspect or refresh.
Its stable evidence values are `dns_resolution_failed`, `http_error`, `connection_refused`,
`timeout`, and `transport_error`; retain those identifiers in support evidence and automation.

When every routed service fails at the edge while DNS is healthy, inspect Caddy and refresh only
the ingress service:

```powershell
docker compose logs --tail=200 dev-ingress
docker compose up -d dev-ingress
```

## Optional local TLS profile

The default HTTP profile is loopback-only. To exercise HTTPS, add the Caddy local-CA profile:

```powershell
docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d --build
```

This publishes `DEV_INGRESS_HTTPS_PORT` on `127.0.0.1`, persists Caddy's local CA in the
`caddy-data` volume, and serves the same `*.dev.lotus` routes over HTTPS. The local Caddy root must
be trusted explicitly on each workstation before browsers and SDKs accept it; never distribute its
private key or treat this development CA as a production PKI. The HTTP listener remains available
for compatibility and redirects are managed by Caddy in this profile.

## Service entry points

Use these stable local identities instead of container ports:

- Workbench: `http://workbench.dev.lotus`
- Gateway: `http://gateway.dev.lotus/health/ready`
- Core query: `http://core-query.dev.lotus/health/ready`
- Core control: `http://core-control.dev.lotus/health/ready`
- Core ingestion: `http://core-ingestion.dev.lotus/health/ready`
- Manage: `http://manage.dev.lotus/health/ready`
- Performance: `http://performance.dev.lotus/health/ready`
- Report: `http://report.dev.lotus/health/ready`
- Idea: `http://idea.dev.lotus/health/ready`
- Prometheus: `http://prometheus.dev.lotus`
- Grafana: `http://grafana.dev.lotus`

The same hostnames use `https://` with the TLS profile. Grafana anonymous access is disabled; use
`GRAFANA_ADMIN_USER` and the generated `GRAFANA_ADMIN_PASSWORD` from the untracked `.env`.

## Observability and recovery

Services send OTLP to `otel-collector`. Traces are exported to Tempo and retained locally for 24
hours; metrics and logs currently remain diagnostic collector output. Grafana provisions both
Prometheus and Tempo datasources. Telemetry is fail-open for applications: a collector or Tempo
failure must not change financial processing, but it can cause telemetry loss and must be visible in
container health and collector exporter metrics. `dev-ingress` therefore waits for healthy
application services but never depends on Prometheus, Grafana, Tempo, or the collector; an
observability outage cannot suppress otherwise healthy application routes.

To prove a known trace is queryable, submit it through OTLP and query Tempo from inside the project:

```powershell
docker compose exec tempo wget -q -O - http://127.0.0.1:3200/api/traces/<32-hex-trace-id>
```

A successful response must contain the expected service and span names. A `404` means the trace is
not retained and is a failed observability proof, even if the collector container is healthy.

Every long-running service has a healthcheck and an explicit local resource ceiling. Small
infrastructure uses `0.5 CPU / 256 MiB`, ordinary services use `1 CPU / 512 MiB`, and Kafka plus
other large services use `2 CPU / 1 GiB`. These are deterministic local safety bounds, not
production sizing guidance.

## Operations

```powershell
docker compose ps
docker compose logs --tail=200 lotus-gateway lotus-core-query lotus-core-control
docker compose down
```

`docker compose down --volumes --remove-orphans` also deletes local database, Grafana, Caddy, and
Tempo state. Use it only when intentional recovery requires a clean local data plane.
