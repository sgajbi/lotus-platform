# Lotus QA Checklist

Use this checklist for every service validation run.

## Runtime bring-up
- Start service via default startup or docker compose.
- Confirm process/container health before probes.
- Capture startup logs and errors.

## API validation
- Probe `/health` and expected core API endpoints.
- Probe docs endpoint (`/docs` or repo-defined equivalent).
- Verify status codes and response shape.

## Observability validation
- Probe `/metrics`.
- Verify expected metric names and non-empty payload.
- Check logs for correlation/tracing keys and service identity.
- Verify traceability/lineage signals where required.

## Standards validation
- Backend foundation standards.
- OpenAPI conformance expectations.
- Durability and consistency controls.
- Platform contract items (health, metrics, correlation, tracing).
- Rounding/precision consistency rules.

## Defect handling
- Record reproducible steps.
- Capture evidence file paths and key snippets.
- Include expected vs actual behavior.
- Explain why existing tests did not catch it.
- Recommend missing regression tests.
