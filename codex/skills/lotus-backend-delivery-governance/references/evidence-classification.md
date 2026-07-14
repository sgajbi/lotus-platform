# Evidence Classification For Blocker-Clearing Proof

Use this reference when a Lotus backend or RFC slice claims that a proof artifact, test run,
workflow, runtime exercise, deployment receipt, or production attestation clears a blocker.

## Closed Evidence Taxonomy

| Evidence Class | What It Can Prove | Minimum Evidence |
| --- | --- | --- |
| `source_design_contract` | Source shape, schema, declared interface, planned ownership, or static contract presence. | Repository path, exact commit/ref, schema or source symbol, and validator or review evidence. |
| `local_test_execution` | Behavior exercised locally in a developer or agent environment. | Command, repository, branch, exact commit, environment boundary, result, and relevant artifact path or digest when an artifact is consumed later. |
| `ci_execution` | Behavior exercised by a trusted CI workflow. | Repository, workflow, job, run id, run attempt, exact commit SHA, ref, successful conclusion, and artifact digest for every proof artifact used to clear a blocker. |
| `runtime_execution` | Behavior exercised against a running service or composed runtime. | Runtime topology, service versions or commits, request/operation evidence, correlation or trace reference, result, and source-safe artifact digest. |
| `deployment` | A release artifact or environment deployment step completed. | Immutable image or package digest, deployment environment, deployed ref, promotion record, operator or CI actor, and rollback or non-production boundary. |
| `production_certification` | Production-grade certification or regulated operating approval. | Cryptographic attestation, protected mainline source, trusted producer workflow, protected environment, signer/key posture, evidence retention, approval owner, and exact certification scope. |

## Blocker Clearance Rule

Every blocker that can be cleared by evidence must declare its minimum `required_evidence_class`.
An artifact may clear the blocker only when its `evidence_class` is the same class or a strictly
stronger class that actually includes the required observations.

Do not promote across classes by implication:

1. `source_design_contract` evidence cannot clear `runtime_execution`, `deployment`, or
   `production_certification` blockers.
2. `local_test_execution` evidence cannot clear `ci_execution` blockers unless the blocker
   explicitly accepts local-only proof.
3. `ci_execution` evidence cannot clear `runtime_execution` blockers unless the CI job records the
   actual runtime topology and source-safe runtime observations.
4. `runtime_execution` evidence cannot clear `deployment` blockers unless it is tied to immutable
   deployed artifacts and environment promotion evidence.
5. `deployment` evidence cannot clear `production_certification` blockers without the required
   cryptographic attestation and approval posture.

## CI Evidence Binding

When a blocker accepts `ci_execution`, the evidence must bind:

1. repository,
2. trusted workflow name or file,
3. trusted job name,
4. run id,
5. run attempt,
6. exact commit SHA,
7. ref,
8. successful conclusion,
9. relevant artifact digest.

Status text, a workflow URL, or a copied artifact path is not enough by itself.

## Migration Guidance

For existing proof inventories:

1. add `evidence_class` and `required_evidence_class` fields before promoting claims,
2. split broad remediation into bounded issues by blocker family and owning repository,
3. keep existing blockers open when their current evidence is a lower class than required,
4. preserve app-specific blocker vocabulary in the owning application rather than centralizing it
   in this platform reference,
5. add local regression tests that reject missing classifications and static-to-runtime promotion,
6. add reusable automation beside this skill only after at least two Lotus repositories adopt the
   taxonomy and the rule can be checked without app-specific blocker vocabulary.

