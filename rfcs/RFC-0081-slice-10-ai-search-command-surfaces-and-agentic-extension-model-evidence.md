# RFC-0081 Slice 10: AI Search, Command Surfaces, and Agentic Extension Model Evidence

## Scope of this slice

Slice 10 reviewed how Lotus should support:

1. AI search,
2. shell-level command entry,
3. semantic discovery,
4. future workflow-native agentic assist surfaces,
5. extension without shell drift.

The review focused on:

1. current `lotus-workbench` shell posture,
2. current route and discovery posture,
3. `lotus-gateway` experience-composition implications,
4. `lotus-ai` retrieval and execution-path contracts,
5. future shell topology needed for AI search and command-driven workflows.

## Current-state findings

### `lotus-workbench` shell is not yet ready for governed search and command entry

`lotus-workbench/src/shell/app-shell.tsx` is still intentionally thin.

That is acceptable for the current product stage, but it is not sufficient for the target state
because the shell does not yet provide governed space for:

1. shell-level search,
2. command palette or command center entry,
3. contextual cross-workspace navigation,
4. AI search and assist invocation,
5. persistent result or task-review panels.

### Current discovery posture is still transitional

`lotus-workbench/src/apps/recommendations/page.tsx` currently redirects to other workspaces instead
of hosting a governed discovery experience.

That confirms the platform has not yet locked:

1. what discovery belongs in the shell,
2. what discovery belongs in a workspace,
3. what AI search results look like,
4. how command-driven actions are staged and reviewed.

### `lotus-ai` already has the right retrieval and execution governance foundation

`lotus-ai` already exposes strong contracts for:

1. retrieval search and execution status,
2. retrieval activation readiness,
3. retrieval governance status,
4. audit and evidence,
5. app-capability rollout governance,
6. task execution path discipline.

This means Lotus should not build shell search as an ungoverned frontend convenience.

Shell search and command surfaces should be thin product entry layers over governed backend posture.

### `lotus-gateway` is not yet the shell discovery composition layer

The current gateway posture is stronger for workspaces than for discovery and command entry.

That is the right current boundary, but RFC-0081 needs the next target model to be explicit:

1. gateway should compose shell discovery state,
2. gateway should broker search and command entry contracts for the shell,
3. gateway should keep workflow truth, entitlement, and evidence posture visible,
4. gateway should stop discovery surfaces from becoming detached UI-only features.

## Keep / replace / retire decisions

### Keep

1. `lotus-ai` retrieval and execution-governance contracts,
2. task execution-path discipline in `lotus-ai`,
3. gateway-first shell composition posture,
4. bounded discovery and retrieval activation semantics,
5. app-capability rollout governance for staged AI expansion.

### Replace

1. route-level redirect placeholders with governed discovery surfaces,
2. ad hoc workspace search ideas with one shell-owned command and discovery model,
3. detached AI-assist entry points with context-aware shell entry,
4. frontend-only discovery semantics with gateway-backed and audit-aware search posture.

### Retire

1. any future command center implemented as a parallel standalone product area,
2. any future AI search surface that bypasses shell navigation and entity context,
3. any future semantic result set that mixes authoritative records and assistive summaries without distinction,
4. any future route-local command widget that duplicates shell behavior,
5. discovery routes that exist only as transitional redirects once governed shell search exists.

## Target AI search and command model confirmed by slice 10

### 1. Shell-owned discovery entry model

Lotus should expose one governed discovery entry model at shell level.

That model should provide:

1. global search entry,
2. command palette entry,
3. recent and pinned entities,
4. workflow-aware shortcuts,
5. AI search and assist entry points,
6. explicit separation between search, command, and assist modes.

The shell should own entry and framing.

Workspaces should own domain-specific drill-down once the user lands in the correct context.

### 2. Result-class model

Search and command results must be typed by result class.

The shell should distinguish at least:

1. portfolio entities,
2. client and relationship entities,
3. proposals and workflow items,
4. approvals and consent tasks,
5. reports and artifacts,
6. AI-assisted answers,
7. semantic retrieval citations,
8. command actions.

This is required so the UI can render:

1. authoritative records with their entity identity,
2. workflow items with readiness and blocking state,
3. AI-assisted answers with provenance and evidence,
4. commands with explicit preconditions and follow-through.

### 3. Search and assist separation model

AI search is not the same thing as an AI assistant conversation.

RFC-0081 should therefore treat these separately:

1. search:
   - retrieval-first,
   - entity and artifact discovery,
   - shell navigation support
2. command:
   - action invocation,
   - route entry,
   - workflow shortcuts
3. assist:
   - contextual explanation,
   - summarization,
   - rationale support,
   - next-best-action support.

All three can share shell entry, but they must not collapse into one ambiguous surface.

### 4. Agentic extension model

Future agentic AI features should plug into the shell as governed modules.

That model should require:

1. task framing,
2. entitlement and workflow checks before invocation,
3. queue, running, review-required, failed, and completed states,
4. audit and telemetry emission,
5. evidence and provenance display,
6. explicit human approval points where workflow impact exists.

Agentic capabilities must remain:

1. workflow-native,
2. auditable,
3. reviewable,
4. subordinate to banker control.

### 5. Command and search gateway model

The shell should not talk directly to multiple downstream search or assist systems.

The target model should route shell discovery through `lotus-gateway`, which should expose:

1. shell search bootstrap,
2. command catalog or command manifest,
3. typed search result groups,
4. entitlement-filtered actions,
5. workflow-aware shortcuts,
6. AI search and assist posture,
7. freshness and evidence semantics for returned results.

### 6. Automation and validation model

Once AI search and command entry land, they must be added to governed automation rather than treated
as exploratory extras.

Automation should validate:

1. shell search opens and returns typed results,
2. authoritative and AI-assisted results render differently,
3. AI-assisted answers show provenance and evidence,
4. command actions honor gating and entitlements,
5. degraded retrieval and unavailable AI states remain truthful,
6. screenshots and runtime evidence include discovery surfaces when they become part of the
   supported product flow.

## Structural implications for implementation

Slice 10 confirms that the shell architecture must reserve explicit space for:

1. global discovery,
2. command invocation,
3. contextual AI assist,
4. result review drawers or panels,
5. progressive task and feedback states.

That means implementation should avoid:

1. bolting command search onto one workspace,
2. implementing search only inside route-local headers,
3. turning AI search into a separate shell competing with core navigation,
4. creating one-off result cards per feature team.

Instead, implementation should introduce:

1. shell-level search and command primitives,
2. typed result renderers,
3. gateway-backed discovery adapters,
4. reviewable assist drawers and panels,
5. shared telemetry and audit wrappers for command and assist actions.

## Dead code and weak-pattern review

No slice-10-specific dead code was removed in `lotus-platform`, because this slice is governance and
assessment evidence.

The assessment did confirm weak patterns that must be retired during implementation:

1. redirect-only discovery placeholders,
2. shell surfaces with no governed search or command posture,
3. transitional capability names such as `command_center` that are not yet reflected in a stable
   banker-facing shell model,
4. any future duplication between shell search, workspace search, and AI assist entry points.

## Skills, context, and documentation review

No immediate skill or onboarding guidance update is required before implementation begins.

That is a conscious decision for this slice because:

1. current agent routing is still correct,
2. AI search and command surfaces do not exist yet in the governed runtime,
3. documentation should be updated only once shell-owned search and command primitives are real.

What must be reviewed later:

1. whether `lotus-front-office-runtime` should explicitly reference search and command validation,
2. whether onboarding docs should describe banker-facing search and command posture,
3. whether agent guidance should distinguish shell command entry from domain workflow execution.

## Review of slice 10

Slice 10 is complete.

The most important conclusion is that Lotus already has enough backend retrieval and audit posture in
`lotus-ai` to support a governed shell search model.

The main missing work is:

1. shell-owned discovery entry,
2. gateway-backed composition for typed discovery and command results,
3. clear separation of search, command, and assist,
4. governed automation and validation for these surfaces.

Slice 10 is complete.
