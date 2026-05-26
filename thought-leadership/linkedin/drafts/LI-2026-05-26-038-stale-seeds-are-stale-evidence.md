---
title: Stale seeds are stale evidence
status: draft
theme: production-readiness
audience: engineering and operations leaders
source_refs: Grounded in merged canonical campaign seed supersession work that replaced older campaign-definition versions lacking selection-basis evidence while preserving audit history.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported product claim.
created_date: 2026-05-26
posted_date:
linkedin_url:
---

Test data can become stale in a very specific way.

It may still load.
It may still pass basic checks.
It may still make the screen look populated.

But it may no longer carry the evidence the product now depends on.

That is why canonical seed data should be treated as governed evidence, not as a convenience script.

When a workflow starts relying on a new source-backed field, the seed needs to prove that field is present, visible, and carried through the stack. If an older seeded definition is silently reused, the demo may pass while the proof is weaker than the implementation.

The better pattern is to version the scenario, supersede stale definitions, and keep the older records auditable.

That gives teams a clean current path without pretending history never existed.

In banking platforms, realistic test data is not only about volume or variety.

It is about whether the evidence is current enough to support the product claim being made.
