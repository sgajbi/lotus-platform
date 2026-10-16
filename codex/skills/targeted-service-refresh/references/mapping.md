# Service Mapping

Source of truth:

`<lotus-platform>/automation/service-map.json`

Purpose:

- Map repo path changes to docker compose services
- Carry non-secret canonical Compose environment required for shared-stack coexistence
- Declare daemon readiness or explicit one-shot completion verification
- Enable `-ChangedOnly` refresh flow
- Keep minimal downtime and faster feedback loops

`composeEnvironment` values are applied only to the refresh process and restored afterward.
Environment names must be uppercase and cannot contain credential-bearing names such as `TOKEN`,
`PASSWORD`, `SECRET`, or `API_KEY`; process-critical names such as `HOME`, `PATH`, and `TEMP` are
also rejected. By default, services are daemons: `serviceVerification` can require healthy state
and exact target/published port pairs, in addition to running state. Missing containers,
non-running daemons (including exited/0), unhealthy state, malformed Compose JSON and required
port mismatches fail readiness. Daemon queries retain Compose's running-only default.

Core `migration-runner` explicitly declares `completionPolicy: exited-zero`. This policy requires
the reviewed reserved path; unknown or malformed policies refuse. Before any build/up, require
exactly one acquired project/service resource and inspect its original full container ID as the
exact Compose project/service with strict `com.docker.compose.oneoff=False`. Acquired historical
runs, missing/duplicate resources, malformed metadata and foreign identity refuse before mutation;
never remove or reclassify acquired bindings to make the topology fit.

Build and prepare every selected immutable image/source first. Force-recreate only the migration
with pinned images and `--no-deps --no-build --pull never`, then await successful completion before
replacing the selected applications. Only job queries use `ps --all`; inspect every candidate's
identity and one-off metadata to select exactly one real service container, independent of names
or row order. Historical `compose run` observations cannot satisfy completion. Created/running
jobs remain pending within `HealthTimeoutSeconds`; success requires inspected exited state with
integer exit 0, no OOM, no restarts or execution error, and exact prepared image/repository/checkout/
source identity. Missing, ambiguous, malformed, nonzero or drifting evidence refuses.

Migration completion failure replaces no selected applications. A failed/interrupted reserved
refresh remains pending under the original holder and expiry, requiring explicit reviewed recovery.
Finish still requires complete acquired cardinality and exact untouched identities; readiness
filtering never changes that accounting. Readiness-only non-acquired run observations are not
canonical finish proof. Follow the [reviewed incremental refresh runbook](https://github.com/sgajbi/lotus-platform/blob/main/docs/operations/canonical-runtime-reservation.md#reviewed-incremental-refresh)
for admission, recovery and separate live-acceptance evidence; do not blindly rerun or regrant.

Before a shared-stack refresh, run `-DryRun` and verify the reported services, environment, and
ports. The governed Manage entry must preserve Advise on host port 8000 by publishing Manage as
`8001:8000` and must retain its canonical Core source/workflow settings.
