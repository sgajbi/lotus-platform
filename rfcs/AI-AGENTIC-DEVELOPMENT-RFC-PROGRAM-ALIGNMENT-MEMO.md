# AI Agentic Development RFC Program Alignment Memo

- Date: 2026-04-18
- Scope:
  - `lotus-ai` RFC-0032
  - `lotus-ai` RFC-0033
  - `lotus-platform` RFC-0093
  - `lotus-platform` RFC-0094

## Purpose

This memo is not a fifth RFC.

It exists to keep the four approved RFC tracks aligned during implementation planning and early
slices.

The memo is intentionally short and operational.

Its role is to:

1. prevent boundary drift between the RFCs,
2. define one source-of-truth matrix,
3. provide one shared vocabulary table,
4. identify the first adopters,
5. define the recommended implementation order.

## RFC Boundary Summary

### RFC-0032

Question answered:

1. **May this workflow pack version run?**

Owns:

1. workflow-pack registry,
2. registration state,
3. activation posture,
4. rollout and deprecation control,
5. eligibility evaluation.

Does not own:

1. run execution history,
2. review-state lifecycle,
3. engineering async task tracking.

### RFC-0033

Question answered:

1. **What happened when this workflow pack ran, and what review state is its output in?**

Owns:

1. pack-run ledger,
2. runtime-state and review-state separation,
3. output, evidence, and artifact linkage,
4. gateway/workbench contract family for AI run and review posture.

Does not own:

1. whether a pack version was eligible to run in the first place,
2. engineering background task tracking,
3. platform-wide context assembly rules.

### RFC-0093

Question answered:

1. **How should long-running Lotus agent sessions assemble, compact, and promote context correctly?**

Owns:

1. context assembly model,
2. compaction policy,
3. identifier preservation,
4. bounded durable note promotion,
5. context, skill, and onboarding alignment for long-running agentic work.

Does not own:

1. product AI runtime state,
2. engineering detached task lifecycle,
3. pack registry or pack-run runtime contracts.

### RFC-0094

Question answered:

1. **How should detached engineering work and bounded delegation be tracked and governed?**

Owns:

1. background engineering task ledger,
2. detached task lifecycle,
3. delegation scope and return rules,
4. async operating discipline for engineering work.

Does not own:

1. long-session context compaction rules,
2. product-facing AI run or review state,
3. workflow-pack registry activation.

## Source-of-Truth Matrix

| Concern | Source of truth | Notes |
| --- | --- | --- |
| Workflow-pack registration identity and activation | `lotus-ai` registry model under RFC-0032 | Governs whether a workflow-pack version may run |
| Workflow-pack run identity, runtime state, review state, and lineage | `lotus-ai` pack-run ledger under RFC-0033 | Governs what happened when a pack ran |
| Workflow authority and consequence-bearing business state | calling workflow service or gateway/domain owner | Never owned by `lotus-ai` |
| Platform-wide context truth | `lotus-platform/context/` and platform-owned docs | Governed by RFC-0073, RFC-0074, RFC-0093 |
| Repository-local engineering truth | owning repo `REPOSITORY-ENGINEERING-CONTEXT.md` and repo docs | Never replaced by platform summaries |
| Background engineering task truth for GitHub checks | GitHub Actions and PR state | RFC-0094 records/aligns status but does not replace GitHub truth |
| Background engineering task truth for local automation | platform automation artifacts and scripts | RFC-0094 standardizes identity, lifecycle, and evidence posture |
| Agent routing and async operating guidance | skills, AGENTS guidance, onboarding docs | Must follow platform truth, not invent parallel policy |

## Canonical Vocabulary Table

| Term | Meaning | Primary RFC |
| --- | --- | --- |
| `pack_id` | Stable workflow-pack family identifier | RFC-0032 |
| `registration_ref` | Registry record that authorized a specific pack version | RFC-0032 |
| `activation_state` | Registry control-plane status for whether a registered pack version is operationally allowed | RFC-0032 |
| `pack_run_id` | Durable identity for one workflow-pack execution | RFC-0033 |
| `runtime_state` | Execution posture of a workflow-pack run | RFC-0033 |
| `review_state` | Review posture of AI-generated output from a workflow-pack run | RFC-0033 |
| `engineering_task_id` | Durable identity for detached engineering work such as background runs or delegated subtasks | RFC-0094 |
| `task_kind` | Category of detached engineering work | RFC-0094 |
| `context assembly` | Governed selection of the smallest correct working set for a Lotus agent task | RFC-0093 |
| `compaction` | Governed reduction of session context while preserving exact engineering-critical identifiers and decisions | RFC-0093 |
| `promotion` | Moving durable session knowledge into governed artifacts such as docs, context files, skills, or validators | RFC-0093 |

## First-Adopter Map

### RFC-0032 first adopter

1. `advisor_brief`

Reason:

1. it is already the most plausible first workflow-pack family,
2. it is cross-service enough to prove registration and activation posture,
3. it is bounded and review-friendly.

### RFC-0033 first adopter

1. `advisor_brief`

Reason:

1. it is the natural first pack-run and review-state proving surface,
2. it already aligns with gateway and Workbench product surfaces.

### RFC-0093 first adopters

1. central context system,
2. Lotus skills most directly involved in long-running agentic work,
3. onboarding and AGENTS guidance.

### RFC-0094 first adopters

1. platform background-run automation,
2. PR-loop monitoring guidance,
3. async/delegation-oriented skills such as `async-task-runner` and `platform-automation-ops`.

## Recommended Implementation Order

### 1. RFC-0032 Slice 1

Why first:

1. define what can run before recording what happened when it ran.

### 2. RFC-0093 Slice 1

Why second:

1. improve long-running agent correctness before the implementation program broadens.

### 3. RFC-0033 Slice 1

Why third:

1. once pack identity and activation are clear, the durable run-ledger model can be implemented on
   top of them.

### 4. RFC-0094 Slice 1

Why fourth:

1. once context discipline is improved, detached engineering work can be aligned around the same
   reliability posture.

## Validation Ownership Guidance

### `lotus-ai`

Expected first validation ownership for:

1. RFC-0032,
2. RFC-0033.

Likely proof types:

1. schema and contract tests,
2. service-layer tests,
3. runtime integration tests,
4. gateway contract tests where needed.

### `lotus-platform`

Expected first validation ownership for:

1. RFC-0093,
2. RFC-0094.

Likely proof types:

1. unit contract tests,
2. documentation contract checks,
3. skill and context cross-link validation,
4. automation output shape checks where applicable.

## Implementation Rule

If a future slice appears to change the answer to more than one of these questions at once:

1. may it run,
2. what happened when it ran,
3. how should long-running context survive,
4. how should detached engineering work survive,

then the slice is probably crossing RFC boundaries and should be narrowed before implementation.

## Final Position

These four RFCs are one coherent program, but they are not one giant implementation unit.

The split is deliberate:

1. `lotus-ai` RFCs govern product/runtime control planes,
2. `lotus-platform` RFCs govern engineering-system control planes.

This memo exists so the implementation program can stay coherent without collapsing those boundaries.
