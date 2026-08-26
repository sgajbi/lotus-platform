# Lens-Based Hardening Promotion

Use issue-discovery lens findings as raw signal for hardening, not as automatic CI requirements.
Promote only lenses that repeatedly produce objective, deterministic, low-noise failures.

## High-signal lens families

1. `lens/architecture-boundaries`: import-direction, runtime-composition, and package-boundary checks.
2. `lens/api-documentation-standards`: OpenAPI quality, operation IDs, response examples,
   route-inventory, vocabulary/no-alias, and duplicate endpoint checks.
3. `lens/http-boundary-controls`: secure headers, CORS, trusted hosts, content type, body-size, and
   abuse-boundary checks.
4. `lens/configuration-secrets`: required settings, unsafe defaults, secret-like values, and
   environment parity checks.
5. `lens/validation-idempotency`: idempotency-store, same-key/different-payload, conflict, retry,
   and replay contract tests.
6. `lens/auditability-lineage`: correlation, source identity, evidence fingerprint, audit, and
   lineage contract checks.
7. `lens/capability-publication`: supported-feature, capability registry, Gateway/Workbench
   publication, and implementation-truth gates.
8. `lens/evidence-proof-contracts`: proof schema, reproducibility, evidence provenance, and
   scorecard freshness checks.
9. `lens/observability`: no-sensitive logging/metrics, bounded labels, route templates, health,
   readiness, and dashboard/alert contract checks.
10. `lens/security-privacy`: first-party security rules, authorization denial tests, sensitive-data
    scans, dependency scanner posture, and abuse-control checks.
11. `lens/testing-quality`: required test-family breadth, uncategorized-test caps, mutation or
    golden-fixture checks where stable.
12. `lens/ci-release-evidence`: workflow permissions, timeouts, no critical `continue-on-error`,
    repo-native target usage, Docker/runtime proof, and main releasability dispatch checks.
13. `lens/dependency-hygiene` and `lens/environment-supply-chain-provenance`: lockfile, scanner,
    SBOM, pinned image, signing, OCI labels, digest capture, version parity, and provenance.
14. AI lenses only when the app has an AI surface: `lens/ai-data-boundaries`,
    `lens/ai-evaluation-quality`, `lens/ai-safety-abuse-controls`, and
    `lens/ai-agent-tool-governance`.

For Docker/image provenance gates, prefer one deterministic validator for the deployable-image
chain: immutable Git-SHA tags, OCI build metadata, CI-only publishing, digest manifests, SBOM,
vulnerability result or time-bounded exception, signing, attestation, digest deployment, version
endpoint parity, promotion of the same image, and no secret leakage through build/runtime metadata.
The validator must also prove Compose-declared worker/operator asset closure with a bounded image
smoke and focused pass/fail contract test; keep packaging and provenance failures diagnosable.

Keep product-workflow, client-communication, customer-impact, localization, third-party-vendor,
and broad dead-code lenses review-only until they have objective, low-noise rules. Before promoting
any lens-derived gate, record the source issues/root causes, deterministic rule, repo-native command,
lane, pass/fail tests, baseline, exception policy, blocking posture, and required scorecard/docs/
context updates. Use `lotus-app-issue-discovery` validators for taxonomy consistency and candidate
selection; never gate on issue count.
