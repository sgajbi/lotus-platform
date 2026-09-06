# Lotus Documentation Layering

This document defines how Lotus documentation should be split across the main documentation surfaces.

It exists to keep `README.md`, repo-local `wiki/`, deep `docs/`, and platform `context/` aligned
without turning them into overlapping prose silos.

## Purpose

Lotus repositories now carry several documentation surfaces because they serve different readers and
different time horizons.

Without an explicit split, the same content tends to drift across:

1. repo front doors,
2. operator wiki pages,
3. deep technical documents,
4. platform context and agent guidance.

This document defines the intended split for Lotus repositories and the stronger platform posture
for `lotus-platform`.

## Documentation Surface Model

Each subject has one authoritative home. Other surfaces summarize and link.

| Surface | Responsibility | Must not become |
| --- | --- | --- |
| `README.md` | Product introduction, capability summary, one quickstart, and reader navigation | An operating manual or implementation diary |
| `AGENTS.md` | Tool-neutral mandatory operating rules and progressive discovery entry | Repository-specific architecture or incident history |
| `CLAUDE.md` | Thin Claude adapter pointing to `AGENTS.md` and repository context | A second policy or context source |
| `REPOSITORY-ENGINEERING-CONTEXT.md` | Current local ownership, architecture, boundaries, commands, constraints, and task routes | A changelog, PR ledger, or duplicate documentation tree |
| `docs/` | Detailed contracts, architecture, methodology, standards, and procedures | A collection of uncategorized status notes |
| `wiki/` | Concise onboarding and operator navigation derived from repo-authored source | Hand-edited publication-only truth |
| GitHub issues and task ledgers | Active work, temporary blockers, PR state, and execution evidence | Durable architecture or operating policy |

### `README.md`

Use the README as the fast truthful front door.

It should answer:

1. what the repository is,
2. what it owns and does not own,
3. how to start quickly,
4. which commands map to the active validation lanes,
5. where the deeper docs live.

The README should stay concise. It should orient quickly and route deeper rather than absorbing
long-form architecture, operations, or market narrative.

### repo-local `wiki/`

Use `wiki/` for onboarding and operator navigation.

It should:

1. summarize repository purpose and boundaries,
2. group the major system surfaces in a way a new engineer or operator can browse,
3. provide short runbook and troubleshooting guidance,
4. link into deeper docs where precision matters,
5. stay grounded in current repository truth.

For repositories that publish a GitHub wiki, the repo-local `wiki/` directory is the canonical
authored source. The separate `*.wiki.git` repository is publication transport only.

### deep `docs/`

Use `docs/` for detailed technical truth.

That includes:

1. architecture documents,
2. runbooks,
3. standards,
4. methodology documents,
5. review ledgers,
6. RFC implementation evidence,
7. long-form technical guidance that would overwhelm the README or wiki.

The deep docs layer should hold the durable detailed explanation. README and wiki should link to it
instead of restating it at length.

### platform `context/`

Use `context/` for cross-repository platform truth and governed working guidance.

That includes:

1. ecosystem roles,
2. reading order,
3. skill routing,
4. task routing,
5. playbooks,
6. machine-readable registries and contracts.

`context/` is not a generic document dump. It is the governed memory layer for reusable Lotus
engineering truth.

## Progressive Loading

Every repository should make the smallest safe path obvious:

1. read `AGENTS.md`, the Lotus quickstart, the repository context, and the skill-routing map,
2. identify the repository's purpose, owning boundary, applicable skill, and default validation,
3. follow repository-context task routes to only the relevant contract, standard, RFC, or runbook,
4. load broad ecosystem history only when ownership, architecture, or recovery genuinely requires it.

Essential controls remain explicit in `AGENTS.md`; progressive loading must never hide a mandatory
security, financial-correctness, review, or release rule in an optional document.

## Portable Discovery

Use repository-relative paths inside a repository. Cross-repository references should use either:

1. `<workspace-root>/lotus-platform/...` when describing a local sibling checkout, or
2. a canonical `https://github.com/sgajbi/<repository>/blob/main/...` link when the document must
   work without sibling repositories.

Define placeholders such as `<workspace-root>` and `<temp-dir>` before using them. Do not publish
personal usernames, drive letters, checkout directories, or local temporary paths as reusable
instructions. Immutable historical evidence may name the environment in which it ran only when
that provenance is material; provide a portable repository-relative or canonical link alongside it.

`AGENTS.md` is the shared, tool-neutral entry. A repository may add a thin `CLAUDE.md` that points
to `AGENTS.md` and local context, but it must not copy policy. Tool/runtime instruction precedence
is controlled by that runtime; Lotus documentation defines its own authority without claiming to
override system, organization, or user instructions.

## Fresh-Start Check

Before adopting a changed convention, start with only the documented repository entry and verify
that a new reader can identify:

1. product purpose and ownership,
2. mandatory Lotus rules and instruction precedence,
3. the applicable skill and task-specific source,
4. the default local validation and required GitHub evidence,
5. merge, wiki-publication, and hygiene completion requirements.

Record the checked paths and any genuinely unverified tool behavior in the PR. Do not fill gaps
with assumptions about a particular agent or workstation.

## Layering Rules

Keep these rules explicit:

1. do not duplicate central platform policy prose into every repository,
2. do not make the wiki a second `docs/` tree,
3. do not put deep architecture detail into the README unless it changes the fast-start contract,
4. do not leave ecosystem-level narrative trapped inside one application repository when it clearly
   belongs to `lotus-platform`,
5. do not use stale legacy wiki pages as current truth without reclassification,
6. do not create a new page when a nearby README, wiki page, or deep doc can be tightened instead.

Before adding a new document, scan the adjacent `README.md`, `wiki/`, and relevant `docs/` folder
for overlap. Prefer consolidating or sharpening an existing page when the new content would mostly
repeat structure that already exists.

## `lotus-platform` Specific Posture

`lotus-platform` carries one extra responsibility: some documentation here is cross-cutting
ecosystem narrative rather than repository-local implementation detail.

That means:

1. ecosystem-level business framing, GTM mechanics, investor narrative, and sales positioning can
   live here when they genuinely describe Lotus as a platform,
2. those pages must still be grounded in actual Lotus architecture, repository boundaries, and
   current delivery posture,
3. they must not claim market-size figures, competitor assertions, or customer numbers unless those
   claims are freshly revalidated,
4. application-specific product promises should stay in the owning repository.

## Migration Rule For Legacy Material

When older wiki or strategy material is discovered:

1. classify what is still current repository truth,
2. classify what is now ecosystem-level Lotus truth,
3. classify what is stale and should be retired,
4. rewrite durable signal in current Lotus language before publishing it again.

Use a migration ledger when that classification work is broad enough that future agents should not
have to rediscover it.

## Practical Authoring Rule

When updating Lotus docs, use this order:

1. update the deep truth first when the change affects architecture, operations, or standards,
2. update the README to reflect the front-door summary if the repo contract changed,
3. update `wiki/` to keep onboarding and operator navigation aligned,
4. update `context/` only when the change is platform-wide or should become durable guidance for
   future work.

If the repository publishes a GitHub wiki, finish by checking whether the repo-local `wiki/`
changes should be synchronized to the live wiki immediately or batched with other pending authored
wiki changes.

## Related References

1. [Lotus Engineering Context](../../context/LOTUS-ENGINEERING-CONTEXT.md)
2. [Context Reference Map](../../context/CONTEXT-REFERENCE-MAP.md)
3. [Lotus Developer Onboarding](../onboarding/LOTUS-DEVELOPER-ONBOARDING.md)
4. [Lotus Agent Ramp-Up](../onboarding/LOTUS-AGENT-RAMP-UP.md)
5. [Platform Surfaces](../../wiki/Platform-Surfaces.md)
