# RFC-0081 Slice 9: AI Surface Governance and Assistive Workflow Controls Evidence

## Scope of this slice

Slice 9 reviewed the current Lotus AI-facing surfaces and the service contracts that already exist
behind them.

The review covered:

1. `lotus-workbench` AI-facing UI posture,
2. `lotus-gateway` advisor-brief AI contract and audit posture,
3. `lotus-advise` workspace-rationale AI seam,
4. `lotus-ai` task, retrieval, and audit contracts,
5. the gap between current backend capability and current shell-wide UI governance.

## Current-state findings

### `lotus-gateway` already carries meaningful AI audit structure

`lotus-gateway/src/app/services/advisor_brief_service.py` already exposes a stronger AI contract
than the current UI governance suggests.

The existing posture is good because it already includes:

1. `ai_audit` with task, prompt, provider, adapter, model, generation time, and stub state,
2. `ai_evidence` and source references,
3. explicit `READY`, `PARTIAL`, and `UNAVAILABLE` handling,
4. fallback behavior when AI is unavailable,
5. separation between source-backed metrics and AI-produced narrative.

That is the right contract direction.

### `lotus-advise` already has an AI-assist seam, but it is still narrow

`lotus-advise/src/api/services/workspace_ai_service.py` and
`lotus-advise/src/integrations/lotus_ai/rationale.py` already define an evidence-grounded
workspace-rationale path.

The current seam is useful because:

1. it refuses to run without evaluated workspace state,
2. it passes a bounded evidence object to the AI layer,
3. it keeps AI assist subordinate to deterministic proposal evaluation.

The limitation is that this is still an integration seam, not yet a governed UI pattern.

### `lotus-ai` is more operationally mature than the current UI usage

`lotus-ai` already exposes:

1. task capability and execution contracts,
2. audit record contracts,
3. retrieval governance and activation-readiness contracts,
4. bounded evidence structures,
5. staged search and activation posture.

This means Lotus does not need to invent AI governance from scratch in the UI.

The UI needs to represent and constrain it correctly.

### `lotus-workbench` still lacks a shell-wide AI interaction grammar

The current `lotus-workbench` posture is transitional:

1. advisor brief provenance exists,
2. some AI audit and evidence fields already flow into the front end,
3. there is no shared shell-wide AI disclosure pattern,
4. there is no governed feedback capture pattern for AI-assisted outputs,
5. there is no consistent distinction between:
   - AI-assisted narrative,
   - human-reviewed recommendation,
   - authoritative workflow state.

There is also no governed shell-native model yet for:

1. AI review required states,
2. AI assist status in workflow rails,
3. AI action telemetry,
4. AI output lifecycle from generated to accepted, revised, or rejected.

## Keep / replace / retire decisions

### Keep

1. `lotus-gateway` advisor brief audit and evidence fields,
2. `lotus-advise` evidence-grounded workspace-rationale seam,
3. `lotus-ai` task and audit contracts,
4. partial and unavailable AI degradation behavior,
5. source-backed fallback behavior when AI is unavailable.

### Replace

1. page-local AI provenance treatment with one shared shell pattern,
2. implicit AI state with explicit banker-facing review state,
3. isolated AI narrative rendering with module-level disclosure and audit affordances,
4. AI-only descriptive UI with workflow-aware AI action controls,
5. passive AI surfacing with feedbackable and reviewable AI interactions.

### Retire

1. any future UI pattern where AI-generated text appears without explicit provenance,
2. any future workflow module where AI recommendations are visually indistinguishable from approved workflow truth,
3. page-local one-off AI badges or disclaimers,
4. any future AI assist surface that lacks audit linkage or user feedback capture,
5. any future AI command surface that bypasses shell entitlements, logging, or workflow gating.

## Target AI governance model confirmed by slice 9

### 1. AI disclosure model

All AI-assisted surfaces must disclose:

1. that the content is AI-assisted or AI-generated,
2. which capability produced it,
3. when it was generated,
4. whether it is stubbed, draft, human-reviewed, approved, or rejected,
5. what source evidence it used when available.

This disclosure must be represented through shared shell primitives, not page-local copy.

### 2. Human review and workflow separation model

AI output must remain subordinate to workflow truth.

The shell must distinguish:

1. authoritative workflow state from gateway or domain services,
2. AI-assisted explanation or recommendation,
3. human review status for that AI-assisted output,
4. workflow consequence of accepting, rejecting, or revising the AI output.

AI-generated content must never be allowed to masquerade as:

1. suitability approval,
2. compliance approval,
3. execution readiness,
4. client consent,
5. final banker instruction.

### 3. Feedback and quality loop model

Every workflow-native AI surface should support structured banker feedback.

The minimum feedback model should allow:

1. useful,
2. not useful,
3. needs correction,
4. factually weak,
5. tone not appropriate,
6. explain issue.

Feedback should be tied to:

1. the generated output,
2. the task id,
3. the prompt or model posture,
4. the workspace and workflow context,
5. the banker or operator identity where governance permits.

### 4. Assistive action-boundary model

AI can assist with:

1. summarization,
2. rationale drafting,
3. recommendation framing,
4. search and discovery,
5. evidence explanation,
6. next-best-action suggestions.

AI cannot directly establish:

1. lifecycle truth,
2. workflow approval,
3. client consent,
4. execution handoff,
5. booking or trade intent authority.

All assistive actions must remain bounded by:

1. shell entitlements,
2. gateway contract posture,
3. workflow gate rules,
4. audit logging,
5. explicit banker action.

### 5. Shell-wide AI module pattern

RFC-0081 implementation should treat AI UI as a governed module pattern, not an embedded exception.

Each AI-bearing module should declare:

1. owning service,
2. capability identifier,
3. authoritative source of workflow truth,
4. AI provenance fields,
5. feedback capture contract,
6. review state model,
7. degraded-state behavior,
8. telemetry and audit events.

### 6. Retrieval and search governance linkage

The existing `lotus-ai` retrieval contracts are already mature enough to shape the UI model.

That means:

1. AI search must expose source posture and retrieval stage,
2. semantic answers must carry source and audit linkage,
3. search results must not flatten authoritative and assistive results into one undifferentiated list,
4. retrieval activation posture must remain visible to operators where relevant,
5. command and search surfaces in later slices must inherit these governance rules.

## Structural implications for implementation

Slice 9 confirms that implementation should not add AI UI as:

1. one-off banner components,
2. freeform prompt widgets per page,
3. route-local feedback forms,
4. detached chatbot overlays that bypass workspace context.

Instead, implementation should introduce:

1. shared AI provenance primitive,
2. shared AI feedback primitive,
3. shared AI review-state primitive,
4. shell-aware AI assist panel or drawer patterns,
5. workflow-safe AI action wrappers,
6. telemetry and audit adapters shared across AI-bearing modules.

## Dead code and weak-pattern review

No slice-9-specific dead code was removed in `lotus-platform`, because this slice is governance and
assessment evidence.

However, the assessment confirmed weak implementation patterns that must be removed during code work:

1. page-local AI disclosure styling,
2. duplicated provenance-strip treatments in large global CSS,
3. AI-specific rendering logic buried inside large workspace view models,
4. future ad hoc feedback controls implemented inside individual pages rather than shared components.

## Skills, context, and documentation review

No immediate skill or onboarding guidance update is required before implementation begins.

That is a conscious decision for this slice because:

1. the current runtime and routing guidance is still correct,
2. the AI governance model has not yet changed the governed execution path,
3. the right time to update skills and context is after shell-wide AI primitives and search surfaces
   actually exist.

What must be reviewed later:

1. whether `lotus-front-office-runtime` should explicitly describe AI-bearing surface validation,
2. whether AGENTS guidance needs a stronger rule for separating AI-assisted content from workflow truth,
3. whether screenshot and browser automation guidance should require AI provenance validation when AI surfaces are present.

## Review of slice 9

Slice 9 is complete.

The most important conclusion is that Lotus already has strong AI audit and evidence contracts in
`lotus-gateway`, `lotus-advise`, and `lotus-ai`.

The gap is in governed UI representation, not raw service capability.

That is the right sequencing outcome for RFC-0081:

1. do not invent new backend AI abstractions unless the UI truly needs them,
2. standardize disclosure, review, feedback, telemetry, and safe action boundaries in the shell,
3. carry retrieval and audit posture forward into later AI search and agentic-extension slices.

Slice 9 is complete.
