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
9. the blocking command does not create or rewrite durable report artifacts in a clean checkout,
10. quantitative PR claims can be reproduced from named commands, base/head refs, or committed
    evidence artifacts where practical,
11. the gate satisfies the Gate Liveness Standard below - reachable from a blocking lane, capable of
    returning non-zero, fail-closed on empty input, observed to have run, and ordered before the
    irreversible act it governs. Promotion is not complete until the gate has failed once on
    purpose.

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

## Threshold Discipline

A **ratchet** (a bound banked from a measurement) belongs at exact equality with zero headroom; a
**band** (a ratio between a floor and a ceiling) must never sit on its edge. Opposite disciplines,
and easy to apply backwards. Re-bank an improvement in the direction that tightens - a ceiling
down, a floor up. An evidenced classifier correction follows the corrected measurement even when
that moves a bound outward; require a regression test, before/after count, and a stable underlying population; classifier proof may change. A
**fixed policy threshold** such as an SLO or coverage target is neither and is never re-banked to
the measurement. When a correctly-banked threshold blocks legitimate work, suspect the
**classifier**, not the bound: the gate is measuring the wrong population and is punishing the
behaviour it exists to encourage. Load `references/threshold-discipline.md` for the instances.

Keep report-only until stable when the signal is noisy or policy is not settled, such as:

1. maintainability index,
2. broad dead-code scans with framework false positives,
3. public docstring percentage,
4. branch coverage before measurement is configured,
5. dependency hygiene with unresolved runtime-only declarations.

## Gate Liveness Standard

Promotion decides *whether a signal deserves a gate*; it does not establish that one which exists is
alive - reachable, able to return non-zero, fail-closed on empty input, observed to have run, and
ordered before the irreversible act it governs. The first four are indistinguishable from a passing
gate; the fifth fails after the artifact ships. See `references/gate-liveness-standard.md`; audit
with `python automation/gate_liveness_audit.py`.

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

## Dependency And Container Vulnerability Posture

When reviewing or designing dependency, SCA, SBOM, or container-image gates, load
`references/dependency-container-vulnerability-posture.md`. It owns the detailed Lotus technology
maturity default, vulnerability evidence expectations, exception fields, and report-only to
blocking promotion criteria.

Keep skill-specific automation with this skill. If this posture later needs a reusable scanner
inventory, exception-schema check, or gate-readiness helper that is not a general platform
validator, place it under `codex/skills/lotus-ci-enforcement-governance/scripts/` and reference the
script from the posture reference instead of adding more repo-root one-off automation.

## Final-Head Quantitative Evidence

Before treating scorecards, diff-stat movement, line-count reductions, coverage deltas, or other
quantitative PR claims as closure truth, remeasure them against the final PR head and current base
after the last rebase, force-push, prerequisite merge, or scope correction.

PR evidence should name the reproducible command, base/head refs, and generated artifact or exact
output used for the final measurement where practical. Earlier branch measurements may remain as
historical notes, but they must not be presented as final closure truth after branch scope or base
state changes.

Keep arbitrary prose parsing report-only unless the repository has a structured contract that makes
the check deterministic and low-noise. Prefer contract tests, scorecard validators, or template
assertions for governed evidence surfaces instead of attempting to block merges by parsing every
human-authored number in free-form text.

## Deterministic Node Quality Tooling

When a blocking quality gate uses a Node-based tool, load
`references/deterministic-node-quality-tooling.md`. It owns the lock-backed package contract,
forbidden mutable-resolution patterns, validation command, and the rule that Node tooling should not
be added to Python-only service scaffolds without a real Node-based blocking gate.

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
9. tenant-aware source adapters that drop trusted tenant context, accept ambiguous tenant scope, or
   reintroduce hard-coded production fallback tenants; enforce the complete API-to-port-to-adapter
   path and cover batch/worker entrypoints where they share the adapter.
10. shared API dependencies whose governed `ProblemDetails` codes are collapsed by global exception
    handlers into one generic response; keep a generic fallback for unknown framework failures but
    statically guard typed product-safe boundary errors and verify runtime/OpenAPI parity.
11. dead-letter implementations that provide terminal storage without governed recovery; require a
    blocking contract gate for source-safe inspection fields, dedicated authorization and trusted
    provenance, idempotent audit-plus-lease fencing, event/schema eligibility, preserved failure
    history, bounded poison recovery, non-mutating replay/conflict, and durable restart evidence.
12. coupled lifecycle/posture, status/phase, or state/eligibility fields that can form contradictory
    combinations; require a blocking contract gate that protects one versioned domain matrix across
    construction, rehydration, transition/mutation guards, durable constraints, queue/readiness
    quarantine, stable API errors, source-safe telemetry, legacy reconciliation, exhaustive pair
    tests, and repeated-action behavior.
13. executable files named after RFCs, slices, issues, PRs, or temporary delivery phases instead of
    the capability or invariant they implement; exempt only true governance/tracking artifacts.
14. feature-package migrations that leave both old flat modules and new package paths active,
    strand tests in unrelated directories, or rely on fixed `Path.parents[n]` depth after moving
    tests; protect proven canonical paths and reject obsolete paths.
15. source-backed proof gates coupled to comments or incidental implementation literals; after a
    refactor, require stable symbol/interface or behavioral evidence plus tamper and missing-source
    tests rather than weakening the proof.
16. changed-code or critical-path coverage gates that hard-code one source root even though the
    governed contract includes migrations, generated schemas, or other Python trees; derive
    eligibility from contract globs, map each eligible path to a measurable coverage source, and
    narrow report evidence back to the exact changed path with non-default-root regression tests.

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

When changing generated backend service scaffolds, generated Makefiles, generated GitHub workflows,
generated endpoint-certification gates, generated cleanup utilities, or scaffold quality packs,
load `references/generated-service-quality-gates.md`. It owns the detailed generated-service
contracts for `make ci-contract-gate`, endpoint example parity, the seven-gate quality pack,
runtime composition boundaries, safe cleanup, and suite target overrides. Endpoint example parity
automation stays with this skill at `scripts/endpoint_example_parity.py`.

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
9. executable reconciliation between any proof registry classification/effect and each application
   consumer, with unknown, duplicate, pending, and wrong-effect wiring rejected before blocker
   mutation.

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

Use `references/lens-hardening-promotion.md` for the governed lens families, Docker provenance
requirements (including Git branch/ref, repository URL, pipeline/run ID, image digest, SBOM,
vulnerability scan, image is signed, provenance attestation, deploy by digest, `/version`, and the
same immutable image, with no secrets in Dockerfile `ARG` or Dockerfile `ENV`), review-only boundaries, and
promotion intake.
Treat issue-discovery output as signal, not an automatic CI requirement; promote only objective,
deterministic, low-noise rules and never gate on issue count.

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
8. stranded-truth reconciliation for workflow, context, or skill changes,
9. final-head quantitative evidence for scorecard, diff-stat, line-count, coverage, or other
   numeric claims, including the command, final PR head/current base refs, and artifact where
   practical.
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


