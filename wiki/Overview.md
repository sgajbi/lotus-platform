# Overview

## Repository role

`lotus-platform` is the shared platform-governance repository for Lotus.

It provides the engineering system that makes the wider Lotus ecosystem repeatable, supportable,
and governed.

It is not a product UI or a business-domain API. It is the control layer that keeps Lotus apps,
runtime evidence, standards, and agent work aligned.

## What it owns

- central context and registries
- developer onboarding and agent ramp-up guidance
- repo checks, platform validation, and QA automation
- shared ingress and local stack support
- cross-repository standards and scaffold templates
- governance RFC inventory and implementation evidence

## What it does not own

- portfolio, transaction, performance, risk, advisory, reporting, or AI business authority
- the primary product UI runtime
- repository-local implementation truth that belongs inside another Lotus repo

## Why the platform exists

Lotus is not a loose collection of repositories. It is a governed private-banking ecosystem.

The platform layer exists to ensure:

1. shared standards are actually executable
2. validation is repeatable across repositories
3. local runtime and ingress posture are governed
4. onboarding and agent workflows do not rely on tribal memory
5. repo-level truth and platform-level truth stay separated cleanly

## Current posture

| Area | Current Implementation-Backed Posture |
| --- | --- |
| CI and validation | RFC-0072 governs feature, PR merge, main releasability, and platform validation lanes. |
| Context and agents | RFC-0073 and RFC-0074 govern central context, agent ramp-up, operating-contract sync, and skill distribution posture. |
| Canonical front-office proof | `lotus-workbench` owns the populated runtime; `lotus-platform` wraps ingress, QA summaries, screenshots, and governance evidence. |
| Canonical data | `PB_SG_GLOBAL_BAL_001` is governed by platform contract files, and the demo pack is excluded from canonical PB seed by default. |
| `lotus-idea` | Included by default in canonical platform QA with readiness and teardown evidence; mesh certification remains evidence-gated. |
| Merge policy | CI and conversation resolution are required controls; human approval reviews are optional in the single-developer baseline. |

## Cross-Cutting Commercial Narrative

Lotus also needs a consistent ecosystem-level way to explain why the platform matters commercially.

That narrative belongs here in `lotus-platform`, not as accidental residue inside one application
repository.

Commercial pages must stay implementation-backed. They may explain operating value, delivery
leverage, and supportability posture, but they must not imply unsupported product readiness or
unverified market claims.

See:

- [Business Benefits](Business-Benefits)
- [Market Landscape](Market-Landscape)
- [Investor Pitch](Investor-Pitch)
- [Commercial Model and GTM](Commercial-Model-and-GTM)
- [Sales FAQ](Sales-FAQ)
- [Technical Moat and Differentiation](Technical-Moat-and-Differentiation)
