# Platform Engineering Ledger

This ledger records cross-repository engineering lessons, recurring quality patterns, and important ecosystem fixes that future sessions should treat as already-learned knowledge.

## How To Use This Ledger

Add entries when a change reveals:

1. a repeatable quality failure,
2. a recurring architectural cleanup theme,
3. a cross-repo delivery pattern that should influence future work,
4. a governance or validation lesson that should not remain trapped in chat history.

Keep entries concise and operational.

## Current Ledger Entries

### 2026-07-22 | Canonical actor identities must be contract-owned by business purpose

Core #513 downstream proof found three nearby but non-interchangeable identities: the Advisor
Cockpit persona, the DPM command-center manager, and the advisor-book portfolio manager. Workbench
had a local advisor-book default, while the platform contract governed only the other two, so Core
seed automation could not persist the authoritative assignment required by the canonical proof.

Implication:

Keep each canonical actor identity in the central demo-data contract under its business purpose,
then make source seed automation and downstream validators consume that field. Do not reuse a
nearby persona to make a check pass, and do not promote source-confirmed tenant posture while the
tenant remains trusted caller context. Contract validators should lock identity, source lineage,
business-date policy, and the separately owned limitation before cross-repo implementation begins.
When a contract claims seed persistence, the Platform gate must execute a source-owned verifier that
uses the live seed builders and validate its structured evidence; contract strings and textual
source markers are not runtime proof.
Likewise, a ready membership input must not promote a composite Workbench panel beyond the
support state governed by its registry; panel certification reconciles every owned dependency and
limitation, not the strongest individual input.

### 2026-07-18 | Stateful cleanup and readiness must prove complete exact identity

Core #805 and PR #806 showed one defect family across seed cleanup, idempotency cleanup, and smoke
readiness: a hand-maintained child-table list omitted relationships, a logical event prefix differed
from the physical topic identity, and an existence wait could accept a different transaction.

Implication:

Future cleanup/reseed operations should derive or verify their dependency inventory against schema
metadata, run atomically, and fail closed. Readiness/replay must assert the exact governed resource
or work identity and durable outcome. Event cleanup must test logical-to-physical routing identity.
The versioned bank-readiness catalog owns the cross-app requirements; the fix-forward playbook owns
the repair sequence; backend delivery and discovery skills route to them. Concrete Core tables,
topics, and evidence remain in Core issue/review history rather than being copied centrally.

### 2026-07-18 | Agent guidance should route to one control authority, not copy it

Bank-readiness review exposed overlapping prose across the standing bank-buyable contract,
implementation guidance, skills, context, and potential app-local adoption documents. Repetition
made it harder to know which definition was authoritative and encouraged broad context loading.

Implication:

Keep stable `BR-NNN` definitions, applicability, evidence classes, and owner mappings only in the
versioned bank-readiness catalog. Context should explain ownership and routing; skills should define
the execution sequence and load applicable controls only; standards should explain outcomes and
evidence boundaries; wiki and app docs should link the authority and record local truth. Contract
tests should reject embedded duplicate control tables. A new skill is unnecessary while existing
issue-discovery, delivery, CI, skill-context, and pre-merge skills own the workflow stages.

### 2026-06-29 | Post-merge mainline proof must point to the merge SHA

`lotus-performance` PR #320 merged cleanly, but the latest automatic Main Releasability Gate was
not present for the merge commit. Manual dispatch proved the exact merged `main` SHA afterward.

Implication:

Future PR closure should query Main Releasability by merge SHA after syncing local `main`. If no
run exists and the workflow supports `workflow_dispatch`, dispatch it from `main`, monitor it, and
record the run URL. A green PR Merge Gate is not release evidence by itself for repositories with a
mainline releasability lane. No wiki source change is needed for this lesson because it is
agent-facing merge workflow guidance.

### 2026-06-28 | Skill improvements should follow measured agent failure patterns

Ongoing `lotus-performance` refactor work showed that future-agent quality improves when repeated
review, documentation, CI, and closure failures are promoted into the right durable control instead
of staying in chat memory.

Implication:

Future Lotus slices should run an explicit guidance review before closure. If the work reveals a
repeatable agent failure mode, update the platform-owned skill source, routing map, context,
scaffold, evaluator case, or deterministic gate that will prevent the same failure. If it does not,
record a short no-skill/no-context/no-doc/no-wiki decision in PR evidence, the scorecard, or the
review ledger. Deployed local Codex skills are sync targets, not authoritative source.

### 2026-06-28 | Test-family breadth can be a CI gate when total test count hides proof loss

`lotus-performance` PR #309 promoted a deterministic test taxonomy inventory from report-only
measurement to a blocking evaluation gate. The useful signal was not total test count; it was the
minimum API/runtime and contract/governance test-family breadth, plus a ceiling on uncategorized
test growth.

Implication:

Future CI-hardening work should inspect whether stable test-family or proof-breadth inventories can
block agent-driven regression before relying on total collected tests. A good promotion names the
baseline artifact, exact failure mode, repo-native command, lane placement, exception policy,
pass/fail tests, and scorecard or review-ledger update.

### 2026-06-22 | Missing auto-merge token should skip helper, not fail PR quality

`lotus-idea` PR #63 showed that a `pull_request_target` auto-merge helper that exits red when
`LOTUS_AUTOMERGE_TOKEN` is absent can block or obscure an otherwise green PR Merge Gate, even when
the repository intentionally falls back to a human or release actor for rebase merge.

Implication:

Future generated backend services should still require a non-`GITHUB_TOKEN` merge actor for
automatic rebase merge, but missing-token behavior should warn and skip auto-merge rather than
creating a permanent red helper check. The PR Merge Gate remains the quality signal; the helper is
only queueing automation.

### 2026-07-05 | Green PRs can still be blocked by unsigned commits

`lotus-core` PR #703 and sibling Lotus PRs showed the same branch-protection failure mode: all
required checks were green and auto-merge was enabled, but `mergeStateStatus=BLOCKED` because the
repositories require signed commits, linear history, and rebase merge while the feature branches
contained unsigned commits.

Implication:

Future PR work must inspect branch protection before opening or pushing merge intent. If signed
commits are required, agents must configure a registered signing key and verify every branch commit
with `git log --format='%h %G? %s' <base>..HEAD` before relying on CI or auto-merge. A green PR that
is still blocked should be diagnosed with `gh api .../branches/<base>/protection` and
`gh api .../commits/<head-sha> --jq .commit.verification`; unsigned branches should be re-signed and
force-with-lease pushed, not admin-merged or merged after weakening protection.

### 2026-04-11 | Canonical local runtime must be treated as a governed operator flow

The local Lotus bring-up path only became repeatable once:

1. direct ingress, managed host mappings, and canonical service addresses were treated as one governed system,
2. startup and teardown were scripted rather than improvised,
3. seeded data validation was included as part of the runtime contract,
4. UI validation checked real screens and sub-screens rather than only health endpoints.

Implication:

Future runtime or demo work should use canonical automation and validation instead of hand-built service startup sequences.

### 2026-04-11 | Front-office product proof must route through the governed workbench runtime

The ecosystem already has a governed front-office runtime under `lotus-workbench` for:

1. seeded `PB_SG_GLOBAL_BAL_001` data,
2. canonical `*.dev.lotus` product routing,
3. populated Workbench surface validation,
4. demo and screenshot evidence capture.

Implication:

Future agent and operator guidance must route front-office bring-up, panel validation, and screenshot work to the governed `lotus-workbench` runtime instead of improvising from `lotus-platform/platform-stack`.

### 2026-04-11 | CI should use GitHub for heavy execution, not repeated expensive local reruns

RFC-0072 rollout work demonstrated that productivity improves when:

1. local checks are targeted and truthful,
2. GitHub Actions carries the expensive full matrix,
3. PRs are raised early,
4. failures are fixed forward from GitHub logs asynchronously.

Implication:

Future work should prefer targeted local proof plus GitHub-backed heavy execution rather than blocking on repeated full local reruns.

### 2026-04-11 | Platform standards become durable only when backed by scaffold and validators

Standards such as CI lane structure, workflow permissions, action baselines, repository hygiene, and container build rules were only durable once they were backed by:

1. scaffold templates,
2. validators,
3. documentation contract tests,
4. platform-owned repo checks.

Implication:

When a pattern matters ecosystem-wide, do not stop at prose. Promote it into executable truth where practical.

### 2026-04-18 | README and wiki quality improves when mixed API conventions are shown, not merely described

Cross-repo README and wiki rollout work showed that short prose warnings are not enough when a repo
still exposes mixed query names, compatibility aliases, or transitional request-body shapes.

The documentation became materially safer once:

1. the README stayed concise and delegated detailed examples into the repo-local `wiki/`,
2. the wiki remained the canonical authored source inside the main repository,
3. API-surface pages included copy-paste-ready examples for the currently supported parameter shapes,
4. repo-local engineering context explicitly called out this documentation requirement where it
   mattered.

Implication:

Future README/wiki work should add executable examples for mixed public contracts and keep that rule
in the platform documentation skill, not only in one repo.

### 2026-04-18 | Product-UI docs must separate active surfaces from legacy or capability-disabled routes

Workbench documentation tightening showed that route inventories can easily drift into historical
topology instead of current product truth.

The documentation became materially more truthful once:

1. active supported surfaces were stated explicitly,
2. compatibility redirects were called out as compatibility-only instead of live product ownership,
3. capability-disabled shell entries were not described as active routes simply because the labels
   still exist in the shell model,
4. canonical runtime examples used the governed seeded portfolio and validation output paths.

Implication:

Future README/wiki work for product UIs should document supported surfaces, compatibility routes,
disabled navigation entries, and canonical evidence paths separately.

### 2026-04-18 | Legacy Lotus wiki material should be mined by ownership boundary before reuse

Reviewing the older `lotus-core` wiki showed that legacy Lotus documentation can contain useful
business framing, market context, and platform rationale even when its repo ownership and technical
topology are outdated.

The documentation became safer once:

1. historical pages were treated as source material instead of as a direct structure template,
2. reusable ecosystem background was separated from current repo truth,
3. stale service-specific or legacy-naming material was not copied into platform-governance docs,
4. rewritten docs used current Lotus vocabulary, architecture, and ownership boundaries.

Implication:

Future README/wiki work should classify legacy material into current repo truth, ecosystem
background, migrated ownership, or retirement before reusing it.

### 2026-04-18 | Cross-cutting investor and GTM narrative belongs in lotus-platform when it survives repo splits

Older Lotus wiki material showed that investor pitch, sales FAQ, and GTM pages can contain useful
ecosystem narrative even when they are misplaced under one application repository.

The documentation became more coherent once:

1. commercial framing that still described the wider Lotus ecosystem was moved to `lotus-platform`,
2. the content was rewritten in current Lotus language instead of old PAS or single-repo language,
3. platform docs kept commercial framing at the level of positioning, packaging, and adoption
   posture rather than repo-local feature claims,
4. detailed pricing mechanics stayed high-level unless explicitly requested.

Implication:

Future Lotus documentation cleanup should move surviving cross-cutting investor, sales, and GTM
material into the platform-governance layer when it no longer belongs to one application repo.

### 2026-04-18 | Cross-cutting business and moat pages should be rewritten around Lotus operating value, not copied from stale service mechanics

Continuing the platform commercial-doc cleanup showed that historical strategy pages often mix a
useful business point with outdated single-repo implementation detail, stale competitor framing, or
hard numeric claims that are not part of current validated repo truth.

The documentation became more durable once:

1. cross-cutting benefits, moat, and positioning pages were rewritten in current Lotus ecosystem
   language,
2. old service-by-service mechanics were replaced with operating-model value such as governance,
   bounded ownership, reusable automation, supportability, and validated delivery,
3. stale or unverifiable market-size and competitor-detail claims were not copied forward unless
   they were intentionally refreshed from current source material.

Implication:

Future platform-level commercial documentation should translate durable business meaning into current
Lotus operating value instead of preserving brittle historical specifics.

### 2026-04-18 | Market-position pages should prefer evergreen structure over stale market statistics

The next documentation pass showed that old market-landscape pages often carry dated CAGR, market
size, named-customer, or competitor-specific claims that become unreliable faster than repo docs are
maintained.

The documentation became more truthful once:

1. market framing focused on buyer pain, operating constraints, and adoption direction,
2. Lotus positioning was explained through current architecture and operating model,
3. hard market or competitor claims were omitted unless they were intentionally refreshed from
   current source material.

Implication:

Future market-position or commercial wiki pages should default to evergreen structural framing and
avoid brittle point-in-time claims unless fresh sourcing is part of the slice.

### 2026-04-18 | Large deep-doc trees need an explicit index or README to stay usable

Documentation cleanup across `lotus-platform` and `lotus-core` showed that a strong README and wiki
are still not enough when the deeper `docs/` tree becomes broad and flat.

The documentation became materially easier to use once:

1. the front-door docs stayed concise,
2. a deep-doc index was added where the detailed architecture set had grown too large to browse
   casually,
3. repo-local engineering context named that deep-doc index as a real navigation surface,
4. the platform repo carried an explicit documentation-layering document instead of leaving the
   split between README, wiki, docs, and context implicit.

Implication:

Future Lotus documentation work should add or refresh deep-doc indexes when the detailed document
set is broad enough that readers would otherwise scan a flat directory or a bloated README.

### 2026-04-18 | README/wiki cleanup needs an explicit anti-duplication and publish-hygiene rule

Recent cross-repo wiki work showed two recurring failure modes:

1. new pages were easy to create even when the right move was to tighten an existing nearby page,
2. GitHub wiki publication could unintentionally carry other pending repo-local `wiki/` edits if
   the authored-source diff was not checked first.

The documentation workflow became safer once:

1. the platform layering guidance explicitly told agents to scan adjacent README, wiki, and deep-doc
   pages before creating a new document,
2. the README/wiki governance skill explicitly told agents to prefer consolidation over parallel
   pages,
3. publication guidance treated the repo-local `wiki/` diff as a required pre-publish check.

Implication:

Future Lotus documentation work should reduce overlap first, add pages only for real navigation or
ownership boundaries, and verify the authored wiki diff before publishing to GitHub.

### 2026-07-19 | Branch policy names must be proved against emitted workflow contexts before reconciliation

A protected-branch audit found that repository-specific container jobs had evolved while the
central governance policy retained a generic retired name. Comparing policy only with live branch
settings could report that stale agreement as healthy or allow enforcement to remove a newer check.

The governance flow became safer once:

1. required contexts were compared with current default-branch workflow job names,
2. matrix job names were expanded using active axes and exclusions,
3. external providers required explicit non-empty declarations,
4. validation and enforcement could be scoped to named repositories,
5. source-only validation ran before any reconciliation plan or mutation.

Implication:

Future required-check changes must update workflow source, durable policy, regression evidence, and
live protection as one issue-backed lifecycle. A green live setting is insufficient if current
source cannot emit the required context.
