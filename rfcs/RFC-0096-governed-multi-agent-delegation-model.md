# RFC-0096: Governed Multi-Agent Delegation Model

- Status: Implemented
- Date: 2026-04-21
- Owners:
  - lotus-platform governance
  - Codex/agent operating-contract maintainers
- Target repositories:
  - `lotus-platform`
- Depends on:
  - `RFC-0093-lotus-context-assembly-and-compaction-hardening-for-agentic-development.md`
  - `RFC-0094-durable-background-engineering-task-ledger-and-governed-delegation-model.md`
  - `RFC-0095-heartbeat-driven-monitoring-and-attention-surfacing.md`

## Summary

Lotus should use parallel agent work only under explicit governance. This RFC defines bounded
delegation profiles, task ownership, read scopes, write scopes, evidence-return requirements,
review obligations, merge discipline, and failure semantics for multi-agent engineering work.

The goal is not to maximize parallelism. The goal is to make parallel work safe, auditable, and
useful without losing ownership, reverting unrelated changes, weakening review discipline, or
allowing delegated work to become hidden state after context compaction.

## Problem

Large Lotus RFCs often span multiple repositories, long-running CI, documentation, wiki
publication, and post-merge hygiene. Parallel agents can help with exploration, validation, review,
and bounded implementation slices, but unmanaged delegation creates risks:

1. overlapping writes,
2. unclear ownership,
3. stale or incomplete findings,
4. duplicate analysis,
5. unreviewed generated changes,
6. hidden task state after context compaction,
7. weak evidence when sub-work returns,
8. low-quality code accepted because a delegated worker produced it,
9. CI failures or PR comments monitored by multiple agents without one accountable owner.

RFC-0093 introduced governed context assembly and identifier preservation. RFC-0094 introduced
durable engineering task ledger foundations. RFC-0095 introduced advisory heartbeat attention
surfacing. This RFC turns those foundations into a practical operating model for bounded
multi-agent work.

## Goals

1. Define approved delegation profiles and disallowed delegation patterns.
2. Require explicit read and write scopes.
3. Require durable task identity and evidence refs for delegated work.
4. Define when delegation is allowed and when work must remain local.
5. Define a standard delegation prompt envelope and a standard return envelope.
6. Define how delegated task state maps into RFC-0094 task ledger semantics.
7. Define main-agent review and integration obligations after delegated work returns.
8. Integrate stale, lost, or blocked delegated task posture into RFC-0095 heartbeat evidence.
9. Add validation and context guidance so future agents follow the model.
10. Preserve human-readable review discipline after every delegated slice.

## Non-Goals

1. Creating unrestricted nested agent trees.
2. Allowing agents to edit overlapping write scopes without explicit ownership transfer.
3. Replacing code review with delegation output.
4. Delegating immediate blockers when the main task cannot progress without the result.
5. Creating a new hidden memory store for delegated work.
6. Allowing delegated workers to merge PRs, resolve review comments, publish wiki, or clean
   branches unless the main agent explicitly owns and reviews the final action.
7. Creating banker-facing product behavior.

## Current Reality

The implementation will build on existing platform truth:

| Surface | Current state | RFC-0096 implication |
| --- | --- | --- |
| AGENTS operating contract | Governs context loading, quality posture, wiki publication, and identifier preservation | Delegation rules must be added here only when implementation proves the exact durable wording |
| Context playbook | `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` already covers basic delegated-work fields | RFC-0096 should extend this playbook with profile, write-scope, review, and return-envelope rules |
| RFC-0094 task ledger | `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` governs task identity, lifecycle, cleanup, delegation, and evidence | Delegation should extend or reuse this contract rather than inventing parallel task identity |
| RFC-0095 heartbeat | Heartbeat can read local task ledger evidence and surface stale/lost work | Delegated task stale/lost/blocked posture should be exposed through heartbeat as derived evidence |
| Codex subagent mechanics | Runtime/tooling can spawn bounded agents, but platform governance cannot depend on hidden runtime state | Ledger, prompt envelope, evidence refs, and review notes must preserve source truth outside model memory |

## Design Principles

1. **One accountable owner.** The main agent owns the outcome, diff review, evidence, PR posture,
   merge readiness, wiki publication, and final answer.
2. **Parallelism only when it reduces risk or wall time.** Delegation is justified when work can
   proceed in parallel without blocking the main critical path.
3. **Explicit scopes before execution.** Every delegated task declares read scope and write scope.
   A no-write task must say so explicitly.
4. **Disjoint write scopes.** Parallel workers must not write the same files, directories, or
   contract families unless the main agent pauses one worker or records an explicit handoff.
5. **Evidence before confidence.** Delegated findings and changes must return command evidence,
   file refs, blockers, assumptions, and residual risks.
6. **Delegation output is not review.** Returned work must still be reviewed by the main agent
   before being committed, pushed, or used as closure evidence.
7. **Source truth remains external.** GitHub, task-ledger artifacts, repo files, validators, and
   tests remain source truth. Agent chat is not durable evidence.
8. **Lost delegated work is a finding.** A disappeared, timed-out, abandoned, or superseded
   delegated task must be visible in ledger and heartbeat posture.

## Delegation Profiles

| Profile | Purpose | Write permission | Typical evidence |
| --- | --- | --- | --- |
| `exploration` | answer a bounded codebase, docs, or history question | none | file refs, search terms, exact findings |
| `implementation` | implement a narrow slice in a declared module or file set | explicit write scope required | changed files, tests, diff summary |
| `validation` | run checks, inspect failures, summarize evidence | none unless explicitly approved | command, exit status, log refs |
| `review_support` | inspect a diff for risks, missing tests, stale docs, or simplification opportunities | none | findings with file refs and severity |
| `documentation` | update a bounded docs, RFC, wiki, context, or skill scope | explicit write scope required | changed docs, publication decision |
| `ci_triage` | inspect GitHub check failures or PR status without fixing code directly | none unless follow-up implementation is assigned | check name, run URL, failure summary |

Disallowed profiles:

1. `general_helper`,
2. `best_effort_worker`,
3. `do_everything`,
4. any profile without a bounded expected output,
5. any profile that allows broad repo-wide writes without a file or module ownership boundary.

## Delegation Eligibility Rules

Delegation is allowed when all of the following are true:

1. the delegated task is concrete, bounded, and self-contained,
2. the main agent has a useful non-overlapping next action,
3. the next main-agent action is not blocked by the delegated answer,
4. write scopes are disjoint or the delegated task is no-write,
5. output can be reviewed through files, commands, and evidence refs,
6. failure or non-return can be represented in the task ledger without losing state.

Delegation is not allowed when any of the following are true:

1. the task is the immediate blocker on the critical path,
2. the main agent cannot review the output,
3. the write scope overlaps another active worker,
4. the subtask requires hidden credentials or mutable state not recorded in evidence,
5. the output would be accepted without test, diff, or evidence review,
6. the delegated task would create nested unmanaged delegation.

## Required Delegation Input Envelope

Every delegated task must include these fields, either as a machine-readable ledger record or a
plain-text prompt that maps one-to-one to the same fields:

| Field | Requirement |
| --- | --- |
| `delegation_task_id` | Stable id or ledger id when the task is recorded before launch |
| `parent_task_id` | Main task or RFC slice id when available |
| `profile` | One governed profile from this RFC |
| `repository` | Exact repo name |
| `branch` | Exact branch name |
| `problem_statement` | What to solve or inspect |
| `expected_output` | Concrete return shape |
| `read_scope` | Files, directories, commands, PRs, or docs the worker may inspect |
| `write_scope` | Files/modules the worker may edit, or `none` |
| `forbidden_actions` | At minimum: no unrelated reverts, no broad cleanup, no PR merge, no wiki publish |
| `evidence_requirements` | Commands, file refs, logs, screenshots, or GitHub check URLs expected |
| `coordination_notes` | Active sibling workers, claimed files, or handoff boundaries |
| `return_envelope` | Required output fields listed below |

## Required Delegation Output Envelope

Delegated work must return:

1. outcome summary,
2. files changed, if any,
3. tests or checks run,
4. evidence refs,
5. blockers or assumptions,
6. remaining risks,
7. follow-up required or `none`,
8. confirmation that unrelated work was not reverted,
9. for implementation work, a concise patch summary grouped by owned write scope.

## Task Ledger Integration

Delegated tasks must map into RFC-0094-compatible lifecycle semantics.

| Delegated posture | Ledger status | Required treatment |
| --- | --- | --- |
| queued but not started | `QUEUED` | Visible but not evidence of progress |
| actively running | `RUNNING` | Main agent may proceed only on non-overlapping work |
| completed and reviewed | `SUCCEEDED` | May support closure evidence after main-agent review |
| returned failure | `FAILED` | Requires fix-forward, abandonment, or explicit supersession |
| exceeded timeout | `TIMED_OUT` | Must not be treated as success |
| intentionally stopped | `CANCELLED` | Record reason and replacement plan, if any |
| process disappeared or result missing | `LOST` | Operational finding; heartbeat should surface it |
| replaced by a newer task | `SUPERSEDED` | Preserve old evidence and link replacement task |

The implementation should reuse the existing task-ledger contract where possible. It should add
delegation-specific fields only when they improve source-truth preservation, for example:

1. `delegation_profile`,
2. `parent_engineering_task_id`,
3. `read_scope`,
4. `write_scope`,
5. `coordination_notes`,
6. `return_envelope_received`,
7. `main_agent_review_status`.

## Conflict And Integration Rules

1. A delegated implementation result must not be committed until the main agent reviews the diff.
2. The main agent must check for overlapping edits before integration.
3. If a delegated worker changes files outside its write scope, those changes must be rejected or
   explicitly reclassified in the review note.
4. If two workers produce conflicting changes, the main agent must choose one integration path and
   mark the other `SUPERSEDED` or `CANCELLED`.
5. Delegated tests are evidence, not sufficient proof. The main agent must run focused local checks
   after integration and use GitHub checks before merge.
6. Delegated documentation or wiki changes still require the normal wiki publication decision.

## Heartbeat Integration

RFC-0095 heartbeat should read delegated task truth from RFC-0094 task-ledger artifacts, not from
agent chat. The first implementation should add heartbeat attention only for explicit evidence:

1. stale `RUNNING` or `QUEUED` delegated tasks beyond configured thresholds,
2. `FAILED`, `TIMED_OUT`, or `LOST` delegated tasks,
3. delegated implementation output missing required evidence,
4. overlapping active write scopes,
5. unresolved blockers after a delegated task returns.

Heartbeat attention items must preserve:

1. `engineering_task_id`,
2. `parent_engineering_task_id`,
3. repository,
4. branch,
5. delegation profile,
6. source artifact path,
7. affected write scope when present.

Heartbeat must not:

1. redefine task status,
2. inspect hidden model state,
3. treat missing ledger evidence as healthy,
4. raise alerts for `SUCCEEDED`, `CANCELLED`, or `SUPERSEDED` tasks when closure evidence is
   complete and no active replacement is stale.

## Machine-Readable Contract Boundary

RFC-0096 implementation should prefer one of these approaches, in order:

1. extend `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` with
   delegation-profile and scope fields if the existing contract is close enough,
2. add a small companion delegation policy contract under `platform-contracts/agent-engineering/`
   if profile vocabulary and prompt/return envelopes need separate validation,
3. avoid a separate contract only if executable tests can prove the same requirements through the
   existing RFC-0094 contract.

If a companion contract is introduced, it must include:

1. governed profile vocabulary,
2. required input envelope fields,
3. required output envelope fields,
4. write-scope and no-write rules,
5. disallowed profile names,
6. lifecycle mapping to RFC-0094 statuses,
7. source-truth and review obligations.

## Implementation Plan

### Slice 1: Delegation Policy Contract

1. Extend the RFC-0094 task-ledger contract or add a companion platform contract for delegation
   profiles and envelopes.
2. Define governed profile vocabulary, disallowed profiles, required input fields, and required
   return fields.
3. Add validator and focused tests for valid and invalid delegation records.
4. Add examples for no-write exploration, implementation with write scope, validation-only work,
   review support, and rejected broad delegation.

Review gate:

1. ensure profile names are bounded,
2. ensure write-scope rules are explicit,
3. avoid duplicating RFC-0094 task identity fields,
4. prove invalid broad or no-scope delegation is rejected,
5. confirm contract examples preserve repository, branch, task id, and evidence refs exactly.

### Slice 2: Agent Operating Guidance

1. Update AGENTS operating contract if durable delegation wording changes.
2. Update `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md`.
3. Update `context/LOTUS-SKILL-ROUTING-MAP.md` if routing expectations change.
4. Add examples of good delegation prompts and bad delegation prompts.

Review gate:

1. confirm guidance discourages delegation of immediate blockers,
2. confirm subagent output is evidence-bearing,
3. confirm no new agent mode conflicts with Codex runtime instructions,
4. confirm future agents can tell when to keep work local,
5. confirm guidance preserves exact identifiers through compaction and handoff.

### Slice 3: Task Ledger Integration

1. Record delegated tasks through RFC-0094-compatible task fields.
2. Define how delegated task status maps to main task status.
3. Add support for superseded, cancelled, lost, and abandoned delegated tasks.
4. Add tests for terminal status transitions and replacement links.

Review gate:

1. verify GitHub truth and local automation truth are not redefined,
2. verify `LOST` delegated work is visible and not treated as success,
3. verify superseded tasks preserve replacement lineage,
4. verify no hidden model-memory state is required to reconstruct delegated task posture.

### Slice 4: Review And Merge Discipline

1. Define the main-agent review obligations after delegated code changes.
2. Require conflict checks before accepting delegated edits.
3. Require focused tests after integration.
4. Add docs for rejecting low-quality delegated output.
5. Define what evidence is required before delegated work can support PR closure.

Review gate:

1. confirm the model preserves one accountable owner,
2. confirm delegated changes cannot bypass PR checks,
3. confirm evidence hierarchy is preserved,
4. confirm write-scope violations are rejected or explicitly reclassified,
5. confirm no broad monolith-splitting or cleanup can be delegated without a bounded slice.

### Slice 5: Heartbeat Integration

1. Feed stale delegated task posture into RFC-0095 heartbeat attention items.
2. Surface missing evidence, stale running state, unresolved blockers, overlapping active write
   scopes, and lost delegated tasks.
3. Add tests using synthetic ledger records.
4. Keep heartbeat advisory and derived from task-ledger artifacts.

Review gate:

1. ensure heartbeat reads task truth without redefining it,
2. ensure duplicate stale-task alerts are deduplicated,
3. ensure no alert is raised for intentionally closed tasks with complete closure evidence,
4. ensure attention items preserve `engineering_task_id`, branch, repository, profile, and write
   scope.

### Slice 6: Code Review, API Certification, And Governance Tightening

Second-last mandatory slice.

1. Review delegation contracts, docs, context, examples, validators, and tests for duplication.
2. Confirm machine-readable artifacts follow the certification pattern.
3. Confirm OpenAPI is not applicable unless a served API endpoint was introduced.
4. Confirm vocabulary, contract, platform governance, and migration impact are covered by tests or
   explicitly not applicable.
5. Confirm no dead or stale agent guidance remains.
6. Tighten examples to repo-native Lotus workflows.
7. Decide whether generated delegation/ledger evidence should become PR-blocking or remain
   advisory, and record the decision explicitly.

Review gate:

1. prove platform repo checks cover the contract and validator,
2. prove malformed delegation records fail validation,
3. confirm no delegated work path can bypass main-agent review,
4. record any follow-up that is outside RFC-0096 rather than silently expanding scope.

### Slice 7: Documentation, Context, Wiki, Skills, And Branch Hygiene

Final mandatory slice.

1. Update documentation and central agent context.
2. Update wiki source if operator or agent-facing behavior changed enough for publication.
3. Assess whether a new skill is needed or existing skills should be tightened.
4. Update deployed local skill copies if tracked skill guidance changes and the repo convention
   requires synchronization.
5. Run wiki sync checks before merge and publish after merge if wiki changed.
6. Record final evidence, PR checks, merge decision, and branch cleanup.

Required final-slice decisions:

1. `AGENTS.md`: update, no change, or defer with rationale.
2. `context/`: update, no change, or defer with rationale.
3. `wiki/`: update and publish, or record no-wiki-change rationale.
4. skills/guidance: update existing skill, add new skill, remove stale guidance, or record
   no-change rationale.
5. branch hygiene: record local clean state, remote branch cleanup, and generated artifact posture.

## Test Plan

Minimum implementation proof:

1. contract tests for valid and invalid delegation profiles,
2. validator tests for missing write scope, broad write scope, unknown profile, and missing return
   envelope,
3. task-ledger tests for delegated status mapping, `LOST`, `SUPERSEDED`, `CANCELLED`, and
   replacement links,
4. heartbeat tests for stale delegated work, lost delegated work, overlapping write scopes, and
   closed-task non-alert behavior,
5. docs/context tests proving future agents see the delegation model,
6. RFC closure governance tests proving second-last and final slices remain present,
7. repo-native feature-lane proof before PR,
8. GitHub PR check proof before merge.

## Acceptance Criteria

1. Delegation profiles are machine-readable or validator-protected.
2. Delegation input and output envelopes are explicit and test-protected.
3. AGENTS/context guidance tells future agents when and how to delegate.
4. Delegated code changes require explicit write scope and main-agent review.
5. Stale, failed, lost, cancelled, and superseded delegated tasks have clear status semantics.
6. Heartbeat integration can surface stale, lost, or blocked delegated work from task-ledger
   artifacts.
7. Final docs/context/wiki/skills/branch hygiene is complete.
8. API certification posture is explicit: artifact contracts are certified; OpenAPI is only
   applicable if an HTTP endpoint is introduced.
9. The implementation records a conscious decision about whether delegation/heartbeat evidence
   remains advisory or becomes gate-affecting.

## Implementation Boundaries

The implementation must not:

1. create unrestricted nested delegation,
2. require hidden model memory to reconstruct work state,
3. let delegated workers merge PRs or publish wiki without main-agent review,
4. treat delegated findings as sufficient review,
5. mutate GitHub state from heartbeat,
6. introduce a served API without endpoint certification,
7. broaden into banker-facing UX or workflow-pack runtime orchestration.

## Open Implementation Decisions

These decisions must be resolved before implementation closure:

1. whether to extend the RFC-0094 task-ledger contract or add a companion delegation policy
   contract,
2. whether local background-run automation should create delegated task records directly or expose a
   separate command wrapper,
3. whether stale delegated task heartbeat findings stay advisory-only or become part of a PR gate,
4. whether `platform-automation-ops` is sufficient skill guidance or a new delegation-specific skill
   is justified,
5. which default stale thresholds apply to delegated work.

## Resolved Implementation Decisions

Resolved on 2026-04-21:

1. A companion delegation policy contract was added at
   `platform-contracts/agent-engineering/delegation-policy-contract.v1.json`. The RFC-0094 task
   ledger contract remains the lifecycle source, while the RFC-0096 policy contract owns profile,
   envelope, write-scope, review, and heartbeat-attention vocabulary.
2. Delegated task records are created and reviewed through
   `automation/delegation_task_ledger.py`. The helper is intentionally separate from background-run
   launch automation so delegated work can be recorded without coupling every runner to subagent
   mechanics.
3. Stale delegated task heartbeat findings are advisory in this implementation. The contracts and
   validators are PR-checkable, but generated delegated-task posture should not block merges until
   signal quality is proven over real usage.
4. `platform-automation-ops` is sufficient skill guidance for this slice. A dedicated delegation
   skill is not justified yet because the durable rules now live in AGENTS, the context playbook,
   the routing map, and machine-readable contracts.
5. The default stale delegated-task threshold is six hours when the `delegated_task_ledger` heartbeat
   source is explicitly enabled.

## Implementation Status And Evidence

Implemented on 2026-04-21 in `lotus-platform`.

Delivered implementation:

1. delegation policy contract and governed examples,
2. contract validator coverage for profiles, input envelopes, output envelopes, write scope,
   disallowed broad delegation, lifecycle mapping, review statuses, and heartbeat identifiers,
3. RFC-0094-compatible delegated task ledger helper for create, status update, return recording,
   and main-agent review,
4. explicit handling for `LOST`, `FAILED`, `TIMED_OUT`, `CANCELLED`, and `SUPERSEDED` delegated
   task posture,
5. write-scope enforcement for returned implementation/documentation output,
6. parseable RFC-3339 UTC timestamp validation for delegated task lifecycle and review timestamps,
7. optional RFC-0095 heartbeat source adapter for stale, failed, lost, missing-evidence,
   unresolved-review, and overlapping-write-scope delegated task attention,
8. AGENTS, central context, playbook, skill-routing, and `platform-automation-ops` guidance updates,
9. docs and wiki source updates for operator and future-agent discovery,
10. slice-by-slice review artifacts and final closure evidence in
    `rfcs/RFC-0096-final-closure-evidence.md`.

API certification posture:

1. OpenAPI certification is not applicable because RFC-0096 introduced no served HTTP endpoint.
2. Artifact certification is applicable and covered by
   `automation/validate_agent_engineering_contracts.py`,
   `automation/validate_heartbeat_contracts.py`, focused unit tests, and platform repo checks.
3. If delegated task posture is later exposed through a service API, that endpoint must go through
   the Lotus endpoint certification pattern before being treated as product or operator API truth.

## Pre-Implementation Gold-Standard Review

Reviewed on 2026-04-21 before implementation begins.

Tightening applied:

1. added explicit current-reality mapping to RFC-0093, RFC-0094, and RFC-0095,
2. added design principles for accountable ownership, disjoint write scopes, evidence hierarchy,
   and lost-task visibility,
3. expanded delegation profiles and added disallowed profile names,
4. added delegation eligibility rules,
5. added required input and output envelopes,
6. added task-ledger status mapping and delegation-specific candidate fields,
7. added conflict and integration rules,
8. tightened heartbeat integration to read task-ledger truth rather than agent chat,
9. added a machine-readable contract boundary and certification expectations,
10. expanded implementation slices with review gates,
11. added implementation boundaries and open decisions,
12. added required final-slice decisions for documentation, context, wiki, skills, and branch
    hygiene.

Documentation, context, wiki, and skills decision for this pre-implementation pass:

1. RFC document: updated because implementation requirements were too implicit.
2. Repo RFC index and wiki index: no status change yet; RFC remains draft and already appears in
   the implementation order.
3. Central agent context: no change yet because behavior is not implemented.
4. Skills: no change yet because delegation guidance should be updated with the implementation
   slice that changes durable agent behavior.
5. Wiki: no publication required for this tightening because operator-facing behavior did not
   change.

## Initial Priority

Implement second. Heartbeat monitoring should land first so delegated tasks can be observed.
