# RFC-0105 Slice 2 Closure Evidence

This note records the repair and re-proof work that closed the remaining Slice 2 gap after the
initial RFC ledger entry overstated the report-to-archive trace propagation.

## Scope

- RFC: `RFC-0105`
- Slice: `Slice 2 trace and structured logging`
- Repair repository: `lotus-report`
- Evidence repository: `lotus-platform`
- Evidence directory: `C:\Users\Sandeep\projects\lotus-report\output\rfc-0105-slice2-live-evidence-20260427-055407`

## Repair

`lotus-report` archive handoff now emits W3C `traceparent` only when the supplied `trace_id` is a
valid 32-character hexadecimal identifier, matching the existing render handoff behavior.

Files changed:

- `lotus-report/src/app/clients/archive_client.py`
- `lotus-report/tests/unit/clients/test_archive_client.py`

## Targeted Validation

Executed in `lotus-report`:

```text
python -m pytest tests/unit/clients/test_archive_client.py -q
python -m pytest tests/unit/test_observability.py tests/unit/clients/test_render_client.py tests/integration/test_api.py -q
docker compose up -d --build lotus-report
```

Observed result:

- archive client unit tests passed with positive and negative `traceparent` coverage
- targeted observability and API tests passed
- refreshed `lotus-report` container became healthy in the running local stack

## Live Proof Identifiers

- Correlation ID: `corr-rfc0105-slice2-20260427-055407`
- Trace ID: `e9b6f70ea5094ad8a3f742b57ea7ef65`
- Traceparent: `00-e9b6f70ea5094ad8a3f742b57ea7ef65-0000000000000001-01`
- Report request ID: `rrq_f432481d9abb4a57811efb1d110091c7`
- Report job ID: `rjob_5fe37956bb834d88be416ddef2cb7ba7`
- Snapshot ID: `rsnap_c2cf29d0eb9e4e379fbedbee79840845`
- Render job ID: `rdr_rjob_5fe37956bb834d88be416ddef2cb7ba7_pdf`
- Archive request ID: `arch_rdr_rjob_5fe37956bb834d88be416ddef2cb7ba7_pdf`
- Document ID: `doc_7c93b0a3b88e41ebb95c37308d97f4b6`
- Download checksum: `sha256:395bd60ab6072307815e86a3fca17c6618215b68b5bef183c4203cf0144c017d`

## Reconciliation

1. `create-report-job-response.json`, `gateway-report-job-status.json`, and `report-job-status.json`
   reconcile to a single archived report job.
2. `db-report-job.txt`, `db-report-input-snapshot.txt`, and `db-report-status-events.txt`
   reconcile job identity, snapshot identity, correlation id, trace id, and the seven expected
   status transitions from `accepted` through `archived`.
3. `logs-report.txt`, `logs-render.txt`, and `logs-archive.txt` preserve the same correlation id
   and trace id across the report to render to archive chain.
4. `archive-document-metadata.json`, `gateway-document-metadata.json`,
   `document-download-headers.txt`, and `archived-document.pdf` reconcile on document identity,
   checksum, and returned trace headers.
5. `sensitive-log-grep.json` records zero hits for `CIF_SG_000184`, `storage_key`, `bucket`,
   `raw_upstream_payload`, `portfolioName`, and `clientName` across the captured service logs.

## Evidence Boundary

This repair run re-proves:

- the corrected report-to-archive `traceparent` propagation,
- the report to render to archive trace chain in live runtime logs,
- gateway retrieval exposure through live API payloads and download headers,
- PostgreSQL-backed reconciliation for the report request, job, snapshot, and status events.

This repair run does not include durable gateway container log lines for the same correlation id in
the evidence folder. Gateway structured request-completion logging remains implementation-backed by
the previously merged Slice 2 gateway work and service-level test gates, but the durable artifacts
for this repair run are the gateway API responses and download headers rather than gateway log
lines.
