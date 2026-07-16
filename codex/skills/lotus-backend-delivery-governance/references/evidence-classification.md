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

## Receipt-Bound Runtime Execution

When a `runtime_execution` artifact can clear a source or workflow blocker, a
success flag, caller-composed summary, candidate count, or copied response field
is not sufficient. Require a closed, versioned contract with:

1. a request receipt that binds pseudonymous entitled scope, business as-of,
   evaluation time, correlation identity, and consumer policy version;
2. a producer receipt that preserves source-owned product/version, stable route
   identity, authoritative scope and time, freshness, quality, content hashes,
   and the workflow facts used by the consumer;
3. an evaluation receipt emitted from one named application use case, binding
   policy inputs, reason codes, outcome, source-receipt digest, and candidate
   identity only when a candidate exists;
4. canonical digests and cross-receipt reconciliation that reject unknown
   fields, source substitution, scope/time drift, malformed counts or hashes,
   contradictory outcomes, and raw sensitive identifiers;
5. explicit blocker lists and non-proof claims that prevent a narrow source
   observation from becoming suitability, compliance, execution, publication,
   deployment, production, data-mesh, Workbench, or supported-feature proof.

The generator must perform one source operation and one named use-case
evaluation. A completed no-opportunity result can be valid runtime evidence when
the domain policy supports it; candidate creation is not a generic proof of
successful execution. A blocked diagnostic artifact may be retained for
operations but must clear no blocker.

Never substitute request as-of, caller tenant, consumer clock, proof generation
time, or local defaults for missing producer-owned identity. Preserve partial
producer evidence for diagnosis and fail qualification closed. Keep this as an
internal capability module unless workload, failure isolation, ownership, or
operability evidence justifies a separately deployable service.

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

