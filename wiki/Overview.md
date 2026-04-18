# Overview

## Repository role

`lotus-platform` is the shared platform-governance repository for Lotus.

It provides the engineering system that makes the wider Lotus ecosystem repeatable, supportable,
and governed.

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

- RFC-0072 governs CI and validation lanes
- RFC-0073 governs the context and agent-guidance system
- RFC-0074 governs onboarding, bootstrap, and skill distribution posture
- `lotus-workbench` is the canonical front-office runtime
- `lotus-platform` wraps that runtime with ingress, QA, and governance support

## Cross-cutting commercial narrative

Lotus also needs a consistent ecosystem-level way to explain why the platform matters commercially.

That narrative belongs here in `lotus-platform`, not as accidental residue inside one application
repository.

See:

- [Business Benefits](Business-Benefits)
- [Market Landscape](Market-Landscape)
- [Investor Pitch](Investor-Pitch)
- [Commercial Model and GTM](Commercial-Model-and-GTM)
- [Sales FAQ](Sales-FAQ)
- [Technical Moat and Differentiation](Technical-Moat-and-Differentiation)
