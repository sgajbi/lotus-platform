# Named-Success Endpoint-Family Closure

## Contents

1. [Purpose](#purpose)
2. [Quality Bar](#quality-bar)
3. [Intake And Goal Alignment](#intake-and-goal-alignment)
4. [Authority And Runtime Boundaries](#authority-and-runtime-boundaries)
5. [Contract Implementation](#contract-implementation)
6. [Behavior And Enforcement Evidence](#behavior-and-enforcement-evidence)
7. [Documentation And Product Truth](#documentation-and-product-truth)
8. [Validation, GitHub, And Closure](#validation-github-and-closure)
9. [Failure Patterns To Reject](#failure-patterns-to-reject)

## Purpose

Use this reference when one endpoint or a related caller/source endpoint family can return multiple
successful business outcomes and the work must publish exact named OpenAPI examples for every
mode. Typical outcomes include created, blocked, suppressed, not eligible, accepted, replayed, or
duplicate posture.

The objective is executable contract truth. A parseable schema, one happy-path example, a large
test count, or a green PR check is not enough by itself.

## Quality Bar

Every family slice should:

1. improve readability, modularity, and repository organization;
2. use meaningful tests and deterministic gates that reject superficial or stale output;
3. produce audience-aware documentation backed by implementation evidence;
4. preserve domain and source authority using precise private-banking language;
5. promote repeatable lessons into skills, context, automation, scaffolds, or validators;
6. use GitHub and CI efficiently, with focused proof before expensive lanes;
7. make measurable progress toward the active goal without widening scope casually;
8. leave enterprise-grade, production-ready, bank-buyable truth, including explicit blockers.

## Intake And Goal Alignment

Before editing:

1. Re-read the active goal, governing RFC slice, focused issue, and current mainline truth.
2. Record the exact repository, base SHA, branch, parent issue, focused issue, endpoint paths,
   source product identifiers, and intended validation lane in durable evidence.
3. Search open and closed issues for the endpoint paths, response model, operation IDs, and domain
   vocabulary. Create a focused issue before editing when no current issue owns the gap.
4. Fetch and prune remotes, inspect branches not merged to `origin/main`, and reconcile any branch
   that touches durable RFC, docs, wiki, context, contract, migration, or CI truth.
5. Run a deterministic pre-change inventory of multi-shape successful operations. Record the
   method, path, executable modes, currently published named modes, and remaining family count.
6. State the blocker codes cleared and preserved. A contract-hardening slice must not claim live
   source, deployment, production, Gateway, Workbench, mesh, publication, or supported-feature
   readiness unless that evidence is actually in scope.

Repeat the goal check after handover or context compaction, before PR/merge, and before selecting the
next family. Store changed decisions in the issue, RFC/context, or governed task ledger instead of
depending on conversational memory.

## Authority And Runtime Boundaries

For every family:

1. name the authoritative source service and governed source product or contract;
2. state what the owning service calculates or approves and what the endpoint service merely
   evaluates, suppresses, classifies, or projects;
3. preserve source product identity and source-safe lineage without exposing raw routes, payloads,
   content hashes, secrets, or diagnostics;
4. keep caller-supplied and source-backed operations as separate public capability contracts even
   when they share internal assembly;
5. prefer internal domain/application/port/adapter modularity inside the existing deployable;
6. do not introduce a new runtime service unless scaling, ownership, data, failure isolation,
   deployment, or security-boundary evidence justifies it.

## Contract Implementation

Use one capability-owned deterministic example factory per family:

1. construct the production request DTO or source command;
2. execute the real request-to-command and application use case;
3. for source-backed examples, replace only the source port with a deterministic fake;
4. serialize through the production response DTO;
5. expose one named example for every executable successful outcome;
6. apply those values to generated OpenAPI without maintaining a parallel hand-written response;
7. preserve explicit nulls, aliases, types, reason codes, blockers, authority fields, promotion
   posture, and source-safe lineage exactly.

Factories may share private helpers, but each operation keeps its own mode set and contract. Do not
assume the caller and source-backed endpoints have identical blockers merely because the domain
outcomes overlap.

## Behavior And Enforcement Evidence

Add or retain meaningful behavior tests that prove:

1. every named successful outcome reaches the real HTTP/application path;
2. candidate/resource creation contains the expected policy, review, provenance, and authority
   posture;
3. blocked behavior preserves the correct unsupported reason;
4. suppression and not-eligible outcomes return no candidate or resource;
5. non-candidate outcomes do not persist records or emit downstream side effects;
6. source-backed evaluation closes owned runtime clients on success and blockers;
7. authorization and source-contract mismatch behavior remains product-safe.

Add a capability-owned validator and register it in the central named-success registry when the
repository has one. The validator should compare code-owned examples, generated OpenAPI, endpoint
ledger values, and required behavior-test references exactly. Include negative tests proving that a
missing mode or missing behavior reference fails certification.

## Documentation And Product Truth

Reconcile the smallest complete truth set:

1. endpoint certification ledger;
2. governing RFC slice and RFC index;
3. repository engineering context;
4. API/operator documentation;
5. repo-authored wiki source when reader-facing truth changed;
6. supported-feature registry only when all governed promotion evidence exists.

Record an explicit no-README, no-wiki, or no-supported-feature decision when those surfaces should
remain unchanged. Re-run the deterministic family inventory and record the post-change count.

## Validation, GitHub, And Closure

Use this sequence:

1. focused behavior and contract tests;
2. formatter, linter, and type checker;
3. OpenAPI, endpoint-certification, architecture, documentation, and supported-feature gates;
4. the repo-native full CI target;
5. wiki pre-merge parity when wiki source changed;
6. small, truthful, signed commits;
7. a focused PR linked to the issue, with boundaries and exact validation evidence;
8. fix-forward monitoring until required PR checks pass;
9. the repository-approved non-squash merge path when policy requires linear history;
10. exact-main releasability, publication, image/digest, and security evidence where governed;
11. post-merge wiki publication and strict parity when wiki source changed;
12. focused and parent issue updates with merge SHA, run IDs, residual blockers, and next inventory;
13. local and remote branch cleanup, followed by a clean `main` status check.

PR checks prove the branch. Main releasability proves the merged commit. Do not substitute one for
the other.

## Failure Patterns To Reject

Reject these shortcuts:

1. manually authored response examples that bypass application behavior;
2. a single happy-path example for a multi-shape success union;
3. ledger examples that do not exactly match generated OpenAPI values;
4. examples created directly from domain objects while bypassing production DTOs;
5. source-backed examples that fake the application service instead of only the source port;
6. superficial tests that check status only or never prove absence of persistence;
7. unsupported feature promotion based on contract completeness alone;
8. documentation claims that transfer calculation, methodology, advice, or execution authority;
9. progress kept only in chat, memory, or an unmerged branch;
10. moving to the next family before exact-main, issue, wiki, and branch hygiene are reconciled.
