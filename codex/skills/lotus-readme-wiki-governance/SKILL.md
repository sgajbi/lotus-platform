---
name: lotus-readme-wiki-governance
description: Create or refresh a gold-standard README.md and GitHub wiki structure for Lotus repositories. Use when standardizing repository documentation, seeding a new repo wiki, upgrading a weak README, aligning repo docs to Lotus platform governance, or producing a reusable README/wiki pattern that must stay consistent across Lotus apps.
---

# Lotus Readme Wiki Governance

Use this skill after loading the smallest correct Lotus context set:

1. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
2. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
3. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`
4. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
5. only the additional local docs needed to make the README or wiki truthful

Use the platform-owned skill source in `lotus-platform/codex/skills`, not the local Codex profile,
as the durable home for Lotus documentation workflow guidance.

## Workflow

1. Classify the repository before writing:
   - `product-ui`
   - `experience-api`
   - `domain-service`
   - `shared-capability-service`
   - `platform-governance`
2. Read the current `README.md`, the repo context, and only the supporting docs needed for:
   - purpose and boundaries
   - quick start and run path
   - validation commands
   - runtime and integration posture
   - operations and troubleshooting entrypoints
3. Derive the repo surface from code as well as prose:
   - read the app entrypoint or main startup path
   - inspect router or route modules for public API groupings
   - inspect contracts or request/response models for the real integration shape
   - inspect `Makefile` or equivalent repo-native command surface
   - use those code surfaces to decide how the wiki should group the system
4. Before a major README rewrite, check whether the repo already has docs regression tests or
   public-contract tests that pin README or guide language. Search the test tree for `README.md`,
   key guide paths, or `docs` contract test packs so you preserve governed public truth instead of
   deleting required contract language accidentally.
5. When the repository has been split, renamed, or re-scoped, scan current operator-facing evidence
   docs such as `docs/demo/`, manual-validation notes, and runbooks for stale service names, image
   names, ingress identities, and command targets.
6. Preserve repo truth. Do not invent maturity, ownership, runtime support, or production readiness.
7. Keep the README short enough to orient a new engineer quickly. Route to deeper docs instead of
   copying them.
8. Keep the wiki operator- and onboarding-focused. It should summarize, organize, and link; it
   should not become an unbounded duplicate of `docs/`.
9. When a repo exposes mixed request conventions, compatibility aliases, or easy-to-confuse query
   shapes, include copy-paste-ready request examples in the wiki so future agents and operators do
   not silently document the wrong contract.
10. For product-UI repositories, distinguish active supported surfaces from compatibility routes,
   disabled navigation entries, and target future topology. Do not treat every historical route or
   shell label as an active product commitment.
11. Use this content split:
   - `README.md`: fast repo truth, top-level contracts, commands, and navigation
   - wiki: onboarding flow, operator maps, grouped surface explanations, and runbook summaries
   - deep docs under `docs/`: detailed architecture, standards, RFCs, and long-form technical truth
   - repo-local `wiki/`: canonical authored source when a GitHub wiki is used
   - separate `*.wiki.git` clone: publish transport only, never a second authored source
12. When a repo has no GitHub wiki yet, create a local `wiki/` source set ready for later
   publication.
13. When the new documentation pattern changes Lotus-wide guidance, update the platform-owned skill
   inventory and routing guidance in the same slice.

## README Standard

Read [references/lotus-readme-wiki-standard.md](./references/lotus-readme-wiki-standard.md) before
drafting.

Every Lotus README should cover:

1. what the repo is,
2. what it owns and does not own,
3. how to start quickly,
4. which commands map to the validation lanes,
5. where the detailed docs and runbooks live.
6. repository layout, common commands, and runtime posture whenever the repo has enough surface
   area that omitting them would slow orientation.

The README must be:

1. truthful,
2. concise,
3. repo-type-aware,
4. command-accurate,
5. aligned to `REPOSITORY-ENGINEERING-CONTEXT.md`.

## Wiki Standard

Read [references/lotus-wiki-pages.md](./references/lotus-wiki-pages.md) before drafting.

The wiki should provide a stable operator and onboarding surface with:

1. `Home`
2. `Overview`
3. `Architecture`
4. `Getting Started`
5. `Development Workflow`
6. `Validation and CI`
7. `Operations Runbook`
8. `Security and Governance`
9. `RFC Index`
10. `Integrations`
11. `Roadmap`

Trim pages if the repo truly does not need one, but do not omit a page just because the current
repo docs are thin.

When a GitHub wiki exists, keep the authored pages in the main repository under `wiki/` and treat
any standalone local clone of the GitHub wiki repo as disposable publication plumbing.

## Repo-Type Adjustments

Apply the standard with repo-type-specific emphasis:

1. `product-ui`
   focus on product role, gateway dependency, live runtime validation, browser evidence, and the
   distinction between active supported surfaces versus legacy or capability-disabled routes
2. `experience-api`
   focus on client contract ownership, upstream dependency map, and cross-app payload shaping
3. `domain-service`
   focus on domain authority, upstream and downstream contracts, and repo-native gates
4. `shared-capability-service`
   focus on bounded capability seams, rollout posture, governance surfaces, and grouped public
   platform or control-plane APIs derived from the actual router layout
5. `platform-governance`
   focus on standards ownership, automation, and ecosystem-wide operational contracts

## Validation

After updating docs:

1. verify every command named in the README still exists,
2. verify linked files exist,
3. verify README and wiki section names match the repo role and current maturity,
4. verify that any grouped API or runtime surface descriptions match the current router and
   contract layout,
5. when documenting a shared-capability or AI service, distinguish capability-catalog truth from
   rollout-governed live execution or provider-allowlist truth,
6. when request conventions are mixed, verify that at least one wiki page contains executable
   examples using the currently supported query and body shapes,
7. when the repo has docs regression tests or public-doc contract tests, run the targeted pack after
   README or wiki changes and treat failures as contract drift until proven otherwise,
8. update repo-local engineering context when you discover that README/wiki changes are governed by a
   meaningful docs regression pack or another repeatable documentation constraint,
9. if repo-native checks regenerate artifacts such as OpenAPI snapshots or API vocabulary files,
   inspect the diff and avoid committing timestamp-only or otherwise non-semantic churn in a docs slice,
10. run any lightweight repo checks needed to confirm commands or paths if they were uncertain,
11. validate this skill with `quick_validate.py` after edits to the skill itself.

## Durable Guidance

When you establish or materially change the Lotus-wide README/wiki pattern:

1. keep this skill current,
2. update `lotus-platform/codex/skills/lotus-skill-manifest.json`,
3. update `lotus-platform/context/LOTUS-SKILL-ROUTING-MAP.md` when routing expectations change.
