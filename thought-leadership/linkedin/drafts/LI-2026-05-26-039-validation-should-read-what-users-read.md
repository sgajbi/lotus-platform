---
title: Validation should read what users read
status: draft
theme: production-readiness
audience: engineering and operations leaders
source_refs: Grounded in merged Workbench live browser validation that asserts rendered candidate-selection basis, source table, predicate evidence, and no-order/no-OMS/no-client-contact boundaries.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported product claim.
created_date: 2026-05-26
posted_date:
linkedin_url:
---

One useful test for a front-office platform is simple:

can the validation read what the user reads?

API tests are necessary. Contract tests are necessary. Data checks are necessary.

But for workflow confidence, the browser also needs to prove that the important evidence is actually visible in the product surface.

If a source-owned field explains why a portfolio was included in a campaign review, it is not enough for the backend to return it. The UI should render it. The live validation should assert it. The evidence should survive the journey from source to screen.

This is especially important for boundary language.

If a workflow does not create orders, does not contact clients, and does not claim execution, those boundaries should be visible and testable, not buried in a document.

Good validation is not screenshot theatre.

It reads the same operational cues the user relies on and proves that the screen is carrying the right business truth.
