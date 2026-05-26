---
title: Audit history should survive refresh
status: draft
theme: delivery-governance-product-truth
audience: banking transformation leaders
source_refs: Grounded in merged canonical campaign-definition versioning and supersession work that moved current proof to a new version while retaining older definitions as auditable history.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported product claim.
created_date: 2026-05-26
posted_date:
linkedin_url:
---

Refreshing a product scenario should not erase its history.

This matters in evidence-heavy workflows.

When a canonical definition changes because the product now carries stronger source evidence, teams need two things at the same time:

a clean current version, and a truthful record of what came before.

Deleting or overwriting the old definition may make the test environment simpler, but it weakens the audit story. Reusing it silently may be worse, because the screen can look current while the underlying evidence is not.

A better pattern is versioning plus supersession.

The current definition carries the evidence the workflow now requires. Older definitions remain visible as historical records. The platform can explain what replaced what, instead of pretending there was never a change.

That is a useful principle beyond test data.

In banking platforms, the path to production readiness is rarely a single perfect state. It is a sequence of controlled changes.

Good systems keep that sequence reviewable.
