---
name: lotus-demo-readiness-certification
description: Use when a Lotus app must be demo-ready, when the user asks to validate all APIs/features/calculations before a demo, when adding repeatable demo seed data or certification commands, when preparing a client-facing demo pack or operating process, or when reviewing demo evidence across backend APIs, frontend product surfaces, gateway flows, seeded data, observability, and supportability. Applies across Lotus apps; use app-specific delivery/runtime skills as supporting guidance.
---

# Lotus Demo Readiness Certification

Use this skill to turn "make it demo ready" into evidence-backed app validation, not screenshots or
HTTP 200 checks alone.

For client-facing demo process work, use:

1. `lotus-platform/docs/standards/Lotus Client Demo Certification Standard.md` for claim states,
   evidence rules, and certification posture,
2. `lotus-platform/docs/demo/client-demo-operating-process.md` for client intake, demo-pack
   structure, rehearsal, delivery, and follow-up,
3. `lotus-platform/docs/demo/canonical-dpm-demo-story.md` for the governed canonical DPM demo
   narrative when the demo uses the front-office reference flow.

## Core Rule

Prove the supported demo scope through one repeatable app-level validation entrypoint when practical.
Review the generated evidence, fix broken or weak proof, then rerun until the evidence is coherent.
Do not claim demo readiness from unreviewed artifacts.

## Scope Intake

Before changing code or data, identify:

1. the app and demo date,
2. the audience, buying question, use case, sensitivity level, and demo objective,
3. the supported demo surfaces, APIs, panels, calculations, workflows, and seeded portfolios or
   entities,
4. the app-owned source of truth for supported features or capabilities,
5. the existing seed automation and whether it is deterministic,
6. the closest unit, integration, e2e, runtime, and docs tests,
7. the single repo-native validation command that already exists, or the gap if none exists.

If the app has a governed front-office Workbench path, also use `lotus-front-office-runtime`.
If the task is backend/API focused, also use `lotus-backend-delivery-governance`.
If the task changes CI or promotes a gate, also use `lotus-ci-enforcement-governance`.
Use `lotus-pr-premerge-gate` before PR/merge.

## Single Validation Entry Point

Prefer one app-level command that:

1. seeds deterministic synthetic/demo data when required,
2. calls real APIs, BFFs, CLI workflows, or browser flows instead of only importing services,
3. validates domain figures and business invariants, not just successful responses,
4. verifies capability or supported-feature publication matches implemented surfaces,
5. checks health/readiness, safe errors, observability, and supportability states where relevant,
6. writes machine-readable evidence under an app-local `output/` or governed evidence directory,
7. exits non-zero on any failed assertion.

Keep small focused tests around the validation command:

1. unit tests for deterministic helper logic,
2. integration/API tests for the full certification function when it is fast and local,
3. e2e or browser tests when product screens or gateway/BFF flows are part of the demo.

## Evidence Review

After running the command, inspect the evidence and fix issues before claiming readiness.

Review for:

1. missing supported APIs, features, panels, or workflows,
2. stale seeded data or unsupported empty/demo placeholders,
3. calculation drift, weak tie-outs, or numbers without expected-value assertions,
4. capability registry or supported-feature drift,
5. failed, degraded, stale, unavailable, or permission-blocked states,
6. sensitive data in evidence, logs, screenshots, metrics, or diagnostics,
7. artifacts that were produced but not validated by assertions.

If evidence exposes a real defect, fix the source issue and add focused tests. Do not weaken the
certification command unless the check is demonstrably outside supported demo scope; document that
decision.

## Seed Data

Use synthetic or approved demo data only.

Seed automation must be:

1. deterministic,
2. idempotent or safely resettable,
3. documented through a repo-native command,
4. covered by tests for expected records or entities,
5. free of real client data, account data, secrets, credentials, and personal data.

If seed data is required but absent, create repeatable seed automation before relying on manual data.

## Gate Posture

Demo certification commands may start report-only or manually invoked.

Promote them into blocking CI only when `lotus-ci-enforcement-governance` intake is satisfied:
measured baseline, deterministic behavior, low false positives, pass/fail tests, clear lane
placement, and documented exception policy.

When the command is fast and deterministic enough for CI but not ready to block, add it to the
repo's reporting or quality snapshot lane as report-only evidence:

1. run the same repo-native command used locally,
2. upload the machine-readable evidence artifact,
3. mark the step non-blocking while signal is being gathered,
4. document the lane placement and non-blocking posture in repo docs, wiki, scorecard, or CI-gate
   guidance,
5. promote to a blocking feature, PR, or main gate only after repeated CI runs prove stability and
   the owner has defined remediation and exception handling.

## Closure

A demo-readiness slice should leave:

1. one documented command for the app,
2. reviewed machine-readable evidence,
3. focused unit/integration/e2e coverage where needed,
4. a client-safe demo pack or operating-process update when the work affects client-facing demos,
5. docs, scorecards, and review ledgers updated with code truth,
6. any residual risks stated with exact unsupported surfaces or stale evidence,
7. branch/PR/main hygiene handled through Lotus pre-merge governance when code changes.
