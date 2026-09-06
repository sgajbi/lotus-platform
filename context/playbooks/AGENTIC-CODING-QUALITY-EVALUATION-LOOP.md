# Agentic Coding Quality Evaluation Loop

Use this playbook when Lotus work needs stronger protection against low-quality agent-authored code,
weak tests, optimistic documentation, or CI gates that are easy to satisfy without improving
software quality.

This is not a claim that Lotus agents train themselves in production. It is a governed feedback
loop: failures from CI, review, runtime validation, and customer-relevant evidence become
repeatable eval cases, deterministic gates, scorecard controls, or skill/context improvements.

## Purpose

Agentic coding quality should be evaluated at three levels:

1. deterministic repository gates that block known bad patterns,
2. evaluator datasets that replay realistic agent tasks and grade outputs,
3. learning loops that convert repeated failures into standards, tests, scaffolds, skills, and
   context updates.

Use deterministic gates for merge decisions. Use AI or LLM-based evaluators as advisory signals
until their graders, datasets, false-positive posture, and exception policy are proven stable.

## Evaluation Sources

Build eval cases from real Lotus evidence:

1. PR review findings,
2. CI failures,
3. reverted or follow-up commits,
4. defects found by QA or demo certification,
5. stale docs, wiki, context, or skill drift,
6. repeated architecture-boundary, OpenAPI, vocabulary, security, observability, or test-quality
   regressions,
7. agent handoff summaries that missed required commands, branches, PR ids, or closure truth.

Each eval case should include:

1. repository and branch context,
2. task prompt or work intent,
3. allowed read/write scope,
4. expected invariant or failure mode,
5. grading rule,
6. required evidence,
7. examples of acceptable and unacceptable outcomes.

## Gate Promotion Ladder

Use this ladder before adding enforcement:

| Stage | Use | CI posture |
| --- | --- | --- |
| Eval dataset | Replays realistic agent tasks and grades output quality. | Advisory only. |
| Report-only inventory | Measures current repository posture. | Artifact or scorecard only. |
| Regression-blocking gate | Fails only when a stable baseline worsens. | Blocking in the narrowest useful lane. |
| Strict gate | Fails when the agreed enterprise target is not met. | Blocking in feature, PR, or main lane based on cost. |

Do not skip from an idea to a strict gate. First prove the signal is deterministic, useful, and
cheap enough for its lane.

## High-Value Enforcement Patterns

Prefer gates that catch common agent failure modes:

1. architecture-boundary drift,
2. duplicate implementation hotspots,
3. OpenAPI, API vocabulary, no-alias, and error-model drift,
4. missing or weakened API/runtime and contract/governance test-family breadth,
5. unchecked growth of uncategorized tests,
6. unsafe observability labels, raw logging, sensitive payloads, or trace leakage,
7. optimistic README, wiki, scorecard, or supported-feature claims,
8. deletion of repo-native Make/NPM targets or GitHub lane wiring,
9. missing SBOM, provenance, dependency, container, or release evidence where the repository
   already claims that posture.

Total test count alone is not a gate. A good agent can add tests that do not protect product
behavior. Gate stable proof families instead: API/runtime, contract/governance,
observability/security, methodology, migration/runtime, or product-surface evidence.

## Agent Workflow

For each meaningful agent-authored slice:

1. state the measured quality signal the slice will improve or preserve,
2. identify the deterministic local command that proves it,
3. add or update focused pass/fail tests for any new gate,
4. update scorecards, ledgers, docs, context, or skills when truth changes,
5. record explicit no-doc/no-wiki/no-context decisions when public truth did not change,
6. push the branch and let GitHub run heavy lanes,
7. turn repeated CI or review failures into future eval cases or gates.
8. sync platform-owned skill changes through the governed bootstrap or validation automation instead
   of editing deployed local skill copies as source truth.

Do not self-grade with prose such as "production-ready" or "enterprise-grade". Use executable
evidence and reviewable artifacts.

## Evidence And Guard Integrity

The compact rules in `AGENTS.md` come from observed failures:

1. shell heredocs interpreted backslash escapes and committed invisible control bytes into source
   and Markdown; use the editing/patch mechanism and scan bytes where this class is relevant,
2. pipelines ending in `tee` or `tail` returned the consumer's success instead of the gate's
   failure; run gates bare or explicitly preserve and propagate the producer status,
3. guards that were tested only on good input or one motivating defect passed while missing the
   broader class; test multiple bad shapes and valid counterexamples after every guard edit,
4. working-tree hashes gave false parity under line-ending normalization and uncommitted repairs;
   compare committed blob SHAs for synchronized canonical files,
5. `gh issue close --comment` can omit evidence when an issue is already closed; comment first and
   verify the durable record before changing issue state,
6. per-revision workflow dispatch can reject intermediate commits whose workflow differs from the
   default branch; keep workflow-changing PRs single-commit unless that repository proves otherwise.
7. a command may print a plausible count and still fail; record the exit status with reported
   output and treat non-zero results as partial evidence,
8. broad pattern matching can classify valid code-fence content or exact entity references as
   defects; inspect representative matches and valid counterexamples before mechanical rewriting,
9. a precise implementation of a false guard premise is still a false guard; verify the governing
   syntax, contract, or source behavior before hardening detection.

When a new case changes one of these rules, update this evidence section and its focused guard
tests. Keep only the mandatory outcome in `AGENTS.md`.

## Skill And Context Promotion

Promote a lesson into a skill or context update when it changes how future agents should approach a
task, not merely because one implementation was imperfect.

Use this decision order:

1. update an existing skill when the task route is already correct but the workflow, evidence, or
   validation expectations need sharper guidance,
2. update `LOTUS-SKILL-ROUTING-MAP.md` when agents could reasonably choose the wrong skill,
3. update central context or onboarding when the expectation applies across repositories,
4. update repo-local context when the lesson is specific to one app,
5. add a validator or CI gate when the pattern is deterministic and should block regression,
6. create a new skill only when a durable task family is too broad or ambiguous for the existing
   skill set.

Record a no-skill/no-context decision when the lesson is not repeatable. That record should be short
and attached to PR evidence, a scorecard, or a review ledger so future agents do not reopen the same
question without new facts.

## Modern Reference Points

Use current industry tooling as reference points, not as unreviewed Lotus policy:

1. OpenAI agent evaluation guidance uses traces, graders, datasets, and eval runs to improve agent
   workflow quality: <https://developers.openai.com/api/docs/guides/agent-evals>
2. OpenAI evaluation best practices emphasize structured evals because AI outputs are variable:
   <https://developers.openai.com/api/docs/guides/evaluation-best-practices>
3. OpenTelemetry provides vendor-neutral semantic conventions for traces, metrics, logs, profiles,
   and resources: <https://opentelemetry.io/docs/concepts/semantic-conventions/>
4. SLSA defines software supply-chain controls and provenance expectations:
   <https://slsa.dev/>
5. OWASP ASVS provides a basis for testing web application technical security controls:
   <https://owasp.org/www-project-application-security-verification-standard/>

If a referenced external tool changes or deprecates a capability, update Lotus guidance to preserve
the underlying control outcome rather than chasing a vendor-specific surface.

## Definition Of Done For New Agentic Quality Controls

A new agentic quality control is not complete until:

1. the failure mode is grounded in real Lotus evidence,
2. the local command is repo-native,
3. focused tests prove pass and fail behavior,
4. CI lane placement is documented,
5. scorecard or review-ledger truth is updated,
6. false-positive and exception policy are explicit,
7. wiki/context/skill update or no-change decision is recorded,
8. GitHub checks prove the gate in the intended lane.
