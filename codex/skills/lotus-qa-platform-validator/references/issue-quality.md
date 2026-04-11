# QA Issue Quality Standard

Each QA defect issue must include:

## Required fields
- Repository and check id.
- Run id and automation timestamp.
- Reproducible steps (ordered, minimal).
- Expected behavior.
- Actual behavior.
- Evidence references (artifact file path and key output).
- Test gap explanation.
- Recommended regression coverage.

## Evidence quality
- Prefer exact endpoint URL and returned status/body.
- Include short log excerpts with correlation context when available.
- Link created artifact path under `output/qa/<run-id>/evidence/...`.

## Acceptance for closure
- Fix merged and deployed in tested environment.
- Added tests fail before fix and pass after fix.
- Validator rerun shows check status as passing.
