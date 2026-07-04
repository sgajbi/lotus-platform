# Lotus Skill Context Audit Standard

Use this standard when reviewing one skill or the full Lotus skill inventory.

## Audit Dimensions

| Dimension | Passing Standard | Common Finding |
| --- | --- | --- |
| Trigger clarity | Frontmatter says what the skill does and when to use it. | Broad or stale description makes routing ambiguous. |
| Progressive disclosure | `SKILL.md` contains mandatory workflow; detailed taxonomies live in references. | Large body repeats reference material. |
| Resource navigation | References over 100 lines have a table of contents and are linked from `SKILL.md`. | Long reference is hard to skim or undiscoverable. |
| Script governance | Scripts are deterministic, referenced, compiled or tested, and replace repeatable manual work. | Script exists but no skill guidance or validation proof mentions it. |
| Token efficiency | Skill body is concise, references are routed, and scripts avoid repeated reasoning. | Skill forces every agent to reload broad prose or reconstruct commands. |
| Lower-model robustness | Workflow is explicit enough for less-capable models: step order, decision rules, acceptance checks, and failure handling are concrete. | Guidance depends on senior judgment without guardrails or examples. |
| Manifest alignment | Manifest contains added/moved/renamed/reclassified skills and category is accurate. | Skill folder exists but is absent from manifest. |
| Routing alignment | Routing map and skill description agree on task intent and precedence. | Multiple skills claim the same task without precedence. |
| OpenAI metadata | `agents/openai.yaml` is present for directly Lotus-owned skills and matches current purpose. | Default prompt omits important new workflow area. |
| Continuous improvement | Skill includes the governed continuous improvement section. | Future-agent learning remains chat-only. |
| Local sync posture | Platform source is authoritative and bootstrap sync can update local deployed skills. | Local skill copy diverges or source/local parity is unproven. |
| Validation proof | Changed skills have quick validation, alignment validation, bootstrap proof, and focused script checks. | Markdown changed without executable proof. |

## Severity Calibration

- `critical`: skill cannot validate, manifest/routing prevents discovery, or sync would deploy broken guidance.
- `high`: agents are likely to choose the wrong skill, miss mandatory context, or file/implement unsafe work.
- `medium`: maintainability or review quality is degraded but current routing still works.
- `low`: cleanup or consistency improvement with limited behavioral effect.

## Whole-Inventory Review Procedure

1. Run the audit script.
2. Read the report and inspect any flagged skill manually before editing.
3. Fix packaging or drift issues that are low risk and clearly correct.
4. Avoid broad rewrites unless a skill is structurally blocking future work.
5. Record follow-ups for large splits, merges, or validator promotions.

## Automation Placement Rule

Add automation inside a skill when the automation is part of how the skill is used. Good examples:

1. label creation for issue-discovery,
2. lens catalog drift validation,
3. campaign-plan generation,
4. skill inventory audit,
5. README/wiki quality audit,
6. RFC inventory checks.

Prefer platform-level automation when the command governs the whole ecosystem independent of one
skill, such as bootstrap sync, platform repo checks, mesh certification, or cross-repo validation.

## No-Change Examples

Record `no-change` when:

1. a skill is intentionally narrow and only needs a routing-map mention elsewhere;
2. a long reference is a taxonomy and already has a table of contents;
3. a supporting non-Lotus skill is present in the manifest because another Lotus skill depends on it;
4. a potential issue belongs in a deterministic CI gate rather than more prose guidance.
