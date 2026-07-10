---
name: lotus-ci-enforcement-governance
description: Use when designing, promoting, reviewing, or fixing Lotus CI enforcement, quality gates, repository-native Make/NPM targets, GitHub Actions lanes, regression blockers, quality scorecards, or agent-facing development guardrails. Apply when the user asks to improve CI, prevent future degradation, make agent-driven work higher quality, promote report-only inventories to blocking gates, or update skills/context so enforcement patterns are reusable across Lotus repositories.
---

# Lotus CI Enforcement Governance

Use this skill to convert proven quality signals into high-signal, low-noise CI enforcement.

Read `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md` when choosing
which signals deserve promotion. CI should reinforce the bank-buyable controls that prevent
architecture drift, unsupported contracts, weak tests, security regressions, observability
regressions, and documentation truth drift across Lotus apps.

## Core Rule

Promote gates that prevent real degradation. Do not add cosmetic, subjective, flaky, or redundant
checks just because a metric exists.

## Gate Promotion Standard

Before making a quality signal blocking, confirm:

1. the current baseline is measured and reproducible,
2. the finding class has clear engineering consequence,
3. the gate has a repo-native local command,
4. false positives and exceptions are understood,
5. the gate is fast enough for its intended lane,
6. focused unit tests cover pass and fail behavior,
7. quality artifacts and scorecards will reflect the new truth,
8. the PR evidence will show the command that developers and agents should run,
9. the blocking command does not create or rewrite durable report artifacts in a clean checkout.

When the same scanner has both blocking and evidence-producing modes, keep those entrypoints
separate. Wire the clean blocking target into `make check`, `make ci`, and GitHub lanes; reserve
report artifacts for explicit report-only commands used by scorecards, RFC proof, or review
evidence.

Prefer promoting clean, deterministic inventories with zero accepted findings first, such as:

1. architecture boundary violations,
2. router or middleware thinness violations,
3. first-party security findings,
4. duplicate first-party implementation hotspots,
5. API vocabulary or OpenAPI contract drift,
6. repository-native domain contract validation.

Also consider regression-blocking thresholds for deterministic non-zero inventories when the
failure mode is clear and the current baseline is stable. Good examples: minimum API/runtime test-family breadth,
minimum contract/governance test-family breadth, and maximum uncategorized-test backlog. These gates
should block loss of proof or unchecked taxonomy drift; they should not pretend that the entire
taxonomy is mature.

Keep report-only until stable when the signal is noisy or policy is not settled, such as:

1. maintainability index,
2. broad dead-code scans with framework false positives,
3. public docstring percentage,
4. branch coverage before measurement is configured,
5. dependency hygiene with unresolved runtime-only declarations.

## Implementation Pattern

For a new enforcement gate:

1. add threshold arguments to the existing inventory script instead of duplicating scanners,
2. add a Make/NPM target with a clear name,
3. wire the target into the repo's canonical local aggregate command,
4. add it to the right GitHub Actions lane:
   - fast static gates for deterministic static analysis,
   - contract/security gates for security, dependency, API, vocabulary, and migration checks,
   - PR/main lanes for heavier integration, coverage, Docker, and runtime validation,
5. add focused tests for passing and failing threshold behavior,
6. update quality reports, scorecards, review ledgers, and PR evidence,
7. fix discovered root causes before adding allowlists or suppressions.

For test-taxonomy or proof-breadth gates, keep total test count as context rather than the gate itself.
Gate the stable families that matter to bank-buyable behavior, such as API/runtime,
contract/governance, observability/security, or methodology proof, and cap uncategorized growth only
when the current count is measured and the exception policy is explicit.

When a newly promoted gate finds issues, fix the issue class directly if the code change is narrow.
Use allowlists only when the allowlist is truthful current-state governance and is documented.

Before changing CI enforcement, produce a short enforcement intake:

1. name the current measured baseline and the artifact that records it,
2. identify the exact failure mode the gate prevents and why it matters for bank-buyable quality,
3. prove the signal is deterministic by running the repo-native command locally,
4. identify the intended lane and why it belongs there instead of a lighter or heavier lane,
5. define the exception or allowlist policy before any exception is added,
6. list the focused tests that prove both pass and fail behavior for the gate,
7. state which scorecard, ledger, docs, skill, or context artifact must be updated with code truth.

For `lotus-platform` enterprise backend refactors, the first measured baseline artifact is
`quality/baseline_report.md`, generated by
`python automation/generate_enterprise_backend_quality_baseline.py --write --check`. Treat
`quality/quality_scorecard.md` and `quality/refactor_health_report.md` as required PR evidence
surfaces for before/after movement and slice-by-slice health notes.

Do not promote a gate from intuition alone. If the signal cannot meet this intake, keep it
report-only. Use it for planning until baseline, false-positive, lane-placement, and exception
policy are settled.

## Agent-Driven Development Guardrails

For repositories where agents do most implementation work, prefer gates that:

1. fail before expensive test matrices,
2. point to the exact file, rule, and remediation,
3. are runnable through one repo-native command,
4. prevent copy-paste drift, boundary erosion, insecure patterns, and API contract drift,
5. produce artifacts future agents can read before choosing the next slice.

Avoid gates that require agents to infer subjective design preferences from vague failure text.

Prefer enforcement that blocks common agent failure modes:

1. copied implementation hotspots that a deterministic duplicate inventory can identify,
2. architecture-boundary imports or ownership drift that make modules harder to reason about,
3. unsupported API shape, OpenAPI, vocabulary, no-alias, or contract drift,
4. first-party security scanner findings and unsafe production assertions,
5. missing contract validation for data migrations, runtime evidence, or cross-service payloads.
6. accidental removal of Makefile or GitHub Actions lane controls that are already part of the
   bank-buyable baseline.
7. removal of API/runtime or contract/governance tests hidden by unchanged or growing total test
   counts.
8. growth in uncategorized tests that makes future agents unable to tell which proof family a test
   protects.

When a repository has a canonical CI/runtime service-set registry, scripts and tests must consume
that registry instead of copying service lists into each workflow helper or assertion. If a runtime
failure shows that a bootstrap, migration, topic, seed, or control-plane service was omitted from a
gate, fix the shared service set first, then remove duplicated expected command lists from adjacent
tests so the same drift cannot recur in latency, E2E, performance, failure-recovery, or
institutional gates.

For agent-generated code, prefer gates that enforce "improve or preserve" rather than "barely pass":
quality scorecards, duplicate-code inventories, architecture boundary checks, OpenAPI/vocabulary
checks, no-sensitive-observability checks, and documentation-current-state tests should make it hard
for agents to ship code that degrades a Lotus app while satisfying the immediate prompt.

## Agentic Quality Feedback Loop

Use `context/playbooks/AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md` when repeated agent-authored
failures show that prose guidance is not enough. Treat CI failures, review comments, weak tests,
optimistic docs, stale wiki/context, missed closure evidence, duplicate implementations, and
architecture-boundary drift as candidate learning signals.

For each candidate signal:

1. ground it in a real Lotus PR, CI run, review finding, validation artifact, or defect,
2. decide the right control level: skill/context guidance, scaffold improvement, report-only
   inventory, regression-blocking gate, strict gate, or advisory evaluator case,
3. prefer deterministic repo-native gates for merge decisions and keep LLM graders advisory until
   datasets, graders, false-positive posture, and exception policy are proven,
4. update the platform-owned skill source under `lotus-platform/codex/skills` when the pattern
   changes how future agents should work,
5. sync local deployed skills through platform automation after source changes; do not hand-edit the
   local Codex profile as authoritative truth,
6. record the no-change decision when the finding is local to one slice and does not justify durable
   skill, context, scaffold, or gate changes.

Do not describe this as production reinforcement learning unless there is an implemented training
system. The Lotus control is a governed feedback loop: evidence becomes better gates, evaluator
cases, scorecards, scaffolds, skills, and context.

For newly scaffolded backend services, treat `make ci-contract-gate` as the default anti-drift gate.
It should remain blocking through `make lint` when it is worktree-clean and validates only concrete
lane wiring: required Makefile targets, approved workflow action majors, least-privilege workflow
permissions, 99% merge/releasability coverage, Docker validation, release evidence,
endpoint-certification, supported-feature, implementation-truth, security-audit,
architecture/OpenAPI gates, safe generated-artifact cleanup wiring, bounded job-level timeouts, and
no `continue-on-error: true` in critical lanes. Rebase auto-merge must use a non-`GITHUB_TOKEN`
merge actor such as
`LOTUS_AUTOMERGE_TOKEN`; otherwise GitHub suppresses the `pull_request_target.closed` event that
dispatches post-merge main releasability proof. The generated CI contract gate should enforce the
token reference, explicit missing-token warning-and-skip behavior, bounded workflow timeouts,
no-soft-fail critical workflow posture, implementation-truth guard presence, safe `make clean`
delegation to `scripts/clean_generated_artifacts.py`, scoped test-target variables
(`UNIT_TESTS`, `INTEGRATION_TESTS`, and `E2E_TESTS`) for repo-native focused validation, and the
merged-PR main-releasability dispatcher together. Missing `LOTUS_AUTOMERGE_TOKEN` must not create a
permanent red helper check; it should skip automatic rebase merge and require an authorized human or
release actor to merge.
GitHub workflows should call the repo-native targets that developers and agents run locally. For
generated backend services, Feature Lane should use `make test-unit`, PR/Main suite matrices should
use `make test-${{ matrix.suite }}-coverage`, and `make ci-contract-gate` should fail if an agent
reintroduces raw workflow-level `./.venv/bin/python -m pytest` commands or bypasses suite coverage
targets.

Generated endpoint-certification gates should require certified business/operator endpoints to cite
bounded operation-event test evidence in the endpoint ledger. Baseline health/metadata endpoints can
remain `baseline_certified` without operation-event evidence, but once an endpoint is marked
`certified`, API contract evidence and supportability telemetry proof must move together.

New backend scaffolds should also generate and run this seven-gate quality pack through
`make lint`: `make maintainability-gate`, `make documentation-contract-gate`,
`make quality-scorecard-gate`, `make monetary-float-guard`,
`make source-observability-contract-gate`, `make operation-metric-contract-gate`, and
`make implementation-truth-gate`.
The maintainability gate should block
oversized source, test, and script files/functions against conservative
thresholds calibrated above the initial scaffold baseline. The documentation
contract gate should scan required README, repository context, standards,
runbooks, quality, evidence, and wiki surfaces for presence, minimum substance,
required operating anchors, and placeholder erosion. The quality-scorecard gate
should scan the bank-buyable control matrix for required rows, approved readiness
statuses, non-empty evidence/gap/next-slice cells, implementation-backed evidence
anchors, and stale scaffold-era scorecard underclaims once certified business
endpoints exist. The monetary-float guard should be AST-backed and block
money-like `float` annotations, literals, return annotations, and conversions
while allowing non-monetary operational floats such as timeout seconds. The
source-observability contract gate should block raw
`print()`, direct Python logging, and low-level `log_event` bypasses in
`src/app` so generated and agent-authored feature code uses central
observability helpers and route-template request diagnostics. The operation metric contract gate
should block sensitive or unbounded operation metric names, labels, and attributes so future
business-operation telemetry starts source-safe before dashboards, alerts, or supported-feature
claims exist. The implementation-truth gate should scan current-state README, repository context, operations/demo docs,
quality docs, and wiki source for unqualified claims of demo readiness, production support,
certification, live source ingestion, Gateway/Workbench support, or client-ready publication before
supported-feature evidence exists. It should also block stale scaffold-era demo underclaims after
implementation and CI evidence prove a stronger current posture. Keep RFC target-state planning text
out of this blocking scan.
The generated architecture boundary gate should also protect `src/app/runtime`
as the process-local composition layer for repositories, adapters, publishers,
workers, and proof generators; runtime composition must not import API routes,
HTTP DTOs, FastAPI, or Starlette.
The generated cleanup utility should be tested and dependency-light: `make clean` should call
`python scripts/clean_generated_artifacts.py`, prune `.git`, `.venv`, and `node_modules`, and
remove only known local cache, build, and coverage artifacts. The generated CI contract gate should
fail if an agent replaces the utility with an inline Makefile command or deletes the script.
Generated test targets should be efficient without bypassing governance: `make test-unit`,
`make test-integration`, and `make test-e2e` should default to full suites while accepting
`UNIT_TESTS=<path>`, `INTEGRATION_TESTS=<path>`, and `E2E_TESTS=<path>` overrides. The CI contract
gate should fail if those scoped target variables, suite coverage targets, workflow Make calls, or
target commands are removed.

## Proof Artifact Enforcement

For cross-repository or runtime evidence work, prefer bounded proof artifacts over broad readiness
claims. A proof artifact should be treated as an enforceable contract, not as a narrative note.

When a repository adds or consumes evidence for downstream services, data mesh, AI, report/render/
archive, broker publication, Workbench/Gateway product surfaces, migrations, dashboards, alerts, or
runtime posture, require:

1. a schema version, proof type, proof scope, generated timestamp, owning repository, and source-safe
   evidence refs,
2. exact blocker codes cleared by the proof and exact blocker codes that intentionally remain,
3. explicit non-proof boundaries so a narrow proof cannot be promoted into unsupported product
   readiness,
4. a repo-native generator or validator command,
5. a blocking or intentionally report-only Make/NPM target with clear lane placement,
6. focused tests for valid payloads, invalid payloads, missing evidence, drift, and
   sensitive-content rejection,
7. README, operations docs, wiki source, supported-feature material, RFCs, and PR evidence updated
   only to the implementation-backed current truth.
8. a single-slice readiness statement that identifies whether this proof is enough to close the
   current slice or only clears one blocker for a later slice.

The anti-overclaim examples are deliberate and reusable:

1. route-foundation proof is not downstream execution proof,
2. report materialization proof is not client-publication proof,
3. data-mesh onboarding proof is not mesh certification,
4. AI workflow-pack registration proof is not live-provider proof,
5. Workbench read-path proof is not full product-surface certification.

If sibling evidence is optional for local developer ergonomics, a generator may write an invalid
non-proof artifact and exit cleanly only for absent evidence. Present but drifting sibling evidence
must fail so contract drift is not hidden.

Do not let proof gates encourage many half-finished slices. Prefer one narrow gate that proves and
closes a blocker completely, then merge that slice before adding the next proof family.

When a new proof gate is added for an RFC slice, require a slice closure manifest in the PR or RFC
ledger before promotion. The manifest should name the proof gate, blockers cleared, blockers
preserved, local command, GitHub lane, documentation/wiki/supported-feature decisions, and branch
cleanup evidence. This keeps enforcement work from becoming another source of partial, unmerged
truth.

For business-application RFC work, a proof gate should fail loudly when:

1. it clears a blocker that is not listed in the proof contract,
2. it removes a remaining blocker without a corresponding source-safe evidence reference,
3. it treats source-product proof as live-source proof,
4. it treats route, Gateway, Workbench, data-mesh onboarding, AI registration, or report
   materialization proof as client-publication or supported-feature proof,
5. it updates README, wiki, supported-features, RFC, or scorecard truth beyond the code and CI
   evidence merged in the same slice.

Live or canonical API exercises are valuable quality evidence, especially for cross-service output
review and refinement, but keep them in the appropriate higher lane. They complement deterministic
unit, contract, adapter, API, and readiness-gate tests; they do not replace those lower-pyramid
checks.

## Lens-Based Hardening Promotion

Use issue-discovery lens findings as raw signal for hardening, not as automatic CI requirements.
Promote only the lenses that repeatedly produce objective, deterministic, low-noise failures.

High-signal lens families for gates are:

1. `lens/architecture-boundaries`: import-direction, runtime-composition, and package-boundary
   checks.
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
    SBOM, pinned image, artifact signing, OCI image labels for Git SHA/branch/source/build
    timestamp, CI run ID capture, image digest capture, version/build metadata endpoint parity, and
    provenance checks.
14. AI lenses only when the app has an AI surface:
    `lens/ai-data-boundaries`, `lens/ai-evaluation-quality`, `lens/ai-safety-abuse-controls`,
    and `lens/ai-agent-tool-governance`.

For Docker/image provenance gates, prefer a single deterministic validator that checks the full
deployable-image chain before promoting the gate:

1. image tag includes the Git SHA,
2. OCI labels include commit, Git branch/ref, repository URL, version, build time, and CI
   pipeline/run ID,
3. release images are built and pushed by CI only,
4. image digest is captured in a release manifest,
5. SBOM is generated,
6. vulnerability scan passes or records an approved time-bounded exception,
7. image is signed,
8. provenance attestation is generated,
9. Kubernetes, Helm, or deployment manifests deploy by digest,
10. `/version` or version/build metadata endpoint exposes the same metadata, including the image
    digest once the image is published,
11. the same immutable image is promoted across environments, and
12. build secrets do not leak through Dockerfile `ARG`, Dockerfile `ENV`, image history, logs,
    labels, or runtime metadata.

The image validator should also check runtime asset closure for Compose-declared workers and
operator entrypoints. A manifest or helper script excluded by `.dockerignore`, omitted from a
Dockerfile `COPY`, or absent from the built image is a packaging defect even when local Python
tests pass. Require a built-image bounded entrypoint smoke (`--check-only` where supported) and a
focused pass/fail contract test for the declared file closure; keep this separate from OCI
provenance so packaging and provenance failures remain diagnosable.

Keep these lens families review-only until they have enough stable signal for automation:

1. `lens/product-workflow-usability`,
2. `lens/client-communication-suitability`,
3. `lens/customer-impact-failure-modes`,
4. `lens/localization-market-conventions`,
5. `lens/third-party-vendor-risk`,
6. broad `lens/dead-code-duplication` without import/runtime/test evidence.

These can still produce excellent GitHub issues, but blocking CI needs objective pass/fail rules,
known exceptions, and repo-native commands.

Before promoting a lens-derived gate, record:

1. the issue-discovery issue numbers and root causes that justify automation,
2. the proposed deterministic rule and why it is low-noise,
3. the repo-native command and intended CI lane,
4. pass/fail tests for the validator,
5. baseline posture and exception policy,
6. whether the gate blocks immediately or starts report-only,
7. scorecard, README/wiki, repo context, central context, and skill updates required by the new
   truth.

Use `lotus-app-issue-discovery` automation outputs as inputs, especially
`validate_issue_discovery_skill.py` for taxonomy consistency and
`plan_issue_discovery_campaign.py` for identifying high-signal hardening candidates by repository
profile. Do not gate on issue count; gate on repeated, measured defect classes.

## Context And Skill Maintenance

If a repeatable enforcement pattern emerges:

1. update the platform-owned skill source under `lotus-platform/codex/skills`,
2. update `codex/skills/lotus-skill-manifest.json` when adding, removing, or moving skills,
3. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing expectations change,
4. update central context or onboarding docs when agent workflow expectations change,
5. run platform bootstrap/validation automation to sync local skills and `AGENTS.md`,
6. preserve unknown local non-Lotus skills.

Before editing skills, context, or agent guidance, produce a short maintenance intake:

1. name the real failure pattern, PR, CI run, review finding, validation artifact, or user-reported
   documentation defect that justifies durable guidance,
2. identify whether the right durable control is a skill edit, routing-map edit, central context
   update, repo-local context update, scaffold/validator change, deterministic gate, advisory eval
   case, or explicit no-change decision,
3. prefer tightening the existing skill route before creating a new skill,
4. update `lotus-readme-wiki-governance` only when README/wiki professionalism, reader navigation,
   publication hygiene, or documentation presentation quality is the surfaced failure,
5. run skill alignment validation, focused routing/context tests, and bootstrap sync after source
   changes so deployed local skills are consumers of platform truth,
6. record whether repo-local wiki source changed or explicitly why no wiki update was needed.
7. when the user asks to "improve skills as needed", inspect the current failure pattern and the
   active Lotus routing map before editing. Prefer one or two precise skill changes at the point
   where future agents make the decision; do not create a new skill, update the manifest, or rewrite
   broad context unless routing, discoverability, or repeatability actually changed.
8. when a backend refactor exposes stale quality reports, weak wiki presentation, missing
   no-doc/no-wiki decisions, or incomplete PR evidence, update the backend delivery and
   README/wiki skills before adding another CI gate. Use gates for deterministic regression
   blockers; use skills for judgment-heavy workflow behavior that agents must remember.

When a quality signal changes repo organization, gate posture, or future-agent workflow, update
README, repo-local wiki source, `REPOSITORY-ENGINEERING-CONTEXT.md`, central context, and this skill
source in the same slice so the next agent starts from current truth.

Do not hand-edit local `C:\Users\<user>\.codex\skills` as the source of truth. Sync it from
`lotus-platform`.

When changing an existing Lotus skill, keep the change proportional to the repeated failure mode.
Tighten trigger descriptions, workflow steps, validation expectations, or reference routing before
creating a new skill. Create or split a skill only when the routing map shows a durable task family
that current skills cover too broadly or ambiguously.

For a skill-maintenance slice, do not treat edited Markdown as enough proof. Before PR closure,
record a skill maintenance proof pack:

1. touched skill names and why each one changed,
2. confirmation that `codex/skills/lotus-skill-manifest.json` was unchanged because no skill was
   added, moved, renamed, or removed, or the exact manifest change when it was,
3. `powershell -ExecutionPolicy Bypass -File automation/Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast -ValidateAfterSync`,
4. `python automation/validate_lotus_skill_alignment.py`,
5. source-to-deployed parity for each touched Lotus skill when the local profile will consume the
   new guidance in the same work session,
6. explicit no-wiki-change decision unless repo-local `wiki/` source changed,
7. any follow-up needed when a repeated failure should become a deterministic gate or evaluator
   case rather than more prose guidance.

If the bootstrap or alignment validation reports stale deployed skills, fix the sync issue before
claiming the skill improvement is usable by future agents.

## PR Evidence

For CI-enforcement PRs, include:

1. the measured baseline before promotion,
2. the new local command,
3. focused pass/fail tests for the gate,
4. aggregate local command output,
5. GitHub lane placement,
6. scorecard or ledger movement,
7. explicit no-wiki-change or wiki-publication decision,
8. stranded-truth reconciliation for workflow, context, or skill changes.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


