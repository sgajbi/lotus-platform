# Recent Architectural Decisions Digest

This digest highlights recent decisions that materially affect current Lotus implementation practice.

It exists so a new session does not have to reconstruct current platform reality from many RFCs and pull requests.

## Current Effective Decisions

### RFC-0071 | Canonical environment-scoped service addressing and ingress governance

Current assumption:

1. local and non-prod runtime should prefer canonical `*.dev.lotus` addressing where supported,
2. ingress, hosts management, and service discovery are part of the platform contract,
3. validation and demo readiness should use canonical endpoints end-to-end.

### Front-office local runtime routing

Current assumption:

1. the canonical populated front-office runtime lives in `lotus-workbench`,
2. front-office demo, screenshot, and panel-validation flows should start from `lotus-workbench/docs/operations/canonical-front-office-local-runtime.md`,
3. `lotus-platform/platform-stack` remains the shared ingress and infrastructure baseline, not the primary governed product-surface bring-up path,
4. `PB_SG_GLOBAL_BAL_001` is the default governed seeded portfolio for local front-office proof unless the task explicitly requires another portfolio,
5. RFC-0076 contract files under `lotus-platform/context/contracts/`, including `canonical-front-office-demo-data-contract.json`, are the machine-readable source of truth for the canonical front-office dataset; version 1.1.2 governs `PM_SG_001` as the distinct advisor-book portfolio manager, aligns DPM mandate-health evidence to the canonical `2026-04-10` portfolio valuation date, and separates the `tenant-sg` Workbench caller from `default` command-centre query scope while preserving later campaign dates as separate workflow governance,
6. live validation evidence should preserve contract provenance rather than relying on implicit repo convention.

### RFC-0072 | Multi-lane CI, validation, and release governance

Current assumption:

1. repositories are moving to explicit feature, PR merge, and main releasability lanes,
2. GitHub should be used as the heavy execution engine for expensive validation,
3. repo-native `make check` and `make ci` commands should match real lane truth,
4. workflow security, action baselines, container build rules, and release evidence are now governed platform concerns.

### RFC-0082 | Core domain authority and analytics-serving boundary hardening

Current assumption:

1. `lotus-core` is the source-data, operational read, snapshot/simulation, analytics-input, policy, and control-execution authority, not the owner of downstream performance or risk conclusions,
2. `lotus-performance`, `lotus-risk`, `lotus-gateway`, `lotus-advise`, and `lotus-manage` must classify upstream `lotus-core` consumption under explicit RFC-0082 contract families,
3. REST/OpenAPI remains the canonical current integration model; gRPC is deferred unless retrieval-shape evidence proves transport is the limiting factor,
4. pre-live cleanup should improve the current applications directly rather than creating parallel `v2` services.

### RFC-0083 | Core system-of-record target architecture

Current assumption:

1. `lotus-core` should harden into a banking-grade system of record through controlled slices, not a greenfield `v2` rewrite,
2. the target core architecture separates command/write behavior from read/source-data products,
3. temporal vocabulary, deterministic state reconstruction, ingestion lineage, reconciliation, data quality, and source-data product contracts are first-class architecture concerns,
4. future implementation work should treat RFC-0083 as the target blueprint and RFC-0082 as the boundary guardrail.

### Consumer retry safety and source-response admission

Current assumption:

1. a consumer may automatically retry an upstream mutation after an ambiguous response loss
   (read/write failure, remote-protocol error, read/write timeout) only with a producer
   replay-identity contract and one identity reused verbatim across attempts; without one it
   stops and surfaces the indeterminate outcome, and it does not follow method-preserving
   redirects such as `307` or `308`; a `303` follow-up is a separately classified read,
2. correlation and trace ids are tracing, never replay identity,
3. a well-shaped upstream success is published only after it is bound to the requested
   operation's identities (resource id, per-row identities, echoed idempotency key,
   handle-to-status-link consistency); mismatches and malformed successes become the declared
   bounded upstream-contract failure, not an internal error,
4. the pattern reference is
   `codex/skills/lotus-backend-delivery-governance/references/source-boundary-and-recovery-patterns.md`;
   the first full implementation is lotus-gateway's 2026-09-05 completion campaign (PRs #724–#729).

### Branch protection as asserted policy

Current assumption:

1. adopting repositories document their `main` protection as a declarative policy table
   (`quality/branch_protection_policy.v1.json`) carrying each protection field, the review
   authority, and `documented_exceptions` with a `retires_when` condition — adopted so far by
   lotus-gateway and lotus-render, with the estate-wide required-checks inventory remaining
   authoritative in `automation/repository-governance-policy.json`,
2. a lifted checker compares live protection against the candidate policy field by field in a
   blocking pre-merge lane, failing in both drift directions; scheduled runs are a supplement
   (and the required home only during a documented drift-first adoption transition),
3. the checker authenticates with a repository PAT — the workflow token cannot read branch
   protection — inside a stated trust boundary (per-PR execution only where every same-repo
   pusher holds the PAT's authority; otherwise an approved `pull_request_target` job on base-ref
   checker code with the PR's policy read as inert data),
4. the pattern reference is
   `codex/skills/lotus-ci-enforcement-governance/references/branch-protection-policy-gate.md`;
   adoptions: lotus-gateway#737 (reference implementation), lotus-render#281.

### Product and UI posture

Current assumption:

1. premium private-banking UI should be conservative, institutional, and information-dense without decorative noise,
2. summary first, detail on demand remains the product principle,
3. no UI feature should exist without real backend support,
4. numbers, clarity, and decision value should dominate over narrative or ornamental UI.

### Documentation and memory posture

Current assumption:

1. important working knowledge should not remain trapped in chat history,
2. platform-wide truth belongs centrally in `lotus-platform`,
3. repository truth belongs locally in each repo,
4. repeatable patterns should be promoted into standards, validators, templates, or skills.
