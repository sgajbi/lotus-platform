# Service Mapping

Source of truth:

`<lotus-platform>/automation/service-map.json`

Purpose:

- Map repo path changes to docker compose services
- Carry non-secret canonical Compose environment required for shared-stack coexistence
- Declare post-refresh health and published-port verification
- Enable `-ChangedOnly` refresh flow
- Keep minimal downtime and faster feedback loops

`composeEnvironment` values are applied only to the refresh process and restored afterward.
Environment names must be uppercase and cannot contain credential-bearing names such as `TOKEN`,
`PASSWORD`, `SECRET`, or `API_KEY`; process-critical names such as `HOME`, `PATH`, and `TEMP` are
also rejected. `serviceVerification` can require healthy state and exact target/published port
pairs. A missing container, non-running state, unhealthy state, malformed Compose JSON, or port
mismatch fails the refresh.

Before a shared-stack refresh, run `-DryRun` and verify the reported services, environment, and
ports. The governed Manage entry must preserve Advise on host port 8000 by publishing Manage as
`8001:8000` and must retain its canonical Core source/workflow settings.
