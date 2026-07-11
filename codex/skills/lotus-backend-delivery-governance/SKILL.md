---
name: lotus-backend-delivery-governance
description: "Use when implementing or reviewing backend work in Lotus repositories such as lotus-core, lotus-performance, lotus-risk, lotus-advise, lotus-manage, lotus-report, lotus-idea, lotus-gateway, or lotus-ai. Apply the Lotus platform CI lane model, enterprise security baseline, contract-governance rules, repository-native command policy, truthful PR evidence process defined by RFC-0072, and non-degradation guardrails that prevent low-quality agent-generated backend code."
---

# Lotus Backend Delivery Governance

Use this skill for Lotus backend feature work, cleanup, validation, and PR preparation.

Apply it in line with:

1. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
2. `lotus-platform/context/PROCEDURAL-MEMORY-INDEX.md`
3. the target repo `REPOSITORY-ENGINEERING-CONTEXT.md`
4. `lotus-platform/rfcs/RFC-0072-platform-wide-multi-lane-ci-validation-and-release-governance.md`
5. `lotus-platform/docs/standards/Continuous Integration, Validation, and Release Governance Standard.md`
6. `lotus-platform/platform-standards/LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md`
7. repository-local RFCs and standards already in force

Use `lotus-platform/context/playbooks/CHANGE-PLAYBOOKS.md` for task sequencing and `lotus-platform/context/playbooks/VALIDATION-PLAYBOOK.md` when deciding how much proof is required.

Use `lotus-front-office-runtime` as the primary route when the backend change is being validated
through the governed canonical front-office runtime and populated Workbench product surfaces.

Use `lotus-ci-enforcement-governance` as the primary route when the backend task is mainly about
designing, promoting, or hardening CI quality gates, repository-native enforcement targets,
scorecard-backed regression blockers, or agent-development guardrails.

## Context-First Rule

Before substantive backend work:

1. load the central engineering context,
2. load the repo-local context,
3. load only the specific standards or RFCs the task actually needs.

## Working Model

Before changing code:

1. confirm the repo and branch,
2. classify the repo:
   - Experience API
   - Domain API
   - Opportunity Intelligence / Domain Workflow Service
   - Shared Capability Service
   - Platform Governance / Automation
3. identify the repository-native commands for:
   - lint
   - typecheck
   - unit
   - integration
   - e2e
   - coverage
   - local parity
4. identify whether the change affects:
   - OpenAPI
   - vocabulary
   - no-alias rules
   - migrations
   - Docker/runtime behavior
   - cross-app contracts
   - canonical front-office runtime behavior
5. separate design modularity from runtime modularity:
   - use internal modules, service boundaries, typed contracts, and clear ownership first when the
     goal is maintainability or domain clarity,
   - propose a separately deployable service only when workload isolation, failure isolation,
     independent scaling, data/security ownership, or operational supportability evidence justifies
     the added distributed-systems cost,
   - record the no-runtime-split decision when the slice intentionally improves design modularity
     inside one deployable application.

When Docker/runtime behavior, package metadata, compose mounts, or service app imports are in
scope, verify package import truth before relying on repo-root tests. Code inside a deployable
service app package must not import its own app through a repo-root path such as
`src.services.<same_service>.app...`; prefer relative imports for same-service modules, shared
libraries or ports for durable cross-service contracts, and a focused runtime proof such as
`PYTHONPATH="src/services/<service>:src/libs/portfolio-common" python -c "import app.main"` in a
POSIX shell, or
`$env:PYTHONPATH = "src/services/<service>;src/libs/portfolio-common"; python -c "import app.main"`
in PowerShell, for the affected service.

Before consolidating Python services into one deployable, inspect each distribution's wheel
contents and declared top-level packages. Do not co-install distributions that expose overlapping
namespaces such as `core`, `consumers`, or `repositories`: installation order can silently replace
modules. Prefer one target distribution with durable shared libraries or a bounded transitional
source closure; do not copy the repository's entire source tree to make imports pass. Prove the
installed image imports the target entrypoint and expected modules, excludes unrelated services,
and add a deterministic package/image contract test for the closure.

When Compose declares a worker, manifest, migration, schema, or operator asset that the image
must read, verify the complete image file closure: every Dockerfile `COPY`, every `.dockerignore`
exception, and every imported helper script required by the entrypoint must be present in the
build context and in the built image. Repository tests are not enough for this check. Build the
affected image and run the real entrypoint's bounded `--check-only` or equivalent contract mode
inside the image before accepting runtime evidence; add a deterministic repository gate for the
closure when the asset is production or canonical-stack relevant.

Before editing backend code, produce a short quality intake from the actual repository:

1. name the existing module, service, repository, model, router, and test patterns in the touched
   area,
2. identify the canonical source of business truth and whether the code path is API-facing,
   operator-facing, batch/runtime, or internal-only,
3. identify the closest meaningful tests and the repo-native command that runs them,
4. inspect the current duplicate-code, complexity/function-size, architecture-boundary, security,
   API/OpenAPI, vocabulary, and contract signals that can regress,
5. state the narrow quality signal the slice will improve or preserve.

If you cannot name those items, keep reading before writing code.

For RFC-driven business-application slices, extend that intake with:

1. the RFC slice or blocker family being targeted,
2. the exact blocker codes this slice will clear,
3. the exact blocker codes this slice will intentionally preserve,
4. the source-authority owner for each consumed portfolio, performance, risk, advisory, suitability,
   compliance, reporting, archive, render, AI, Gateway, or Workbench fact,
5. the API/OpenAPI/error-model, persistence, data-mesh, proof-artifact, docs/wiki, and
   supported-feature surfaces affected,
6. the local gate commands and remote GitHub lanes that must pass before merge,
7. the no-claim boundary that prevents a narrow proof from becoming a demo-ready, production-ready,
   client-publication, supported-feature, data-mesh-certified, or live-provider claim,
8. where the slice closure manifest will be recorded before PR merge.

## Delivery Rules

1. Use repository-native commands as the source of truth.
2. Keep changes small and auditable.
3. Update docs and runbooks in the same slice when contracts or operator flow change.
4. Keep security and governance checks first-class; do not treat them as optional cleanup.
5. Prefer fixing root-cause quality issues over updating allowlists or suppressions, unless the allowlist is the truthful current state.
6. Treat closure truth as mainline validated truth. A backend RFC or product capability is not
   complete until the implementation and required proof are merged to `main`, required gates have
   passed, local state is synced clean, and RFC docs, source maps, work-to-be-done ledgers, wiki
   source, supported-features, repository context, API contracts, and proof references are not
   stranded on an unmerged side branch.
7. For RFC-driven backend work, run stranded-truth reconciliation before implementation starts,
   before final closure, and before moving to the next RFC.
8. When a quality inventory is clean, deterministic, and already measured, consider whether
   `lotus-ci-enforcement-governance` should promote it to a blocking gate instead of leaving it as
   report-only evidence.
9. For RFC or proof-driven slices, do not move to the next slice until the PR or ledger records a
   closure manifest: blockers cleared, blockers preserved, proof artifacts, commands, docs/wiki and
   supported-feature decisions, merge method, post-merge validation, and branch cleanup evidence.
10. Before deleting a local or remote branch, verify it is merged or explicitly superseded with PR,
    `git log`, `git diff`, or cherry-pick evidence. Branch cleanup is part of delivery, but code
    preservation comes first.
11. At the end of every meaningful backend slice, run a conscious guidance review before final
    validation and again before PR closure. Decide whether the work revealed a repeatable pattern
    that belongs in a platform skill, repo context, central context, scaffold, validator, README,
    wiki, or runbook. Update durable guidance in the same slice when truth changed; otherwise
    record an explicit no-skill/no-context/no-doc/no-wiki decision in PR evidence, the review
    ledger, or the scorecard.
12. When refactoring orchestration, analytics, inspection, batch, or operator-support code, make
    domain ownership explicit before adding deployment boundaries. Prefer smaller cohesive
    application services and reusable policy/helper modules unless runtime evidence shows that a
    microservice split will improve scalability, resilience, security isolation, or team ownership.
13. Treat documentation presentation as part of backend delivery when the slice changes public,
    operator, or agent-facing truth. A backend PR should not leave README, wiki, scorecard, or
    context pages with stale branch names, stale quality numbers, unprofessional navigation,
    unsupported readiness claims, or hard-to-scan tables that would mislead business, engineering,
    sales, marketing, operations, support, or future-agent readers.
14. When a branch is driven by GitHub issues, build and maintain a current issue matrix from
    GitHub before PR creation. For each issue, record the acceptance criteria,
    files/tests/docs/wiki/context surfaces changed, same-pattern scan performed, local evidence,
    remaining gap, and close/keep-open decision. Count an issue as locally fixed only when the
    branch contains the implementation change plus meaningful tests and any contract, OpenAPI,
    docs, wiki, context, or supported-feature truth required by the issue. Do not count adjacent
    modularity/refactor commits as issue closure unless they directly satisfy the issue's
    acceptance criteria. Do not open the PR while any actionable issue in the agreed batch lacks
    code, tests/docs evidence, or an explicit owner-approved deferral. Keep campaign ledger issues
    open unless the ledger itself was the target.
15. When a GitHub issue exposes repeated concrete external-capability coupling in application code
    such as direct database sessions, Kafka/EventHub producers, HTTP clients, object storage,
    clocks, UUIDs, audit stores, idempotency stores, or unit-of-work commits, fix the pattern rather
    than only the named call site. Define the narrow port and concrete adapter, preserve the
    existing runtime behavior behind the adapter, add fake-port tests for the business contract and
    failure semantics, add a deterministic guard when the invariant is statically checkable, and
    update repo context or standards so the same coupling does not return in the next issue slice.
16. When a backend slice touches lifecycle events, audit logs, replay lineage, recovery, outbox
    records, status history, or operator event history, do not encode identifiers or machine state
    only in human-readable messages. Define a versioned, support-safe typed payload contract; add
    schema/read compatibility for existing rows; ensure replay, regenerate, dedupe, and lineage
    logic consume typed fields rather than parsing text; and test accepted, failed, render/archive,
    retry/replay, batch-item, and legacy-read cases that match the touched event family.
17. When a source adapter calls a tenant-aware downstream service, carry one resolved tenant from
    trusted caller context through the request DTO mapper, application command, port, and adapter.
    Reject missing, multiple, or inconsistent tenant context before runtime construction or network
    I/O; reject unknown request fields so a body cannot silently pose as scope input, and never use a
    hard-coded production tenant fallback. Propagate tenant only where the downstream route publishes
    a tenant-aware contract; do not invent query/header fields on non-tenant-aware routes. Retain the
    resolved tenant in local access scope, deterministic aggregate identity, persistence/idempotency
    identity, and audit lineage wherever those artifacts can otherwise collide across tenants. Apply
    the same contract to scheduled or batch workers through explicit governed configuration. Keep raw
    tenant identifiers out of logs and metric labels; use a bounded scope-provenance posture when
    operations need explanatory evidence. Test tenant A/B outbound payload, candidate identity,
    persistence and ingestion isolation plus no-tenant, ambiguous-tenant, untrusted-header, body
    override, and non-tenant-aware downstream paths. Add a cross-layer deterministic gate when the
    contract is statically enforceable.
18. When a shared dependency can reject a request before route code runs, preserve its approved
    product-safe error code, title, status, media type, and remediation detail through the global
    exception handler. Use a typed boundary exception for governed failures and retain a generic
    safe fallback for unrelated framework errors. Test representative routes, correlation headers,
    observability category, and absence of raw header/token/scope values; add a deterministic gate
    when direct generic exceptions can be detected statically.
19. Do not treat a dead-letter status or queue as a complete recovery control. Provide a bounded,
    operator-authorized, source-safe inspection projection and an explicit re-drive use case through
    API/command DTO, application service, domain policy, repository port, and durable adapter. Bind
    re-drive to trusted caller provenance, dedicated capability, idempotency key, bounded reason and
    change reference, event-family/schema eligibility, a new fenced lease, and append-only audit
    evidence that preserves the original retry count, failure reason, and timestamps. Fence
    concurrent requests, prove replay/conflict after repository or process restart, cap poison-event
    recovery, return rejected attempts to quarantine without automatic infinite retry, and keep
    payloads, aggregate/client/portfolio ids, and raw idempotency material out of responses and
    telemetry. Resolve opaque support references with an exact durable, indexed selector across the
    states needed for truthful conflict reporting; never make older records unreachable through a
    fixed-size recent-row scan or lock unrelated rows while searching. Execute the selector,
    transition, migration/index, restart, and replay path against the real repository technology;
    migration dry-runs and fake adapters are not sufficient database proof. Improve this as an
    internal bounded module first; add a separately deployed recovery service only when workload,
    failure-isolation, ownership, or operability evidence justifies it.
20. When two or more domain fields jointly define one business state, do not validate or query them
    as independent flags. Define one exhaustive, versioned compatibility policy and apply it at
    construction, transitions, repository rehydration, writes, queue/readiness classification, API
    conflict mapping, audit, and operation telemetry. Normalize terminal transitions to explicitly
    non-actionable posture, fail every mutation closed outside its allowed state matrix, and test the
    complete field-value cross product plus repeated actions. For legacy contradictions, preserve an
    auditable quarantine/reconciliation path and prevent new invalid writes without deleting history
    merely to validate a constraint. Derive adapter predicates from the domain policy where possible,
    add a deterministic contract gate against enforcement drift, and keep this as internal design
    modularity unless scaling, isolation, ownership, or operability evidence justifies a runtime split.
21. When an API exposes `asOf`, `evaluatedAt`, effective-time, snapshot, cursor, page-token, or
    continuation semantics, trace that contract through request DTO mapping, application command,
    domain policy, repository port, every adapter, response metadata, OpenAPI, and operator docs.
    Name the exact business field that governs visibility; do not silently substitute source
    business date, evidence generation time, persistence time, or wall-clock time. For offset or
    cursor traversal over mutable state, bind continuation identity to the effective time, entitled
    scope, policy/version, and every state field that can affect ordering, inclusion, or counts.
    Require the identity on later pages, fail stale identity with a stable product-safe conflict,
    and ensure rows outside the as-of boundary neither appear nor invalidate the historical page.
    Prove exact-boundary inclusion, future exclusion, backdated insert, lifecycle/score/suppression
    mutation, malformed identity, and in-flight read races for process-local and durable adapters;
    use a real database proof when SQL snapshot/fingerprint behavior is part of the claim. Prefer a
    pure internal policy plus typed port fields and a deterministic cross-layer gate. Add a separate
    pagination service only when workload, isolation, ownership, or operability evidence justifies
    the runtime complexity.
22. When a use case consumes source-owned evidence, define a versioned temporal compatibility
    contract for every domain family instead of relying only on timezone-aware fields. Validate
    request business date, every included source business/effective date, source generation time,
    evaluation time, and freshness as separate concepts before candidate/result persistence. Apply
    the same domain policy to caller-supplied DTOs, infrastructure-adapter results, scheduled/batch
    ingestion, and optional enrichment refs; do not validate only the required primary source and
    then include unchecked cross-domain evidence. Define source correction/revision identity
    explicitly: preserve producer hashes and lineage, and either create a new versioned aggregate
    identity or apply a governed correction transition rather than silently rewriting evidence.
    Test exact-boundary success, any allowed effective window, mismatched date, future generation,
    stale/partial posture, multi-source conflict, correction identity, and no-persistence behavior.
    Add a deterministic all-family gate when coverage can be checked statically.
23. When lifecycle, audit, replay, recovery, or outbox events carry diagnostic lineage, model
    correlation, trace, and causation as distinct typed concepts across the full request-to-publish
    path. Carry one validated context through request mapping, application use cases, ports,
    adapters, durable rows, and publishers; require correlation and trace for attributable work,
    populate causation only for a real parent event, and define deterministic system context for
    background work. Keep lineage outside business idempotency fingerprints, preserve original
    lineage on replay, constrain identifiers in migrations and storage, map transport headers
    semantically, document consumer replay rules, and keep sensitive data out of lineage and event
    payloads. Prefer an internal bounded module and stable interface; introduce a separate runtime
    service only when workload, failure isolation, ownership, or operability evidence justifies it.
24. When a registry, manifest, or evidence pack controls supported-feature or capability promotion,
    derive promotion through one typed evaluator shared by the repository gate, runtime readiness,
    API projection, and generated artifact. Never count a status string independently. Validate the
    complete schema, required evidence, referenced paths/tests/contracts, authority boundaries,
    review freshness, and planned-versus-implemented separation before promotion. Fail missing,
    malformed, unresolved, future-dated, or stale evidence closed with stable source-safe blocker
    codes; do not expose validator details or filesystem paths through product APIs. Add a
    deterministic gate that rejects parallel counters and hard-coded projections, and prove empty,
    invalid, stale, and fully evidenced current fixtures. Keep the evaluator as internal design
    modularity unless runtime-split evidence exists.
25. Do not treat migration rollback, repository replay, queue re-drive, synthetic smoke, or a
    logical dump as production database disaster-recovery certification. Define a versioned
    service-owned recovery contract that names RPO/RTO, protected tables, backup/PITR strategy,
    retention and legal-hold boundary, residency, encryption/access controls, ownership,
    escalation, cadence, and remaining approval blockers. Keep provider backup infrastructure
    outside the service while implementing a read-only restored-database validator behind a port,
    a real clean-target restore drill, source-safe counts/hashes and invariant evidence, and a
    post-restore resume proof for idempotency, leases, outbox/downstream non-duplication, and
    lineage. Measure readiness after validation rather than accepting a caller-declared ready time;
    distinguish logical restore evidence from physical base-backup plus WAL/PITR evidence. Block
    readiness and every durable write while posture is draining, restoring, degraded, or invalid,
    and require an authorized cutover/rollback runbook. Exercise catalog queries, constraints,
    indexes, relationships, state invariants, and resume behavior against the real database. Use
    scheduled attested evidence where appropriate, but keep production certification blocked until
    approved provider topology and a real PITR/failover exercise exist.
26. When a backend owns personal, advisory, audit, outbox, idempotency, AI-lineage, quarantine, or
    downstream-reference records, treat retention, legal hold, erasure, and purge as one cross-path
    lifecycle contract. Allow only versioned policy references mapped from named authorities;
    caller-chosen non-blank policy text is not authority. Inventory every durable table with field
    classification, purpose, residency, retention start/duration, hold behavior, redaction, and
    purge posture. Keep legal/privacy approval, Report/Archive authority, and AI-provider deletion
    outside the service while enforcing approved local decisions through API DTO, application use
    case, domain policy, port, adapter, and database constraints. Fence ordinary writes and new
    delivery claims with the same aggregate lock; exclude erased/purged records from every direct
    lookup and product projection; pseudonymize prior audit identity and the terminal operation
    itself; preserve enough immutable control authority to purge after payload scope is redacted.
    Publish only bounded state/expiry/missing-control telemetry, with no tenant, client, portfolio,
    case, or actor labels. Prove wrong-tenant, hold precedence, preview, dual approval,
    replay/conflict, restart, atomic rollback, erasure/purge, orphan prevention, and concurrent
    workflow/outbox races against the real repository technology. Keep certification blocked until
    jurisdiction policy, signed authority integration, cross-service retention conformance, and
    scheduled expiry/purge evidence are approved. Prefer an internal bounded module; add a runtime
    service only when workload, isolation, ownership, or operability evidence justifies it.

## Bank-Buyable Default Bar

Treat the Lotus Bank-Buyable Engineering Contract as the default quality posture for backend work,
even when the user does not explicitly ask for a refactor.

Every meaningful backend slice should improve or preserve at least one bank-buyable control:

1. architecture and module boundaries,
2. API and contract quality,
3. data, methodology, lineage, and supportability truth,
4. security and privacy,
5. observability and operator diagnostics,
6. resilience, performance, and scalability,
7. meaningful tests and CI/release evidence,
8. documentation, README, wiki, and repo-context truth.

Do not leave low-quality generated code in place just because the requested feature works. If the
slice exposes duplicate logic, unsupported contract claims, unsafe error/logging behavior, weak
tests, or stale docs in the touched area, either fix it in the same slice or record a concrete
follow-up in the repo's scorecard, review ledger, or PR evidence.

## Non-Degradation Bar

Backend work must leave the application at least as maintainable, observable, secure, and contract
truthful as it was before the change.

Before editing, identify the quality signals that can regress in the touched area:

1. duplicate implementation hotspots,
2. architecture-boundary imports and ownership drift,
3. OpenAPI, vocabulary, no-alias, and domain-contract drift,
4. security scanner findings, dependency findings, and unsafe production assertions,
5. complexity, function-size, and low-maintainability hotspots,
6. test coverage quality for the actual behavior being changed,
7. observability, runtime-status, lineage, and supportability evidence when runtime behavior changes.

During implementation:

1. prefer a shared helper, typed model, service boundary, or existing local pattern over copy-paste,
2. avoid broad rewrites unless the user asked for them and the proof plan covers the blast radius,
3. remove stale special cases when the slice safely reaches them,
4. keep public behavior unchanged unless the behavior change is intentional, tested, documented, and
   represented in API or contract truth,
5. treat report-only inventories as planning evidence and blocking gates as minimum standards, not
   as permission to add weak code that barely passes.
6. finish and merge one proof-backed RFC slice before opening the next, unless the user explicitly
   asks for a planning branch and the branch is clearly marked as unmerged planning work.

Do not claim progress from:

1. cosmetic renames, formatting-only churn, or doc-only optimism,
2. tests that only assert mocks were called while ignoring domain output,
3. allowlists or suppressions without a documented reason and follow-up,
4. generated abstractions that hide complexity without reducing duplicated responsibility,
5. PR summaries that overstate readiness beyond the evidence.

Reject agent-produced backend code that only appears plausible. A Lotus backend change is low
quality if it:

1. creates a parallel service, mapper, DTO, status enum, or contract vocabulary when a governed
   helper or schema already exists,
2. adds local branching, coercion, or fallback behavior that bypasses canonical domain rules,
3. copies calculations, serialization envelopes, query shaping, or error mapping instead of
   extracting the shared responsibility,
4. weakens observability, lineage, runtime-status, or supportability evidence for operator-facing
   paths,
5. adds tests that only freeze implementation mechanics while leaving domain output, failure
   behavior, or contract truth unverified.

## Required Validation Thinking

Map validation to the platform lanes:

1. Feature Lane:
   - lint
   - typecheck
   - fast unit
   - fast contract/schema checks
2. PR Merge Gate:
   - integration
   - coverage
   - security audit
   - OpenAPI / vocabulary / no-alias / migration smoke where relevant
   - Docker build validation where relevant
3. Main Releasability:
   - release-grade rerun and artifact posture
4. Platform End-to-End Validation:
   - required when the change affects canonical product flows, gateway/upstream behavior, seeded demo flows, or platform runtime assumptions

Remote workflows should consume repo-native commands rather than reimplementing local validation in
YAML. If a Make/NPM target exists for a test, coverage, contract, security, or quality gate, call
that target from GitHub Actions. Add or repair the target before adding raw workflow-level `pytest`,
coverage, or scanner commands, and update the CI contract gate when workflow drift should become
blocking.

If the backend change affects governed front-office proof:

1. validate the authoritative service locally,
2. use the canonical runtime path for product-surface proof,
3. do not claim UI readiness from backend checks alone.

## Backend Gold-Standard Checklist

1. API contracts are truthful and fully documented.
2. Naming matches Lotus domain vocabulary.
3. Security and dependency checks are green or explicitly governed.
4. Tests are meaningful, domain-aware, and high-value.
5. The diff reduces or preserves measured duplicate-code, complexity, architecture-boundary,
   security, API-governance, and contract posture.
6. PR evidence lists the actual commands run and any quality metrics that moved.
7. Cross-app impacts are validated at the right layer.
8. Front-office truth claims are supported by governed runtime evidence when the slice affects
   product surfaces.
9. Unmerged remote branches containing durable governance artifacts have been classified as
   `must-merge`, `cherry-pick`, `superseded`, `delete`, or `active`.
10. Any restored durable truth is indexed and pinned by tests or explicit governance evidence where
    the repository has a docs/current-state test pack.
11. Skill, context, README, wiki, and runbook guidance has been updated when the slice changed a
    reusable workflow, command, quality gate, domain ownership boundary, API convention, or
    documentation standard. If not, the no-change decision is explicit and reviewable.
12. README/wiki presentation has been reviewed when docs changed or the user flagged weak
    formatting. Changed wiki pages have professional first-screen scope, clear reader paths,
    implementation-backed claims, reachable navigation, and a recorded check-only or publication
    decision.

## Cross-App Rule

If the change affects a UI-facing workflow through `lotus-gateway`:

1. validate the backend repo locally,
2. validate `lotus-gateway` if contract shape is affected,
3. require platform-level evidence if canonical UI behavior is part of the slice.

## Final Response Rule

When closing backend work, report:

1. what changed,
2. which repository-native commands were run,
3. which lane(s) were satisfied,
4. any remaining gap or governed deviation,
5. for RFC/proof-driven slices, where the slice closure manifest was recorded and how branch
   cleanup was proven.
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


