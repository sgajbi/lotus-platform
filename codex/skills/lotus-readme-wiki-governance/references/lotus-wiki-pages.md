# Lotus Wiki Pages

Use this reference to seed a Lotus repo wiki or a local `wiki/` source set.

## Contents

1. [Purpose](#purpose)
2. [Standard Page Set](#standard-page-set)
3. [API Surface](#api-surface)
4. [Page Intent](#page-intent)
5. [Page Quality Rules](#page-quality-rules)
6. [Publication Notes](#publication-notes)

## Purpose

The Lotus wiki should be:

1. an onboarding surface,
2. an operator navigation layer,
3. a concise summary of repo truth,
4. a route into the detailed repo docs.

It should not become a second uncontrolled documentation tree.

Use the wiki for the material that is too detailed for the README but too important to bury inside
deep architecture or RFC documents.

## Standard Page Set

Create these pages unless the repo truly lacks the subject:

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
12. `_Sidebar`

Optional pages when the repo surface is large enough to justify them:

1. `API Surface`
2. `Platform Surfaces`
3. `Capability Packs`
4. `Troubleshooting`
5. `RFC Index` grouped by capability family rather than one flat list when the RFC estate is large

### API Surface

Summarize:

1. grouped public endpoints or route families,
2. current contract notes that are easy to get wrong,
3. copy-paste-ready request examples when query or request-body conventions are mixed,
4. links to deeper contract or OpenAPI material when present,
5. for product UIs, whether each route family is active, compatibility-only, or capability-disabled
   when route existence and supported product posture differ.

## Page Intent

### Home

Summarize:

1. repo role,
2. current phase,
3. quickest starting links,
4. most important commands,
5. page navigation.

### Overview

Summarize:

1. business role,
2. ownership boundaries,
3. upstream and downstream relationships,
4. current-state posture.

For platform-governance repositories, this page may also include concise ecosystem rationale for why
the platform layer exists, but it should still stay anchored to actual repo-owned automation,
standards, runtime support, and governance responsibilities.

### Architecture

Summarize:

1. major modules,
2. runtime shape,
3. critical seams,
4. execution flow or data flow when it is central to understanding the repo,
5. links to the detailed architecture docs.

### Getting Started

Summarize:

1. prerequisites,
2. install steps,
3. local run path,
4. health checks,
5. important environment or mode choices,
6. where to look first when startup fails.

### Development Workflow

Summarize:

1. common developer commands,
2. local working loop,
3. formatting, linting, tests,
4. repo-specific caveats.

### Validation and CI

Summarize:

1. lane model,
2. feature-lane commands,
3. PR-grade commands,
4. Docker or runtime parity,
5. evidence expectations,
6. what the important gates actually protect.

### Operations Runbook

Summarize:

1. health endpoints,
2. readiness semantics,
3. operational checks,
4. rollout or rollback highlights,
5. grouped operator-facing surfaces when the repo exposes many control-plane APIs,
6. links to full runbooks.

### Security and Governance

Summarize:

1. relevant governance posture,
2. security-sensitive seams,
3. production readiness caveats,
4. links to standards and local governance docs.

### RFC Index

Summarize:

1. major active RFCs,
2. what each RFC governs locally,
3. links to the canonical RFC docs,
4. grouping by capability family or maturity when the repo carries many RFCs.

### Integrations

Summarize:

1. who calls this repo,
2. which services it calls,
3. canonical URLs or identities when relevant,
4. the primary executable contract or contracts,
5. integration guides or contract docs.

### Roadmap

Summarize:

1. current phase,
2. delivered foundations,
3. intentional limitations,
4. next major milestones,
5. the difference between implemented bounded runtime and broader future-facing expansion.

## Naming

For a local source set intended for GitHub wiki publication:

1. use one file per page,
2. match page names closely, for example `Home.md` or `Validation-and-CI.md`,
3. include `_Sidebar.md` for navigation,
4. keep the source set inside the main repository under `wiki/` when possible,
5. treat any separate local clone of `*.wiki.git` as a publish target rather than a second editing
   location,
6. if a legacy live wiki cannot be checked out cleanly on Windows, publish through a bare clone
   instead of editing around the legacy filenames.

## Writing Rules

1. Keep each page concise.
2. Prefer summary plus links over duplication.
3. Keep page titles stable across repos where possible.
4. Use the same section order across repos unless a repo-type reason justifies a change.
5. Group large API estates by surface area derived from code, such as router prefixes or contract
   families, instead of presenting an unstructured endpoint dump.
6. Add light cross-links between pages so readers can move from overview to setup to operations to
   troubleshooting without returning to the sidebar every time.
7. Make `Home` a professional front door with audience-specific paths, repo role, evidence
   standard, common commands, and navigation.
8. Group `_Sidebar` navigation into sections when the page set is large enough. Typical sections
   are overview, product capabilities, engineering, operations, and governance.
9. Prefer concise tables for audience paths, capability matrices, quality-signal maps,
   first-response operations, and troubleshooting escalation details.
10. Keep supported-feature pages implementation-backed. Move planned capability, aspirational
    readiness, or unverified market language to roadmap or platform strategy material.
11. Long pages are acceptable when they are intentionally structured. Open long pages with current
    scope, evidence posture, and a reader map, decision matrix, evidence table, first-response
    matrix, or equivalent structure before detailed background.
12. Do not publish large raw command dumps. Group commands by purpose, name the gate or operating
    scenario each command proves, and link to the authoritative Makefile, runbook, script, or CI
    workflow for exhaustive command truth.
13. Review the rendered shape mentally before finishing: a wiki that is technically accurate but
    looks like unstructured notes is not ready for business, operator, or client-adjacent use.

## Professional Publication Checklist

Before treating a wiki source update as complete, verify:

1. `Home` works as a polished reader map with repository role, current maturity, evidence standard,
   common commands, and audience-specific paths.
2. `_Sidebar` is grouped when the page set is large enough, and the grouping matches the page
   purpose rather than the order files happened to be created.
3. Each page opens with the page purpose and current-state scope before detailed background.
4. Capability, operations, evidence, and quality-signal tables use stable column labels across the
   page set so readers can scan without relearning the structure.
5. Business, demo, sales, support, operations, and engineering readers can each find their
   decision-critical path without reading every page.
6. Unsupported, planned, degraded, or bounded-preview behavior is visible next to the claim it
   qualifies, not buried at the end of a long page.
7. Diagrams clarify system ownership, workflow, integration, or evidence flow; they do not replace
   implementation-backed text or duplicate deeper architecture documents.
8. Links route to implementation evidence, commands, RFCs, standards, contracts, runbooks, or
   authoritative docs.
9. No page includes scratch-note terms such as `TODO`, `maybe`, `rough`, `temp`, or unqualified
   "production-ready" language unless the wording is intentionally part of a roadmap, gap register,
   or current limitation.
10. Long pages expose current-state scope and an early reader, decision, evidence, support, route,
    governance, or quality-signal structure in the first screen.
11. Command-heavy pages use grouped command tables or short examples plus authoritative links
    instead of a single oversized fenced command block.

## Rendered Quality Pass

Run this pass whenever a user calls out poor formatting, weak professionalism, hard-to-scan wiki
pages, or stale publication quality.

1. Treat `Home.md`, `_Sidebar.md`, and every changed page as one reader journey, not isolated files.
2. Rework the first screen of `Home.md` until it gives repository role, current maturity, evidence
   posture, and audience paths without depending on a raw page list.
3. Make `_Sidebar.md` a grouped navigation aid when the page set has more than a small handful of
   pages. Use stable groups such as product, engineering, operations, and governance when they fit
   the repo.
4. Scan each changed page for first-screen purpose, current-state scope, clear next action, and
   visible limitations.
5. Replace wall-of-text explanations with narrow tables only when the table makes a decision faster.
   Split any table that requires horizontal scanning to understand one row.
6. For pages over a first-screen length, make sure current-state scope and reader structure appear
   before detailed background. If a reader cannot tell what decision the page supports from the
   first screen, polish the page before adding more content.
7. Replace long fenced command lists with a grouped command table and links to the authoritative
   Makefile, runbook, script, or workflow. Keep only short copy-paste examples in the wiki.
8. Verify every implementation-backed claim has an evidence path: code, command, generated
   artifact, test, RFC, runbook, scorecard, or supported-feature record.
9. Move unsupported, target-state, aspirational, or commercial claims into roadmap or limitations
   language before publication.
10. Check every changed intra-wiki link and make sure each changed page is reachable from `Home.md`
   or `_Sidebar.md`.
11. Record the wiki-quality evidence in PR notes: changed pages, reader audiences served, evidence
   anchors, limitations clarified, check-only result, and publish decision.

## Deterministic Audit

When a repo-local `wiki/` source changed, run:

```bash
python <lotus-platform>/codex/skills/lotus-readme-wiki-governance/scripts/audit_wiki_quality.py --wiki-dir <repo>/wiki --changed-page <Page.md>
```

Pass `--changed-page` once for each changed wiki page. Use `--all-professional-pages` only for an
explicit full-wiki polish campaign after legacy pages have been brought up to the professional
first-screen standard.

Use the audit as a structural quality gate before publication. Repo-wide checks cover failure modes
that make a wiki look unfinished even when the prose is directionally correct:

1. missing `Home.md` or `_Sidebar.md`,
2. pages that are not reachable from `Home.md` or `_Sidebar.md`,
3. broken local wiki links,
4. duplicate or missing H1 page titles,
5. bare URLs instead of named links,
6. scratch-note terms such as `TODO`, `maybe`, `rough`, `temp`, `TBD`, and `FIXME`.

Changed-page or all-page professional checks also cover:

7. long pages that do not state current scope or evidence posture near the top,
8. long pages that lack an early reader map, decision/evidence table, or equivalent first-screen
   structure,
9. oversized fenced command blocks that should be grouped by purpose and linked to authoritative
   command truth.

These checks are intentionally co-located with the skill as first-screen structure and command-dump
automation so documentation guidance and deterministic enforcement evolve together.

If the audit fails on legacy pages outside the changed scope, either include the cleanup in the
same polish slice or record the failure as an explicit follow-up with page names. Do not publish a
known-unprofessional wiki without a visible exception decision.
