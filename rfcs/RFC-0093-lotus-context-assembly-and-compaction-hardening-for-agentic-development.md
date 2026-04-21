# RFC-0093: Lotus Context Assembly and Compaction Hardening for Agentic Development

- Status: Implemented
- Date: 2026-04-18
- Owners:
  - lotus-platform governance
- Requires Approval From:
  - lotus-platform maintainers
  - maintainers of Lotus repositories whose context or skill guidance is updated under this RFC
- Related:
  - `RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
  - `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`
  - `RFC-0074-repeatable-developer-and-agent-bootstrap-system.md`
  - `RFC-0080-lotus-agent-runtime-demo-skill-pack-and-guidance-hardening.md`
  - `RFC-0081-slice-9-ai-surface-governance-and-assistive-workflow-controls-evidence.md`
  - `../../lotus-ai/docs/rfcs/RFC-0031-governed-agent-workflow-packs-and-bounded-ai-runtime.md`
  - `../../lotus-ai/docs/rfcs/RFC-0032-governed-workflow-pack-registry-and-activation-posture.md`
  - `../../lotus-ai/docs/rfcs/RFC-0033-durable-ai-run-ledger-and-review-state-contracts.md`

## Summary

RFC-0073 created the Lotus engineering context system.

RFC-0074 made onboarding and bootstrap repeatable.

RFC-0080 hardened skill routing and asynchronous operating posture.

Those RFCs improved how a Lotus agent begins work, but they do not yet define how long-running
agent sessions should:

1. assemble the right context for the current task,
2. preserve important identifiers and decisions when sessions compact,
3. capture durable notes before context is lost,
4. distinguish ephemeral conversation history from governed durable memory,
5. stay effective across multi-day, multi-branch, multi-repository delivery loops.

This RFC defines the next platform layer:

1. a governed Lotus context-assembly model for agentic development,
2. a governed compaction policy that preserves engineering-critical identifiers and decisions,
3. a bounded durable note-capture posture before compaction or context transitions,
4. skill, context, and validation updates so the system is enforced rather than aspirational.

The goal is to make Codex and future Lotus agent workflows materially more reliable in long-running
engineering sessions without treating prior chat history as trusted durable memory.

## Why This RFC Exists

Lotus has already invested in:

1. governed central context,
2. repeatable bootstrap,
3. skill routing,
4. asynchronous PR and CI posture,
5. durable documentation and repository-local engineering truth.

But there is still a practical reliability gap in agentic development.

Long sessions can still degrade because:

1. too much low-value history is carried forward,
2. the wrong context is assembled for the active task,
3. important identifiers are paraphrased away during summarization,
4. branch, PR, issue, RFC, endpoint, test, and file-path references get blurred,
5. durable insights remain trapped in transient chat rather than promoted into governed artifacts.

This is not merely a convenience problem.

For Lotus, it directly affects:

1. delivery accuracy,
2. traceability,
3. fix-forward speed,
4. auditability of engineering reasoning,
5. consistency of multi-day agent-driven work.

OpenClaw is useful here as a reference, not a dependency.

Its context-engine, compaction, and note-preservation ideas show the value of:

1. explicit context assembly,
2. explicit compaction behavior,
3. identifier-preserving summarization,
4. bounded pre-compaction memory capture.

Lotus should selectively translate those ideas into its own standards and operating model.

## Problem

Today Lotus has strong startup context, but weaker long-session context discipline.

Common failure modes include:

1. excessive context loading at the start of a task,
2. stale or irrelevant context lingering after task intent changes,
3. compaction summaries that preserve general themes but lose exact engineering identifiers,
4. agent-discovered reusable lessons staying inside chat instead of becoming:
   - docs,
   - context updates,
   - skills,
   - procedural memory,
   - validators,
5. context transitions that do not clearly distinguish between:
   - ephemeral working memory,
   - durable engineering truth,
   - repo-local truth,
   - platform-wide truth.

The result is that the existing context system can still underperform during:

1. long PR loops,
2. asynchronous fix-forward work,
3. multi-repository implementation programs,
4. RFC-driven execution carried across multiple days,
5. large validation and QA cycles.

Lotus needs a deliberate context-assembly and compaction policy, not just better initial reading
order.

## Goals

1. Define a governed context-assembly model for Lotus agentic development.
2. Define a compaction policy that preserves engineering-critical identifiers and decisions.
3. Introduce bounded durable note capture before compaction or context loss.
4. Distinguish clearly between ephemeral session memory and durable governed memory.
5. Improve long-running agent reliability across PR, CI, QA, and cross-repo workflows.
6. Align skills, AGENTS guidance, onboarding docs, and context validators with the new model.

## Non-Goals

1. Building a general plugin-based context-engine marketplace.
2. Replacing RFC-0073 context architecture with a second documentation system.
3. Treating chat transcripts as authoritative engineering records.
4. Storing arbitrary conversational memory without governance.
5. Replacing repository truth with platform-owned summaries.
6. Turning every session insight into a permanent artifact automatically without review.

## Scope Boundary

This RFC governs:

1. context assembly for Lotus agentic development tasks,
2. context compaction policy,
3. identifier-preservation requirements,
4. bounded note-capture and promotion rules,
5. required updates to skills, context docs, onboarding, and validation where this posture changes
   platform truth.

This RFC does not govern:

1. product-facing AI workflow runtime state,
2. business-domain knowledge management,
3. arbitrary personal memory features,
4. repository-local implementation documentation beyond how it is consumed and promoted by the
   context system.

## Decision

Lotus will adopt a governed context-assembly and compaction hardening model for agentic development.

Specifically:

1. context assembly must be task-scoped and layered rather than conversation-wide by default,
2. compaction must preserve engineering-critical identifiers and decision lineage,
3. important transient insights must be promoted into durable governed artifacts before context is
   lost,
4. skills, AGENTS guidance, onboarding docs, and validation rules must reinforce this model,
5. OpenClaw-like ideas may inform the pattern, but implementation remains Lotus-native and governed.

## Implementation Status

Current status: **Implemented on `main` via PR `#163`**.

The first implementation slice adds the shared agent-engineering contract foundation used by
RFC-0093 and RFC-0094:

1. `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json`,
2. `automation/validate_agent_engineering_contracts.py`,
3. `tests/unit/test_agent_engineering_contracts.py`.

That contract establishes RFC-0093's identifier-preservation, decision-state, and promotion-target
requirements in machine-readable form. The context adoption slice adds a governed agent context and
task-ledger playbook plus context-system validation. The automation adoption slice makes detached
background-run state preserve task identity and evidence references for resumed sessions. The
targeted skill slice aligns `platform-automation-ops` with the new contract. The final slice updates
AGENTS guidance, wiki source, final closure evidence, and branch/PR hygiene.

No implementation slice may mark RFC-0093 as fully implemented until the platform can point to:

1. concrete context, AGENTS, onboarding, skill, or validator changes,
2. tests or contract checks for any executable governance that was added,
3. explicit review evidence for the second-last tightening slice,
4. final documentation, context, wiki, skills/guidance, and branch-hygiene evidence.

The RFC may remain valuable as approved design before all automation exists, but implementation
status must stay truthful and must not imply that compaction behavior is enforced before it is
actually enforced by docs, skills, validators, or operating contracts.

## Design Principles

### 1. Assemble only the smallest correct working set

Agents should load:

1. mandatory platform truth,
2. target repository truth,
3. task-relevant standards and RFCs,
4. only the extra context actually required for the current slice.

They should not carry broad context by default once it is no longer relevant.

### 2. Durable truth and ephemeral working memory are different things

Conversation history can help reasoning.

It is not a substitute for:

1. docs,
2. context artifacts,
3. RFCs,
4. wiki pages,
5. skills,
6. validators,
7. repository truth.

### 3. Identifier loss is a correctness bug

When a session compacts, these must remain exact where they matter:

1. RFC ids,
2. issue ids,
3. PR numbers,
4. branch names,
5. endpoint names,
6. file paths,
7. command names,
8. portfolio ids,
9. test names,
10. contract names,
11. task status labels,
12. repository names.

### 4. Promotion is better than recollection

Important reusable engineering knowledge should be promoted into durable artifacts rather than
hoping the next session reconstructs it from summaries.

### 5. Compaction should preserve decision lineage, not just topic summary

The point is not simply "what the conversation was about."

The point is also:

1. what was decided,
2. what was ruled out,
3. what evidence supported the decision,
4. what remained open.

## Lotus Context Assembly Model

The Lotus context-assembly model should be treated as a governed platform contract.

### Context layers

The working set should be assembled from the following layers.

1. **Operating contract**
   `AGENTS.md` and equivalent operating instructions.
2. **Central platform context**
   `LOTUS-QUICKSTART-CONTEXT.md`, `LOTUS-ENGINEERING-CONTEXT.md`, `CONTEXT-REFERENCE-MAP.md`.
3. **Repository-local truth**
   `REPOSITORY-ENGINEERING-CONTEXT.md` and repo-owned docs.
4. **Task-local authority**
   RFCs, standards, runbooks, tests, contracts, failing-check evidence, PR context.
5. **Session-local working memory**
   the current active plan, recent observations, and current unresolved blockers.

### Assembly rule

The agent should always prefer:

1. central platform truth for platform-wide rules,
2. repository-local truth for repository behavior,
3. task-local authority for the current slice,
4. recent working memory only after the authoritative layers above are in place.

### Assembly outcomes

The system should support these session states:

1. `startup` - initial safe orientation,
2. `implementation` - focused coding or document-editing work,
3. `validation` - checks, PR evidence, CI, QA, runbook-guided proof,
4. `review` - findings, regressions, or RFC review,
5. `handoff` - concise durable state before pause or context transition.

## Compaction Policy

Compaction should be a governed transformation, not an uncontrolled shortening step.

### Required behavior

1. preserve exact engineering identifiers where they materially affect correctness,
2. preserve explicit decisions and open questions,
3. preserve current plan state and progress where still relevant,
4. preserve relationships between tool actions and their important outputs,
5. avoid flattening accepted, rejected, and deferred options into vague prose.

### Required preserved items

When relevant to the active or likely next slice, compaction must preserve:

1. current branch and PR reference,
2. commit ids referenced in the active program,
3. currently failing checks and their exact names,
4. active RFC ids and titles,
5. file paths changed or under review,
6. absolute identifiers for seeded data, endpoints, panels, and contracts,
7. open blockers and owner assumptions,
8. explicit next steps already agreed with the user.

### Prohibited compaction failures

Compaction should not:

1. paraphrase identifiers into approximate descriptions,
2. collapse exact check names into generic "tests failed" wording,
3. erase branch or PR identity,
4. drop explicit user decisions in favor of inferred summaries,
5. preserve so much stale detail that the compacted context becomes noisy instead of useful.

### Compaction output contract

When a session compacts, the resulting compacted state should preserve, in bounded form:

1. current task identity,
2. exact active identifiers still relevant to the next slice,
3. explicit accepted, rejected, deferred, and still-open decisions,
4. active plan state and next intended action,
5. known blockers, assumptions, and pending validations.

The compacted output should not attempt to become a full transcript replacement.

It should be:

1. precise,
2. identifier-safe,
3. decision-aware,
4. short enough to keep the next turn useful.

## Durable Note-Capture and Promotion Model

Before or during compaction, Lotus agent workflows should have one bounded chance to capture durable
notes when important information would otherwise be lost.

### Durable note categories

1. **Decision notes**
   important design or delivery choices not yet captured in docs or RFCs.
2. **Execution notes**
   validated commands, CI expectations, or repeatable fix-forward patterns.
3. **Context drift notes**
   mismatches between actual implementation truth and the current context system.
4. **Skill improvement notes**
   recurring routing or guidance gaps that should become skill or onboarding updates.

### Promotion targets

Depending on the note type, durable promotion should go to:

1. repository docs,
2. central context files,
3. onboarding docs,
4. wiki source,
5. skill files,
6. validators or contract tests,
7. RFC follow-up sections when the change is not yet implemented.

### Promotion rule

Promotion must stay bounded and reviewed.

The system should prefer:

1. explicit artifact updates,
2. concise durable notes,
3. no speculative permanent memory without a governed destination.

### Promotion decision rules

Promotion is required when a session uncovers information that is:

1. likely to affect the correctness of future work,
2. not already captured in the current source of truth,
3. reusable across future sessions, repos, or delivery slices,
4. too exact or operationally important to risk losing in compaction.

Promotion is not required for:

1. temporary scratch reasoning,
2. already-captured repository truth,
3. low-value conversational repetition,
4. implementation trivia with no future operational value.

## State Authority and Invariants

This RFC establishes the following authority rules.

1. platform-wide engineering context truth remains in `lotus-platform/context/`,
2. repository-local truth remains in the owning repository,
3. skills and onboarding docs are routing and operating aids, not replacement sources of
   architecture truth,
4. compacted session summaries are temporary working context, not durable system truth,
5. durable promoted notes must land in a governed artifact if they are intended to outlive the
   session.

The following invariants must hold:

1. context compaction must preserve exact identifiers when those identifiers are still operationally
   relevant,
2. durable note promotion must not create a second conflicting source of truth,
3. validator and skill updates must follow platform truth rather than inventing parallel policy,
4. the context system must remain smaller and more targeted after hardening, not more sprawling.

## OpenClaw Reference Findings

OpenClaw is useful here as a reference for patterns, not as a dependency or library.

The most relevant findings are:

1. **Context engine**
   a clear lifecycle for ingest, assemble, compact, and after-turn behavior is useful and should be
   translated into Lotus operating rules.
2. **Compaction**
   identifier-preserving summarization is valuable and directly relevant to engineering accuracy.
3. **Pre-compaction note capture**
   bounded durable note capture before compaction is a useful safeguard.
4. **Session management discipline**
   explicit handling of compacted versus recent context is better than relying on opaque overflow
   behavior.

Lotus should not copy:

1. plugin-driven context-engine extensibility as the primary model,
2. community-installed context providers,
3. loose personal-assistant assumptions around memory and session scope.

## Cross-Repository Impact

### `lotus-platform`

High impact:

1. central context rules,
2. onboarding docs,
3. AGENTS operating contract references,
4. skill routing and maintenance rules,
5. documentation contract validators where needed.

### All Lotus repositories

Medium impact:

1. repo-local context documents may need clarification where durable promotion reveals drift,
2. repo-local docs may become more important as promotion targets for validated notes.

### Codex skill system

High impact:

1. skills must reflect the new context-assembly and promotion rules,
2. skill updates become a required implementation consideration whenever these rules affect agent
   behavior.

## Alternatives Considered

### Alternative 1: Keep the current startup context system and rely on manual chat discipline

Rejected because it leaves long-session reliability too dependent on individual agent behavior and
does not solve compaction correctness.

### Alternative 2: Store arbitrary durable memory outside the governed documentation system

Rejected because it would create hidden or weakly governed sources of engineering truth.

### Alternative 3: Treat compaction as purely model/runtime behavior outside Lotus governance

Rejected because identifier loss and decision loss directly affect engineering correctness in Lotus
work.

## Implementation Plan

Every implementation slice must end with:

1. focused validation appropriate to the files changed,
2. a review pass for simplification, stale guidance, duplicate policy, and test quality,
3. a small truthful commit,
4. updated PR evidence,
5. updated shared-memory or handoff state when the work is cross-session.

### Slice 1: Context-Assembly Standard

1. document the governed Lotus context-assembly model,
2. define context layers and task-state modes,
3. define the "smallest correct working set" rule more explicitly for long-running sessions.

Deliverables:

1. RFC-approved context-assembly standard,
2. updated central context references where needed,
3. initial validator or contract-test targets if the standard changes durable platform truth.

### Slice 2: Compaction and Identifier-Preservation Standard

1. define exact identifier-preservation requirements,
2. define prohibited compaction failures,
3. define the required preserved items for PR, CI, RFC, and implementation loops.

Deliverables:

1. compaction standard text,
2. skill and onboarding guidance updates,
3. validation targets for critical identifier-preservation expectations where feasible.

### Slice 3: Durable Note-Capture and Promotion Rules

1. define note categories,
2. define promotion targets,
3. define when a session must promote durable knowledge instead of leaving it in chat.

Deliverables:

1. promotion-rule guidance,
2. context and onboarding updates,
3. any needed procedural-memory or skill cross-links.

### Slice 4: Skill, AGENTS, and Onboarding Hardening

1. update skills to reinforce context assembly, compaction, and promotion posture,
2. update AGENTS and onboarding docs,
3. keep the guidance concise and routing-oriented rather than duplicating long RFC prose.

Deliverables:

1. updated skills,
2. updated AGENTS or context files where needed,
3. onboarding updates.

### Slice 5: Validation and Contract-Test Hardening

1. update documentation or context validators where platform truth changed,
2. add targeted tests for cross-link integrity and required contract presence where appropriate,
3. ensure the context system remains coherent after the new rules are adopted.

Deliverables:

1. validator updates,
2. targeted tests,
3. truthful repo-native validation evidence.

### Slice 6: Code Review, Loose-End Tightening, API Certification Pattern, and Platform Governance

1. review all RFC-0093 implementation changes for duplicated guidance, stale context, overbroad
   prose, missing validation, and avoidable complexity,
2. verify any API-like or machine-readable contract introduced under this RFC follows the Lotus API
   certification pattern where applicable:
   - stable identity,
   - explicit schema or contract,
   - source-of-truth ownership,
   - validation evidence,
   - degraded or unsupported-state behavior,
   - OpenAPI or generated-contract alignment when an HTTP endpoint is involved,
3. verify platform governance requirements:
   - RFC-0072 lane evidence,
   - RFC-0073/RFC-0074 context ownership,
   - skill-routing consistency,
   - AGENTS synchronization when the operating contract changes,
   - no hidden second source of engineering truth,
4. remove stale or conflicting guidance discovered during implementation,
5. decide whether any remaining work must become a follow-up issue before the final slice.

Deliverables:

1. explicit review findings and fixes,
2. targeted validation rerun after review fixes,
3. platform governance checklist evidence,
4. updated gap or follow-up list if the RFC is not yet fully implemented.

### Slice 7: Documentation, Agent Context, Wiki Update, Skill Update if Needed, and Branch Hygiene

1. update docs that now own durable truth under this RFC,
2. update central and repo-local context artifacts where implemented truth changed,
3. update wiki-source guidance where operator or onboarding behavior changed,
4. explicitly assess whether skills, guidance, documentation, wiki, or context should be updated
   for future agent effectiveness,
5. update skills where the implementation changes durable agent workflow guidance,
6. record a conscious "no change needed" decision when a reviewed skill, guidance file, wiki page,
   or context artifact does not need modification,
7. keep PR evidence, branch cleanup, and implementation status truthful.

Deliverables:

1. updated docs and wiki-source pages,
2. updated context files,
3. updated skills where needed,
4. explicit skills/guidance/context/wiki assessment, including "no change needed" decisions,
5. PR and branch-hygiene evidence,
6. no stale guidance that implies implementation beyond what was actually delivered.

## Requirement Traceability

| Requirement | Primary implementation slice | Required evidence before closure |
| --- | --- | --- |
| Governed context-assembly model | Slice 1 | Context standard plus validator or documentation-contract evidence where feasible |
| Identifier-preserving compaction policy | Slice 2 | Skill/onboarding updates and targeted identifier-preservation validation where feasible |
| Bounded durable note capture and promotion | Slice 3 | Promotion rules with clear source-of-truth ownership and no hidden memory store |
| Skills, AGENTS, and onboarding alignment | Slice 4 | Updated guidance or explicit no-change rationale with AGENTS sync validation when applicable |
| Executable governance checks | Slice 5 | Repo-native validator/test evidence and PR lane evidence |
| Review and governance closure | Slice 6 | Review findings, fixes, API-certification/platform-governance checklist evidence |
| Final docs/context/wiki/skills/branch hygiene | Slice 7 | Final documentation/context/wiki/skills assessment and branch cleanup evidence |

### Current Evidence

| Evidence | Status | Notes |
| --- | --- | --- |
| `platform-contracts/agent-engineering/engineering-task-ledger-contract.v1.json` | Implemented on `main` | Captures RFC-0093 identifier-preservation, decision-state, and promotion-target requirements |
| `automation/validate_agent_engineering_contracts.py` | Implemented on `main` | Validates the shared RFC-0093/RFC-0094 contract shape |
| `tests/unit/test_agent_engineering_contracts.py` | Implemented on `main` | Proves the contract preserves required identifiers, decision states, promotion targets, task lifecycle, and delegation guardrails |
| `automation/Start-Background-Run.ps1` and `automation/Check-Background-Runs.ps1` | Implemented on `main` | Preserve deterministic task identity, lifecycle status, and evidence references across detached background-run monitoring |
| `tests/unit/test_agent_engineering_background_runs.py` | Implemented on `main` | Executes the monitor against synthetic state to prove legacy-state upgrade and failed-artifact truthfulness |
| `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md` | Implemented on `main` | Provides governed operating guidance for scoped context assembly, identifier preservation, task ledgers, delegation, and promotion decisions |
| `automation/validate_engineering_context_system.py` | Implemented on `main` | Validates that the RFC-0093/RFC-0094 playbook is registered in procedural memory and central engineering context |
| `codex/skills/platform-automation-ops/SKILL.md` | Implemented on `main` | Directs async platform automation work to the context/task-ledger playbook and preserves governed task identifiers |
| `tests/unit/test_lotus_skill_routing_behavior_contract.py` | Implemented on `main` | Protects skill routing and task-ledger skill guidance |
| `rfcs/RFC-0093-0094-slice-6-review-and-governance-evidence.md` | Implemented on `main` | Records the Slice 6 code-review, API-certification-pattern, platform-governance, and remaining-gap assessment |
| `rfcs/RFC-0093-0094-final-closure-evidence.md` | Implemented on `main` | Records final docs/context/wiki/skills/AGENTS/branch-hygiene decisions and final proof |

## Validation Posture

This RFC should drive both governed guidance and executable validation where the signal is strong
enough.

The platform should prefer validation for:

1. required cross-links,
2. required context artifact presence,
3. required skill or onboarding references after implementation,
4. obvious identifier-preservation contract checks where a validator can enforce them truthfully.

The platform should prefer governed prose rather than brittle automation for:

1. nuanced judgment about which session insights deserve promotion,
2. task-specific context minimization choices,
3. exact summarization quality beyond what can be validated meaningfully.

## Risks and Mitigations

### Risk: The context system becomes larger and noisier instead of more disciplined

Mitigation:

1. prefer smaller authoritative updates,
2. keep routing docs concise,
3. remove stale guidance rather than layering new prose on top of it.

### Risk: Durable note promotion creates duplicate sources of truth

Mitigation:

1. require governed promotion targets,
2. prefer existing source-of-truth artifacts over new ad hoc files,
3. update validators or cross-links where needed.

### Risk: Identifier-preservation rules are treated as optional style guidance

Mitigation:

1. state them as correctness requirements,
2. reflect them in skills and onboarding,
3. add targeted validation where feasible.

## Open Questions

Resolved by the active implementation branch:

1. Lotus now has a dedicated procedural-memory artifact for agentic context and task-ledger work:
   `context/playbooks/AGENT-CONTEXT-AND-TASK-LEDGER.md`.
2. The first required skill consumer is `platform-automation-ops`, because it directly owns
   detached local automation launched through `Start-Background-Run.ps1`.
3. The first executable validation targets are contract shape, required context/playbook
   registration, skill routing, and background-run state shape. Nuanced compaction quality remains
   governed guidance rather than brittle automation.

Remaining open question:

1. Which additional skills should become required consumers after repeated evidence shows the
   context-preservation rules are used outside async platform automation?

## Acceptance Criteria

1. Lotus has a documented context-assembly model for agentic development beyond the initial startup
   reading order.
2. Lotus has a documented compaction standard that preserves engineering-critical identifiers and
   decision lineage.
3. Lotus has a documented bounded durable note-capture and promotion model.
4. The RFC defines clear authority boundaries between:
   1. platform-wide context truth,
   2. repository-local truth,
   3. skill guidance,
   4. ephemeral session context.
5. The implementation plan includes a final slice for documentation, agent context, wiki update,
   skill update if needed, and branch hygiene.
6. The implementation plan includes a second-last review and governance slice covering loose-end
   tightening, API certification pattern checks where applicable, and platform governance
   conformance.
7. The final slice includes an explicit skills, guidance, documentation, wiki, and context
   assessment, including conscious "no change needed" decisions when appropriate.
8. No slice under this RFC creates an uncontrolled durable memory system outside the governed Lotus
   documentation and skill model.

## Final Position

Lotus has already solved startup context better than most codebases.

The next reliability gap is what happens after startup:

1. how sessions assemble the right working set,
2. how they compact without losing exact engineering truth,
3. how they promote important knowledge before it disappears,
4. how they stay reliable across long-running agentic development loops.

The correct Lotus answer is:

1. governed context assembly,
2. governed compaction,
3. bounded durable note promotion,
4. skill, onboarding, validator, and documentation alignment.

That is the platform-quality path for making agentic development in Lotus more reliable without
turning transient chat memory into an uncontrolled second source of truth.
