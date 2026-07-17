---
name: lotus-skill-context-governance
description: Use when maintaining, auditing, creating, splitting, merging, or reviewing Lotus skills, agent context, skill routing, skill manifests, deployed-skill sync, AGENTS.md guidance, procedural memory, or reusable agent guardrails across Lotus repositories. Apply when the user asks whether a new skill is needed, to review all skills, to curate iterative skill changes, to prevent skill/routing drift, or to promote repeated agent-workflow lessons into durable skills, context, validators, scaffolds, gates, or an explicit no-change decision.
---

# Lotus Skill Context Governance

## Purpose

Use this skill to steward the Lotus agent operating system: platform-owned Codex skills, routing
context, agent contracts, procedural memory, manifests, validators, and deployed local sync.

This skill is the first stop when the task is primarily about skill quality or agent context. Use
`lotus-ci-enforcement-governance` as a supporting skill when the outcome should become a CI gate,
quality scorecard, scaffold rule, or deterministic enforcement check.

The goal is leverage: make Lotus skills, automation, and context strong enough that future agents
use fewer tokens, make fewer routing mistakes, and can execute reliably even when the model is less
capable. Prefer compact trigger-time instructions, progressive disclosure, deterministic scripts,
repo-native commands, and explicit acceptance checks over long prose that every agent must reread.

## Required Context

Load the smallest correct working set:

1. `AGENTS.md`
2. `context/LOTUS-QUICKSTART-CONTEXT.md`
3. `context/LOTUS-ENGINEERING-CONTEXT.md`
4. `REPOSITORY-ENGINEERING-CONTEXT.md`
5. `context/CONTEXT-REFERENCE-MAP.md`
6. `context/PROCEDURAL-MEMORY-INDEX.md`
7. `context/LOTUS-SKILL-ROUTING-MAP.md`
8. `codex/skills/README.md`
9. `codex/skills/lotus-skill-manifest.json`
10. the target skill `SKILL.md`, `agents/openai.yaml`, references, scripts, and relevant validators

Read `references/skill-context-audit-standard.md` before doing a whole-skill inventory review or
creating a new skill.

## Decision Rules

Before creating a new skill, prove that the need is distinct from current routing:

1. The task family recurs across repositories or sessions.
2. Existing skills cover it only indirectly or create routing ambiguity.
3. The durable behavior is more than one paragraph of guidance.
4. Future agents need a separate trigger phrase, checklist, reference, or script.
5. The new skill has a clear owner, validation path, and manifest category.

Prefer tightening an existing skill when the change only affects one workflow step, one trigger
phrase, or one lens. Create a new skill when the work is a durable operating surface, such as
cross-skill inventory stewardship, platform-wide routing hygiene, or deployed-skill sync posture.

Use this control-placement order:

1. skill guidance for judgment-heavy agent behavior;
2. routing-map update for task selection or overlap changes;
3. central context update for platform-wide source-of-truth changes;
4. repo-local context update for repository-specific truth;
5. validator, scaffold, or gate when deterministic enforcement is better than prose;
6. docs/wiki update when operator-facing or reader-facing truth changed;
7. explicit no-change decision when the lesson is local, speculative, or already covered.

Use the token-efficiency rule:

1. if agents keep rereading the same long prose, move detail into a reference with a clear table of
   contents and load instructions;
2. if agents keep retyping the same command sequence, add or improve a script under the relevant
   skill;
3. if agents keep deciding the same routing question, update `LOTUS-SKILL-ROUTING-MAP.md`;
4. if agents keep missing the same factual context, update central or repo-local context;
5. if agents keep making the same objective mistake, add a validator, scaffold guard, or CI gate.

## Whole-Skill Review

For a holistic review of all platform-owned skills:

1. Inspect `codex/skills/lotus-skill-manifest.json` and all `codex/skills/*/SKILL.md` files.
2. Run `python codex\skills\lotus-skill-context-governance\scripts\audit_lotus_skills.py`
   (`scripts/audit_lotus_skills.py`).
3. Review the generated report under `output/lotus-skill-context-audit.md`.
4. Classify findings as:
   - `fix-now`: low-risk packaging, routing, or validation drift that should be corrected in the
     same slice;
   - `follow-up`: real improvement that needs a bounded later task;
   - `no-change`: acceptable current posture or intentionally delegated responsibility.
5. Patch only focused, high-confidence issues. Do not rewrite every skill for style consistency.
6. Re-run the audit, skill validation, skill alignment validation, and bootstrap sync.

For each skill, check:

- frontmatter has only `name` and `description`, and the description clearly states when to use it;
- `agents/openai.yaml` exists for directly Lotus-owned skills and matches the skill purpose;
- body is concise enough for trigger-time loading, with detailed material moved into references;
- long references have a table of contents;
- scripts are deterministic, tested or compiled, referenced from `SKILL.md`, and replace repeated
  fragile manual reasoning or command sequences;
- `Continuous Skill Improvement` exists;
- the manifest category, routing map, and skill description agree;
- local deployed skills are consumers of platform source, not divergent source truth.

## Skill Maintenance Workflow

When changing skills or agent context:

1. State the active target repo as `lotus-platform`.
2. Inspect current worktree state and preserve unrelated user or agent changes.
3. Identify the repeated failure pattern or user request that justifies the change.
4. Decide whether the change belongs in a skill, reference, script, routing map, manifest, context,
   validator, scaffold, docs/wiki source, or a no-change note.
5. Make focused edits under `codex/skills/` and `context/` using platform-owned source files.
6. Update `codex/skills/lotus-skill-manifest.json` only when adding, removing, moving, renaming, or
   reclassifying a skill.
7. Update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changes.
8. Update `codex/skills/README.md` when inventory ownership or maintenance rules change.
9. Run the validation proof pack.
10. Record explicit no-wiki-change unless repo-local wiki source changed.

Do not hand-edit `C:\Users\<user>\.codex\skills` as authoritative source. Use bootstrap sync after
platform-owned source changes.

## Validation Proof Pack

For skill/context governance work, run the checks that match the slice:

```powershell
python codex\skills\lotus-skill-context-governance\scripts\audit_lotus_skills.py
python -m py_compile codex\skills\lotus-skill-context-governance\scripts\audit_lotus_skills.py
python automation\validate_lotus_skill_alignment.py
powershell -ExecutionPolicy Bypass -File automation\Bootstrap-LotusDeveloperEnvironment.ps1 -Profile fast -ValidateAfterSync
```

Also run the changed skill's checked-in validator when it has one, such as issue-discovery
label/catalog validators. Do not assume a shared `quick_validate.py` exists: locate and invoke the
validator owned by the changed skill, then record an explicit no-skill-specific-validator decision
when the alignment validator is the only applicable structural proof.

When a new skill is added, validate:

- the skill itself with `quick_validate.py`;
- manifest inclusion and category;
- routing-map row or trigger section;
- OpenAI metadata;
- bootstrap sync and local deployed parity.

## Review Output

When reporting a whole-skill audit, include:

1. skills reviewed and audit command;
2. high-value fixes made;
3. follow-up findings by severity;
4. validation commands and outcomes;
5. no-wiki-change or wiki update decision;
6. whether local deployed skill sync is ready.

Keep the report focused on actionable drift. Avoid broad style opinions unless they affect
triggering, execution, validation, sync, or future-agent correctness.

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
