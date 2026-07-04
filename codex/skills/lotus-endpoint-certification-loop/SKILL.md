---
name: lotus-endpoint-certification-loop
description: Certify Lotus API endpoints end to end across behavior, every returned figure, OpenAPI/Swagger documentation, GitHub issues, upstream and downstream integrations, duplicate/dead endpoint detection, live canonical evidence, and test-pyramid adequacy. Use when a user asks to test, certify, harden, production-grade review, or move endpoint-by-endpoint through Lotus APIs in lotus-performance, lotus-risk, lotus-core, lotus-gateway, lotus-advise, lotus-manage, lotus-report, or related Lotus services.
---

# Lotus Endpoint Certification Loop

Use this skill with the repo delivery-governance skill that matches the target app. Keep the work
endpoint-scoped and finish one endpoint before moving to the next.

## Start

1. Load the mandatory Lotus context for the target repo.
2. Identify the exact endpoint path, method, request/response models, service path, tests, docs,
   upstream sources, and downstream consumers.
3. State the repo, branch, endpoint, task intent, applicable standards, and validation lane before
   editing.
4. Search open GitHub issues in the owning repo and known downstream repos for the endpoint path,
   model names, and domain vocabulary.

## Certification Checks

For each endpoint, verify and improve:

1. Purpose and ownership:
   - when to use the endpoint;
   - when not to use it;
   - whether a more strategic endpoint already exists;
   - whether the endpoint is product-facing, integration-facing, operator-facing, or internal.
2. Contract options:
   - every request option and mode;
   - defaults and validation behavior;
   - sync and async paths;
   - result polling routes;
   - error behavior.
3. Output figures:
   - every returned amount, percentage, ratio, date, count, summary, diagnostic, provenance, and
     metadata field;
   - totals, subtotals, reconciliation fields, and row-level details;
   - unit conventions such as percentage points versus decimal ratios;
   - domain formulas against private-banking, quant, performance, or risk expectations.
4. Upstream integration:
   - canonical upstream service and base URL;
   - route method and request body shape;
   - source lineage and snapshot capture;
   - chunking, paging, concurrency, and timeout behavior;
   - stale assumptions such as old GET routes, wrong read-plane/control-plane service names, or
     ungoverned aliases.
5. Downstream integration:
   - direct consumers in gateway, risk, workbench, report, advise, manage, or other Lotus apps;
   - whether consumers use the endpoint correctly;
   - whether useful front-office features are omitted from the UI;
   - whether a downstream app should migrate from a duplicate endpoint to the strategic endpoint.
6. Documentation:
   - Swagger operation summary and description explain purpose and use;
   - every request and response attribute has description, type, and example where practical;
   - README, API reference, methodology, operator, and certification docs match implementation.
7. Tests:
   - model validation tests for schema and mode constraints;
   - service/unit tests for formulas and helper edge cases;
   - integration tests for request options and every output family;
   - async/result route tests where applicable;
   - docs/OpenAPI tests for schema quality;
   - live canonical proof when the endpoint affects seeded product flows.

## Issue Handling

If an open issue is still valid, fix it or document why it remains out of scope. If the issue is
already addressed, close it only when evidence is current and specific.

If a downstream consumer uses a duplicate or stale endpoint, create a GitHub issue in that
downstream repository. Include:

1. current consumer path and behavior;
2. strategic endpoint to use instead;
3. migration reason;
4. user or production impact;
5. exact request/response evidence;
6. acceptance criteria and validation commands.

Do not remove a public endpoint until downstream migration and deprecation are governed.

## Evidence

Record endpoint certification in a repo-local technical document when the work is substantial. The
document should include supported options, figure tie-outs, upstream/downstream posture, issue
disposition, test-pyramid assessment, live proof, and any residual risks.

Run focused validation first. For API contract changes, also run OpenAPI and vocabulary gates. For
service/model changes, run type checks according to the repo-native pattern.

Commit the endpoint slice with a small, meaningful message after focused validation passes.

## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work revealed a repeatable failure,
missing endpoint-certification step, weak trigger, validation gap, context-routing gap, or
documentation/source-of-truth drift that should change future agent behavior.

When the lesson is durable, update the platform-owned skill source under
`lotus-platform/codex/skills`, and update the routing map, context, validators, scaffolds, gates, or
templates that enforce the new behavior. When no durable change is needed, record the explicit
no-skill/no-context decision in the PR, issue, ledger, or final evidence.
