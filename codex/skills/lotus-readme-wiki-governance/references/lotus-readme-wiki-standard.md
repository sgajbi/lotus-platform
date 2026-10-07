# Lotus README Standard

Use this reference to draft or refresh a Lotus repository `README.md`.

## Contents

1. [Goals](#goals)
2. [Required Structure](#required-structure)
3. [Writing Rules](#writing-rules)
4. [Source-of-Truth Hierarchy](#source-of-truth-hierarchy)
5. [Common README Patterns](#common-readme-patterns)

## Goals

The README is the shortest truthful entry point for a repo. A strong Lotus README should answer:

1. what this repository is,
2. why it exists in the Lotus ecosystem,
3. what it owns and does not own,
4. how to run and validate it,
5. where to go for deeper docs.

The README is not the place to explain every route, every rollout seam, or every operational check.
Its job is to orient quickly and route the reader to the right deeper page.

## Required Structure

Use this section order unless the repo type needs a minor adjustment:

1. title and one-sentence role summary
2. repository-local engineering context pointer
3. purpose and scope
4. ownership and boundaries
5. current phase or operational posture
6. architecture at a glance
7. repository layout
8. quick start
9. common commands
10. validation and CI lanes
11. integration boundaries
12. operations and runtime posture
13. documentation map
14. wiki source or wiki link when present

## Writing Rules

1. Prefer short paragraphs and flat bullets.
2. Use exact commands from the repo, not generic placeholders.
3. Prefer links to detailed docs over copying long architecture prose into the README.
4. Keep platform-wide policy in platform docs; only summarize what the repo needs locally.
5. Use domain-correct Lotus vocabulary.
6. Do not oversell maturity. Say when a capability is bounded, staged, disabled by default, or not
   production-ready.
7. Keep the README focused on the repo's front door:
   - role
   - ownership boundaries
   - current posture
   - quick start
   - validation commands
   - where to go next
8. For large API estates, summarize the surface in groups rather than listing every endpoint unless
   the current product depends on a short fixed set.
9. When a service has mixed request conventions or compatibility aliases, point the reader to a
   wiki page with executable examples rather than trying to explain the entire nuance inline.
10. When a repository has a large or flat deep-doc tree, add or refresh a docs index so the README
   and wiki can route readers into the deep material without dumping a long unstructured link list
   into the front door.

## Source-of-Truth Hierarchy

Use this split consistently:

1. `README.md`
   the fastest truthful repo entrypoint
2. repo-local `wiki/`
   the canonical authored source for onboarding and operator navigation across the repo's major
   surfaces
3. `docs/`
   detailed architecture, standards, RFCs, methodology, and runbook source material
4. standalone `*.wiki.git` clone when used
   publication transport for the live GitHub wiki, not a second authored source

If the live GitHub wiki carries legacy filenames that are not Windows-safe, use a bare-clone
publication path rather than treating the legacy file naming as the standard.

Do not let the README become a second wiki, and do not let the wiki become a second `docs/`
tree.

## Repo-Type Adjustments

### Product UI

Emphasize:

1. gateway-first contract,
2. canonical runtime and live validation,
3. browser evidence expectations,
4. major app areas.

### Experience API

Emphasize:

1. client-contract ownership,
2. upstream dependency map,
3. canonical service identity,
4. cross-app contract impact.

### Domain Service

Emphasize:

1. domain authority,
2. upstream and downstream consumers,
3. repo-native lane commands,
4. contract and migration governance.

### Shared Capability Service

Emphasize:

1. bounded capability seams,
2. rollout posture,
3. governance and evidence surfaces,
4. clear non-ownership of business domain truth,
5. major public or operator-facing surface groups derived from actual routers and contracts.

### Platform Governance

Emphasize:

1. standards ownership,
2. automation entrypoints,
3. ecosystem-wide role,
4. bootstrap and sync expectations.

## Publication Link And Prose Classification

Named links to existing local wiki pages may use the page name with or without `.md`.
Resolve that wiki page before considering a same-named repository directory. Missing pages,
parent/root-relative escapes and repository-relative file links remain failures. Repository files
use owning-repository `blob/main/<path>` or `tree/main/<path>` URLs, matching the local file/directory
type and staying inside the checkout.

Owning-repository GitHub evidence citations retain their native URL shape: numbered Actions runs
and jobs, named YAML workflows, numbered issues/pull requests (including files/commits/checks),
commit hashes, releases/latest/tag and compare ranges. Validate route shape and repository identity;
do not require `blob/main` for evidence. This is a syntax check, not proof that a remote run, issue,
commit or release exists. Malformed or unknown routes do not bypass file-link controls.

The prose classifier admits individual technical noun phrases `temporary relation(s)`,
`temporary table(s)`, and OS `temporary directory`/`temporary directories` on one line.
It still rejects `TODO`, `TBD`, `FIXME`, `temp notes`, `temporary workaround`,
`maybe implement later`, and these noun phrases immediately followed by `notes` or `workaround`.
For directory phrases, any same-line punctuation or Markdown delimiter run before `notes` or
`workaround` also remains scratch prose. This includes emphasis, inline code, strikethrough,
quotes and escaped formatting, including incomplete wrappers. Delimiters never cross CR/LF
line boundaries. Technical punctuation such as `temporary directory, with mode 0700` remains
valid. Database phrase grammar is unchanged. Underscore closing delimiters are recognized
without treating an identifier such as `notes_directory` as that noun.
Formatted technical descriptions such as `temporary directory: **mode 0700**` remain valid.
Directory qualifier classification renders only the remainder of the noun's raw CR/LF-bounded
line with the standard HTML parser: inline tags, attributes and comments do not supply prose,
while named/numeric character references supply their decoded text. The explicit local boundary
set follows [WHATWG default rendering](https://html.spec.whatwg.org/multipage/rendering.html#flow-content)
for flow/page/section/list and text-bearing table layout, plus `br`:
`address article aside blockquote body br caption center dd details dialog dir div dl dt
fieldset figcaption figure footer form h1 h2 h3 h4 h5 h6 header hgroup hr html legend li
listing main menu nav ol p plaintext pre search section summary table tbody td tfoot th
thead tr ul xmp`. Both start and end tags in this set supply a local line boundary.
Inline phrasing tags, hidden names such as `base`, `link`, `param`, `title`, and column metadata
`col`/`colgroup` do not supply boundaries; CommonMark HTML-block syntax is not this policy.
Backslash-escaped angles and complete inline-code contents
remain literal, including entity syntax; decoded literal markup is not reparsed as tags.
This lexical convention is not a complete browser rendering guarantee. CSS overrides,
visibility/open state, sanitizer transformations, HTML5 tree repair/raw-text behavior,
JavaScript and arbitrary Markdown rendering are outside its scope.
A legitimate technical term never exempts other scratch-note occurrences
in the same sentence or page. Fenced executable examples remain outside prose checks.
Base prose, navigation and link checks apply wiki-wide; changed-page scope selects only the
stricter professional first-screen and command-dump checks. Auditor failures propagate CLI exit 1.

## Anti-Patterns

Avoid:

1. marketing copy,
2. stale endpoint inventories unless the repo truly depends on a short current list,
3. duplicated RFC prose,
4. local-machine-specific paths,
5. giant historical narrative at the top of the file,
6. claiming production readiness by implication,
7. dumping every router or endpoint into the README when a grouped surface summary belongs in the
   wiki.
