# Lotus Bank-Ready Engineering Implementation Playbook

This playbook operationalizes the [Lotus Bank-Buyable Engineering Contract](./LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md).
It is the human operating standard for the machine-readable
[bank-readiness control catalog](../platform-contracts/bank-readiness/bank-ready-control-catalog.v1.json).

It applies to Lotus APIs, services, workers, batch jobs, calculation engines, libraries, gateways,
product UIs, AI capabilities, deployment assets, and platform-governance automation.

This is engineering guidance. It is not a claim of regulatory compliance, ISO certification,
SOC attestation, penetration-test approval, production operation, customer acceptance, or bank
acceptance.

## Why This Exists

Bank-ready engineering is not a document count. For every material control, Lotus should be able
to trace:

```text
expectation
  -> documented design
    -> implementation or deployment configuration
      -> positive and negative verification
        -> regression enforcement
          -> operating evidence
            -> accountable owner
```

A policy without implementation is not an implemented control. A tool that is installed but not
run is not enforced. A CI check does not prove production operation. A production claim without
deployment and runtime evidence is unsupported.

## Authority And Layering

Use the following authority order:

1. `AGENTS.md` and explicit user instructions govern execution.
2. Repository context, approved RFCs, contracts, and ADRs govern repository ownership and design.
3. `LOTUS_BANK_BUYABLE_ENGINEERING_CONTRACT.md` defines the standing non-degradation bar.
4. This playbook defines the local, CI, production, evidence, and maturity workflow.
5. `bank-ready-control-catalog.v1.json` defines stable control IDs and machine-readable mappings.
6. App-local scorecards and assessments record current evidence; they do not fork the catalog.

Use `context/playbooks/ENTERPRISE-BACKEND-REFACTORING-INSTRUCTIONS.md` for measurement-backed
backend refactors. Use the applicable delivery, CI, issue-discovery, documentation, and pre-merge
skills for execution. Do not create a parallel bank-readiness skill: current routing is owned by
`lotus-app-issue-discovery`, the app delivery skills, `lotus-ci-enforcement-governance`, and
`lotus-pr-premerge-gate`.

## Target Deployment Posture

The preferred first enterprise posture is bank-hosted deployment:

1. production identity, network, secrets, telemetry, data stores, encryption keys, and operator
   access remain inside the bank-controlled boundary;
2. client-identifiable and bank-confidential data does not leave that boundary by default;
3. Lotus supplies reviewed software, immutable artifacts, deployment templates, upgrade and
   rollback guidance, evidence, and product support;
4. vendor-hosted SaaS, external telemetry, or external model providers require a separate explicit
   architecture, data-boundary, security, legal, and operating decision.

This posture does not mean `lotus-platform` owns a bank's runtime identity, audit, observability,
deployment, or compliance functions. `lotus-platform` owns the shared contracts, validators,
scaffolds, routing, and evidence expectations; the deploying bank and each application owner retain
their substantive responsibilities.

## Environment Responsibilities

| Environment | Purpose | Data Boundary | Required Posture |
| --- | --- | --- | --- |
| Local | Fast deterministic development and focused proof | Synthetic data only | Simple supported startup, isolated identities, safe defaults, focused checks |
| CI | Reproducible verification and evidence generation | Synthetic data only | Clean builds, quality/security/contract gates, source-safe artifacts |
| Shared development | Cross-service integration | Synthetic or explicitly approved masked data | IAM, network boundaries, observability, deployment automation |
| Test/UAT | Business and non-functional verification | Approved test data only | Access control, audit, performance, recovery, release controls |
| Production | Client-serving bank-controlled runtime | Approved production data | Bank IAM, least privilege, encryption, monitoring, resilience, backup, audit, controlled release |
| Recovery | Restore, failover, and continuity validation | Controlled replicated or restored data | RPO/RTO evidence, restore/reconciliation proof, controlled access |

Local Kubernetes is not mandatory for ordinary application work. Use it when proving
Kubernetes-specific behavior such as probes, service discovery, workload identity, network policy,
pod security, Helm rendering, autoscaling, or upgrade behavior.

Production must fail closed when required security configuration is absent. Development bypasses,
debug routes, permissive CORS, default credentials, local secret files, in-memory production state,
or verbose payload logging must not be production-enablable by accident.

## Status, Maturity, And Evidence

Use only the catalog status vocabulary:

| Status | Meaning |
| --- | --- |
| `Implemented` | The applicable completion layers are backed by current evidence. |
| `Partially implemented` | Some required layers exist, but important proof or operation is missing. |
| `Planned` | Deliberate future work; never present it as current support. |
| `Not applicable` | The repository boundary proves the control is outside scope; cite the evidence. |
| `Unknown - requires owner review` | Current truth cannot be proven. This is not compliant or implemented. |

Use maturity independently from status:

| Level | Meaning | Minimum Evidence Class |
| --- | --- | --- |
| `M0` | Unknown | `source_design_contract` only records the gap |
| `M1` | Documented | `source_design_contract` |
| `M2` | Built | `local_test_execution` |
| `M3` | Enforced | `ci_execution` |
| `M4` | Operated | `runtime_execution` or stronger evidence appropriate to the claim |
| `M5` | Independently verified | `production_certification` from the authorized independent process |

Do not infer a higher class from a lower one. Source design cannot clear runtime, deployment, or
production-certification requirements. CI must bind repository, workflow/job, run and attempt,
exact commit, ref, conclusion, and relevant artifact digest. Runtime and deployment evidence must
name the environment boundary and exact version under test.

## Canonical Controls

The catalog is the only source for detailed control definitions and their local, CI, production,
evidence, applicability, lens, and owner mappings. Stable `BR-NNN` IDs are the issue, scorecard, and
assessment vocabulary. Human documents may group or reference those IDs, but must not copy their
definitions or maintain a second control list.

## Control Assessment Workflow

For an app assessment or improvement campaign:

1. Refresh GitHub issue, PR, branch, and repository truth.
2. Determine the repository profile from current repository context.
3. Select a coherent control group from the catalog; do not assess all 25 superficially.
4. Inspect source plus tests, contracts, migrations, workflows, docs, or runtime evidence.
5. Record applicability, status, maturity, evidence class, owner, and residual gap.
6. Search open and closed GitHub issues by control/lens terms and concrete symbols.
7. Reuse or create one issue per root cause with control IDs, evidence, impact, acceptance criteria,
   evaluation condition, non-goals, compatibility impact, and recheck trigger.
8. Implement through the applicable repository delivery skill.
9. Add meaningful positive and negative tests and scan the agreed scope for the same defect pattern.
10. Promote gates only after the signal is measured, deterministic, actionable, low-noise, locally
    runnable, and covered by pass/fail tests.
11. Update the assessment, scorecard, docs, context, wiki, and issue evidence only to current truth.
12. Merge with the repository-approved history-preserving method, validate exact `main`, publish
    wiki source when changed, close verified issues, and reconcile branches/worktrees safely.

Issue count is not progress. Prefer a smaller coherent batch that removes root causes. Never create
backlog solely to populate a matrix.

## Repository-Native Command Surface

Repositories should expose a small, discoverable command surface appropriate to their technology:

```text
setup / dev
lint / format / typecheck
test-unit / test-integration / test-contract / test-security
check or ci
openapi-contract-check / architecture-check
sbom / scan / release-evidence
docker-build / docker-smoke
deployment-render / deployment-check
evidence or assessment report
```

GitHub workflows should consume repository-native commands instead of reimplementing the same logic
in YAML. Blocking commands must leave a clean worktree. Evidence-generation commands may write only
to explicit report or ignored output paths.

## Progressive Enforcement

Use four stages:

1. `Baseline`: measure and disclose current debt.
2. `No regression`: block new critical findings and growth of stable known debt.
3. `Targeted remediation`: remove high-risk gaps and expire exceptions.
4. `Strict release readiness`: require the complete applicable release and deployment evidence set.

Every gate must state the risk it prevents, have a local command, deterministic pass/fail behavior,
focused tests, clear remediation, and an explicit exception policy. Keep subjective, flaky, broad,
or policy-immature signals report-only.

## Definition Of Done For One Control Slice

A control slice is done only when:

1. applicability and owner are explicit;
2. objective, measurable improvement, and compatibility impact are recorded;
3. implementation/configuration and meaningful positive/negative tests exist;
4. the same defect pattern is handled within the bounded scope;
5. the applicable repository-native checks and GitHub lanes pass at exact commits;
6. evidence class and maturity do not exceed the proof supplied;
7. documentation, context, scorecard, contracts, migration, OpenAPI, and wiki decisions are durable;
8. residual actionable work is in a deduplicated GitHub issue;
9. merge, exact-main validation, wiki publication, issue closure, and branch/worktree hygiene are
   complete.

## External Engineering References

The catalog pins the reference identifiers and URLs. Current core references include NIST SSDF
SP 800-218, OWASP ASVS 5.0, SLSA 1.2, the OpenSSF OSPS Baseline, Kubernetes Pod Security
Standards, CISA SBOM guidance, and applicable MAS technology-risk guidance/notices.

These are engineering inputs, not automatic obligations or compliance claims. The bank and the
authorized legal, risk, compliance, security, records, and procurement stakeholders determine
customer-specific applicability.

## Validation

```powershell
python automation\validate_bank_readiness_control_catalog.py
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
```

When the catalog or this playbook changes, update the standing contract, context/reference maps,
issue-discovery skill, affected scaffolds, platform docs/wiki navigation, and deployment sync only
where their truth changes. Record explicit no-change decisions for every adjacent surface reviewed.
