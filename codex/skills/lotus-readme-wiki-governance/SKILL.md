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
4. Scan the existing `README.md`, `wiki/`, and relevant `docs/` subtree for overlapping pages
   before adding a new one:
   - prefer tightening an existing page when the new content would mostly duplicate structure
   - merge or retire near-duplicate wiki pages instead of letting both survive
   - use new pages only when there is a real navigation or ownership boundary
5. Before a major README rewrite, check whether the repo already has docs regression tests or
   public-contract tests that pin README or guide language. Search the test tree for `README.md`,
   key guide paths, or `docs` contract test packs so you preserve governed public truth instead of
   deleting required contract language accidentally.
6. Before adding, moving, restoring, or closing durable documentation truth, run stranded-truth
   reconciliation for unmerged branches that touch `README.md`, `wiki/`, `docs/rfcs/`, repo
   context, AGENTS.md, contracts, standards, or supported-features material. A page or ledger that
   exists only on an unmerged side branch is not governed truth.
7. When the repository has been split, renamed, or re-scoped, scan current operator-facing evidence
   docs such as `docs/demo/`, manual-validation notes, and runbooks for stale service names, image
   names, ingress identities, and command targets.
8. When a repository has older wiki or strategy material with useful historical signal, mine it as
   source material instead of copying its structure blindly. Classify what remains current repo
   truth, what has become ecosystem background, what now belongs in another Lotus repository, and
   what should be retired.
9. When the harvested legacy material is broad enough that future cleanup would otherwise repeat the
   same classification work, create a durable migration ledger page or doc so later agents can reuse
   the disposition instead of re-triaging the same historical pages.
10. Preserve repo truth. Do not invent maturity, ownership, runtime support, or production readiness.
11. Keep the README short enough to orient a new engineer quickly. Route to deeper docs instead of
   copying them.
12. Keep the wiki operator- and onboarding-focused. It should summarize, organize, and link; it
    should not become an unbounded duplicate of `docs/`.
13. For business applications, make the wiki useful beyond developers:
   - business users should understand the product role, feature behavior, and operating model,
   - sales and marketing should understand implementation-backed value propositions and demo
     stories without target-state overclaim,
   - operations should understand runtime posture, supportability, upstream/downstream dependencies,
     degraded states, monitoring, and escalation paths,
   - engineers should have links to APIs, contracts, tests, RFCs, and runbooks.
   Include diagrams where they clarify flows, upstream and downstream integrations,
   feature behavior, functional capability groupings, or non-functional posture.
14. When a repo exposes mixed request conventions, compatibility aliases, or easy-to-confuse query
   shapes, include copy-paste-ready request examples in the wiki so future agents and operators do
   not silently document the wrong contract.
15. For product-UI repositories, distinguish active supported surfaces from compatibility routes,
   disabled navigation entries, and target future topology. Do not treat every historical route or
   shell label as an active product commitment.
16. For platform-governance repositories, keep ecosystem narrative subordinate to repo truth: use
   business or market framing only when it clarifies why the platform exists, never as a substitute
   for actual automation, standards, and runtime ownership.
17. When users explicitly want investor, sales, or GTM material preserved, rewrite it as
   ecosystem-level platform narrative under the platform-governance repository instead of leaving it
   stranded inside one application repo. Keep numeric pricing and deal-specific terms high-level
   unless the user explicitly asks for detailed commercial mechanics.
18. When legacy commercial or strategy pages contain stale implementation mechanics, dated vendor
   comparisons, or unverified market-size numbers, translate the durable business meaning into
   current Lotus ecosystem language instead of copying the old claims forward. Prefer operating-model
   value, ownership clarity, delivery leverage, and supportability posture over brittle legacy
   specifics.
19. Do not carry forward hard market-size figures, CAGR claims, named-customer adoption numbers, or
   competitor assertions unless they are freshly verified for the current date. For evergreen repo
   wiki pages, prefer structural market forces, buyer pain, and Lotus positioning over brittle
   point-in-time statistics.
20. Use this content split:
   - `README.md`: fast repo truth, top-level contracts, commands, and navigation
   - wiki: onboarding flow, operator maps, grouped surface explanations, and runbook summaries
   - deep docs under `docs/`: detailed architecture, standards, RFCs, and long-form technical truth
   - repo-local `wiki/`: canonical authored source when a GitHub wiki is used
   - separate `*.wiki.git` clone: publish transport only, never a second authored source
21. When a repo has no GitHub wiki yet, create a local `wiki/` source set ready for later
   publication.
22. If the user asks to publish, mirror the repo-local `wiki/` source into the GitHub wiki rather
   than editing the GitHub wiki clone directly. Treat publication as a synchronization step, not as
   a second authoring workflow.
23. Before publishing, check the repo-local `wiki/` diff so you understand whether the publish will
    carry only the intended slice or also other pending authored wiki edits.
24. When the existing GitHub wiki contains legacy filenames that are not Windows-safe, or checkout
   fails because of old characters such as `:`, use a bare clone publication path instead of
   mutating the repo-local `wiki/` source or skipping the publish.
25. When replacing a legacy wiki with the current governed page set, preserve durable business or
   operator signal by migrating it into grounded Lotus language first; then retire the stale page
   names from the live wiki.
26. When the new documentation pattern changes Lotus-wide guidance, update the platform-owned skill
   inventory and routing guidance in the same slice.

## Durable Documentation Controls

For durable documentation artifacts such as RFC ledgers, supported-features pages, RFC indexes,
source maps, context files, API inventories, or wiki roadmap pages:

1. add an index reference from the nearest stable navigation page,
2. add or update a regression/current-state test when the repo has a docs test pack,
3. record whether wiki source should change or explicitly state why no wiki change is needed,
4. publish the wiki after merge when repo-local wiki source changes,
5. delete or classify any branch that used to contain the only copy of the restored truth.

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
Read [references/github-wiki-publication.md](./references/github-wiki-publication.md) when the task
includes publishing.

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
12. `Supported Features` when a product or service has implementation-backed feature claims that
    business, operations, or demo teams need to trust.

For business applications, the wiki should also include:

1. a current-state functional capability matrix,
2. a current-state non-functional capability matrix,
3. upstream and downstream integration diagrams,
4. feature-flow diagrams for the main product workflows,
5. explicit target-state roadmap material separated from implemented support,
6. demo-preparation notes that identify which claims are implementation-backed.

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
