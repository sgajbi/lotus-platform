# RFC-0088 - Self-Serve Discovery and Dependency Catalog

| Field | Value |
| --- | --- |
| Status | Draft |
| Created | 2026-04-19 |
| Last Updated | 2026-04-19 |
| Owners | lotus-platform architecture; ecosystem repository maintainers |
| Depends On | RFC-0073; RFC-0084; RFC-0085; RFC-0086 |
| Related Standards | `RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`; `RFC-0084-mesh-governance.md`; `RFC-0085-gateway-governed-domain-product-publication-and-trust-contracts.md`; `RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md` |
| Scope | Cross-repo |

## Executive Summary

Even with governed products, repo-native declarations, and strong published contracts, Lotus still
needs one more capability before it starts to feel like a genuinely navigable federated platform:
people need to discover products, dependencies, ownership, and lifecycle posture without reading
many repositories manually.

This RFC defines the self-serve discovery and dependency catalog plane for Lotus.

The target state is:

1. Lotus can generate a searchable, machine-readable catalog of governed products,
2. ownership and consumer relationships are visible in one place,
3. dependency graphs and lifecycle posture are discoverable without manual repo archaeology,
4. future agents and engineers can onboard faster because the ecosystem explains itself.

This RFC turns the declaration and publication work from hidden metadata into an explorable platform
surface.

## Original Requested Requirements (Preserved)

The user intent preserved in this RFC is:

1. cover self-serve discovery and dependency catalog as one of the remaining areas needed for a more
   credible mesh posture,
2. make the work implementation-bearing rather than writing only more descriptions,
3. improve future agent effectiveness by making ecosystem discovery easier and less chat-dependent,
4. preserve the same mandatory second-last and final closure slices,
5. consciously assess context, docs, and skills changes as part of the final slice.

## Current Implementation Reality

Overall classification: `Partially implemented (requires enhancement)`

### What is implemented well today

#### 1. Lotus already has strong context and registry foundations

Evidence:

1. `context/lotus-context-manifest.json`
2. `context/ECOSYSTEM-REGISTRIES.md`
3. `context/CONTEXT-REFERENCE-MAP.md`
4. `rfcs/RFC-0073-lotus-ecosystem-engineering-context-and-agent-guidance-system.md`

Assessment:

Lotus already values machine-readable context and navigable ecosystem metadata. RFC-0088 should
 extend that principle into product and dependency discovery.

#### 2. RFC-0084 defines the core product-governance data

Evidence:

1. `platform-contracts/domain-data-products/README.md`
2. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
3. `rfcs/RFC-0084-mesh-governance.md`

Assessment:

The discovery plane does not need to invent product metadata; it needs to generate navigable views
from already-governed declarations.

#### 3. RFC-0086 prepares repo-native ownership

Evidence:

1. `rfcs/RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md`

Assessment:

Repo-native onboarding is the right precursor. Once those declarations are federated, discovery can
aggregate them into catalog and graph surfaces.

### What is only partially implemented

1. ecosystem context exists, but product and dependency cataloging are not yet self-serve,
2. product metadata exists, but graph-style discovery does not,
3. ownership and dependency posture are available only by reading contracts or docs directly.

### What is not yet implemented

1. no platform-generated product catalog,
2. no platform-generated dependency graph,
3. no single discovery surface for ownership, lifecycle, consumer posture, and publication posture,
4. no self-serve discovery workflow for future agents and engineers.

## Requirement-to-Implementation Traceability

| Requirement | Current evidence | Current status | RFC-0088 response |
| --- | --- | --- | --- |
| Make product and dependency discovery self-serve | Context registries exist, but domain-product discovery is still manual | Partially satisfied | Generate catalog and dependency graph artifacts from governed declarations |
| Keep the work implementation-bearing | Structured metadata already exists in context and contracts | Partially satisfied | Add generators, validation, and discovery artifacts instead of only prose |
| Improve future agent effectiveness | Context system exists but still requires many file reads for cross-repo product discovery | Partially satisfied | Add machine-readable and human-readable discovery surfaces built from governed inputs |
| Preserve strong closure discipline | User requested same quality posture | Not yet satisfied before this pass | Include mandatory Slice 7 and Slice 8 plus review gates |

## Design Reasoning and Trade-offs

The key design choice is to make discovery generated, not hand-maintained.

### Why discovery should be generated from governed inputs

If Lotus writes manual catalog prose in many places, it will drift quickly.

The right model is:

1. declarations remain the source of truth,
2. platform generates catalog and graph artifacts from those declarations,
3. human-readable docs summarize the generated truth rather than competing with it.

### Why discovery should be separate from telemetry

Telemetry answers "what is true right now?"

Discovery answers:

1. what exists,
2. who owns it,
3. who depends on it,
4. how it is classified,
5. where it is published.

Those are related but distinct concerns. Keeping discovery separate allows implementation and review
to stay clearer.

## Why This Is The Next Highest-Value RFC

This RFC is high-value because it removes the hidden-tax problem in a federated architecture.

Without RFC-0088:

1. the metadata may exist,
2. the contracts may be governed,
3. but people still need manual repo archaeology to understand the ecosystem.

With RFC-0088:

1. engineers onboard faster,
2. agents need less repetitive discovery work,
3. ownership and dependency reasoning become much easier,
4. Lotus gains one of the practical qualities people expect from a real mesh-like platform.

## Gap Assessment

### Gap 1: Product catalog generation

Lotus does not yet generate a durable catalog of governed products from the declaration set.

### Gap 2: Dependency graph generation

Lotus does not yet generate a clear dependency graph showing producer-consumer relationships across
the ecosystem.

### Gap 3: Published contract visibility

There is not yet one place that connects products, gateway publication families, and consumers.

### Gap 4: Agent-oriented discovery support

Future agents still have to open many files manually to answer basic cross-repo ownership and
dependency questions.

## Deviations and Evolution Since Original RFC Direction

Discovery was initially treated as a natural by-product of RFC-0084.

After reviewing the current state, the clearer conclusion is:

1. the data is necessary but not sufficient,
2. generated discovery and graphing deserve their own implementation program,
3. that program should build on repo-native onboarding rather than precede it.

## Proposed Changes

### Decision

Lotus will implement a self-serve discovery and dependency catalog plane generated from governed
domain-product declarations, consumer declarations, and gateway publication manifests.

Specifically:

1. `lotus-platform` will generate catalog artifacts from governed declaration sources,
2. the generated catalog will include ownership, lifecycle, consumer posture, and dependency
   relationships,
3. dependency graph artifacts will become discoverable to both humans and automation,
4. context and onboarding flows will link to these generated discovery surfaces.

### Governance invariants

1. discovery must be generated from governed inputs rather than manually curated prose,
2. generated artifacts must identify their source declarations and generation timestamp,
3. no secondary discovery surface may redefine ownership or dependency truth manually,
4. final two slices remain mandatory quality gates.

### Target operating model

#### 1. Federated declaration sources

Repo-native producer and consumer declarations remain the source inputs.

#### 2. Platform-generated catalog plane

`lotus-platform` generates searchable machine-readable and human-readable catalog outputs.

#### 3. Platform-generated dependency graph plane

`lotus-platform` generates graph-friendly artifacts for upstream and downstream reasoning.

#### 4. Context and onboarding discovery plane

Lotus context and onboarding surfaces link to the generated catalog instead of requiring manual file
discovery first.

### Platform capability model

#### A. Generated product catalog

Recommended outputs:

1. `generated/domain-product-catalog.json`
2. `generated/domain-product-catalog.md`

#### B. Generated dependency graph

Recommended outputs:

1. `generated/domain-product-dependency-graph.json`
2. optional graph-friendly exports such as CSV or Mermaid

#### C. Discovery integration

Context and onboarding docs should link to the generated catalog and graph as the default discovery
surface.

## Test and Validation Evidence

Reviewed evidence includes:

1. `context/lotus-context-manifest.json`
2. `context/ECOSYSTEM-REGISTRIES.md`
3. `platform-contracts/domain-data-products/validate_domain_data_product_contracts.py`
4. `rfcs/RFC-0084-mesh-governance.md`
5. `rfcs/RFC-0086-repo-native-domain-product-onboarding-and-federated-rollout.md`

## Original Acceptance Criteria Alignment

| Original intent | RFC-0088 alignment |
| --- | --- |
| Make discovery and dependency posture self-serve | The RFC centers on generated catalogs and dependency graph artifacts |
| Keep the work implementation-bearing | The RFC requires generators, validation, and integration into context/onboarding |
| Improve future agent effectiveness | The generated discovery plane becomes a first-class context input |
| Preserve second-last and final closure slices | Slice 7 and Slice 8 are mandatory and explicit |

## Mandatory Slice Review Gate

Every completed slice must receive a review pass before the next slice begins.

That review must check:

1. whether generated outputs remain source-driven and truthful,
2. whether duplicate manual discovery prose can be removed or reduced,
3. whether future agents will be able to use the outputs directly,
4. whether any repeated discovery lesson should become durable context or skill guidance,
5. whether the slice left the discovery surface cleaner and easier to maintain than before.

## Rollout and Backward Compatibility

### Slice 0: Audit current discovery posture and source inputs

1. inventory existing product and dependency truth sources,
2. identify which generated outputs are needed first,
3. classify which existing docs should later link to generated discovery instead of duplicating it.

Exit gate:

1. source inputs for the first-wave generated artifacts are explicit,
2. existing manual discovery docs are classified as durable, transitional, or removable.

### Slice 1: Catalog and graph schema design

1. define generated artifact shapes,
2. define graph-friendly export formats,
3. add generator validation tests.

Exit gate:

1. generated artifact shapes are explicit and test-backed,
2. graph exports are sufficient for both human and automation use in the first wave.

### Slice 2: First generated catalog outputs

1. generate the first product catalog from governed inputs,
2. generate the first dependency graph artifact.

Exit gate:

1. generated outputs are produced from real governed inputs,
2. the first-wave catalog and graph answer core ownership and dependency questions truthfully.

### Slice 3: Context and onboarding integration

1. link context and onboarding docs to the generated discovery surfaces,
2. update reference maps to make the generated artifacts easy to find.

Exit gate:

1. context and onboarding no longer require avoidable manual repo archaeology for common discovery
   questions,
2. generated outputs are discoverable from the normal Lotus reading path.

### Slice 4: Publication and consumer visibility integration

1. extend the catalog to show gateway publication families where applicable,
2. connect product, consumer, and publication relationships in the generated view.

Exit gate:

1. generated outputs can connect domain products to consumer and publication posture where
   applicable,
2. publication visibility is source-driven rather than manually narrated.

### Slice 5: Discovery UX and automation hardening

1. improve generated artifact readability and machine-utility,
2. add tests and validation for drift and regeneration.

Exit gate:

1. generated outputs are both readable and automation-friendly,
2. drift and regeneration are test-backed.

### Slice 6: Agent and operator readiness hardening

1. confirm the generated catalog supports the most common discovery questions,
2. reduce manual repo-archeology requirements in docs and procedures.

Exit gate:

1. common ownership and dependency questions are answerable from the generated plane,
2. operator and agent discovery paths are materially simpler than before.

### Slice 7: Code Review, Governance Tightening, and Loose-End Closure

This slice is mandatory.

1. review generation logic, drift checks, and context integration for loose ends and duplicated
   discovery prose,
2. tighten governance so generated discovery remains the stronger truth source,
3. confirm the discovery and dependency catalog follows the platform certification pattern,
4. remove or retire duplicated manual discovery prose and transitional shortcuts where generated
   discovery is already authoritative.

Exit gate:

1. no completed discovery surface is left with avoidable duplicate manual truth,
2. platform governance and certification expectations are satisfied across the discovery plane.

### Slice 8: Documentation, Agent Context, Wiki Update, Skills Review, and Branch Hygiene

This slice is mandatory.

1. update docs, context, and wiki links for the generated discovery plane,
2. consciously assess whether skills or onboarding guidance should change for catalog-generation and
   dependency-discovery work,
3. identify anything that should be added or removed from the context/docs to support future agent
   effectiveness,
4. make any keep, tighten, add, remove, or no-change decisions for discovery guidance explicit,
5. complete branch hygiene truthfully.

Exit gate:

1. future agents can discover the generated discovery plane quickly,
2. any no-change decision for skills or context is explicit rather than omitted,
3. no branch or context debt is left behind.

## Validation and Evidence Model

Required proof for implementation under this RFC:

1. generator tests,
2. drift-detection tests,
3. generated catalog and graph artifacts from real governed inputs,
4. context/onboarding updates that point to the generated discovery plane,
5. evidence that common ecosystem ownership and dependency questions are answerable from the
   generated outputs.

## Skills and Guidance Assessment for Future Work

### Improvements likely needed once implementation starts

1. context routing guidance may need a clearer route for discovery-catalog work,
2. a generated-catalog reference may need to be added to the quickstart or engineering context once
   it becomes durable truth,
3. a dedicated discovery/catalog skill may be justified if this becomes recurring work.

### Conscious no-change decisions at RFC draft stage

1. no skills are changed in this draft-only pass,
2. no context files are changed until generated artifact paths are implemented,
3. no manual discovery docs are removed until generated outputs are proven sufficient.

That no-change posture at the draft stage is intentional rather than accidental.

## Risks and Mitigations

### Risk: Generated catalog becomes another stale artifact

Mitigation:

1. generate from governed inputs,
2. add drift checks and regeneration validation.

### Risk: Context grows too noisy

Mitigation:

1. link to generated discovery rather than duplicating it everywhere,
2. keep generated outputs high-signal and task-oriented.

## Acceptance Criteria

This RFC is complete only when:

1. Lotus can generate a product catalog from governed inputs,
2. Lotus can generate a dependency graph from governed inputs,
3. context and onboarding surfaces point to the generated discovery plane,
4. common ownership and dependency questions are answerable without manual multi-repo archaeology,
5. duplicated manual discovery truth is removed or explicitly justified where generated discovery is
   authoritative,
6. Slice 7 and Slice 8 are completed as mandatory quality and closure gates.

## Non-Goals

This RFC does not:

1. replace RFC-0086 repo-native onboarding work,
2. replace RFC-0087 live telemetry and trust certification work,
3. define a polished end-user UI for catalog browsing,
4. manually curate product truth outside the governed declaration sources.

## Open Questions

1. Which generated outputs should be canonical first: JSON only, or JSON plus Markdown?
2. Should graph exports include gateway publication relationships in the first wave or only domain
   producer-consumer edges?
3. Which existing context docs should be slimmed down once generated discovery is strong enough?

## Next Actions

1. refine the generated artifact shapes and locations,
2. define the first-wave dependency graph outputs,
3. prepare implementation prompts for catalog generation and context integration.
