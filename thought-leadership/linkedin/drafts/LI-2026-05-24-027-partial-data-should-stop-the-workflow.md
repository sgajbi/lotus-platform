---
title: Partial data should stop the workflow
status: draft
theme: production-readiness
audience: engineering and operations leaders
source_refs: Grounded in the implemented fail-closed bulk-review campaign candidate consumption path that rejects unavailable, incomplete, degraded, empty, or truncated source pages before durable wave creation.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported product claim.
created_date: 2026-05-24
posted_date:
linkedin_url:
---

One production-readiness test I like is simple:

What does the system do when the data is almost good enough?

That is where many workflow designs reveal their quality.

In a portfolio-management context, a candidate list that is unavailable, incomplete, degraded, empty, or truncated should not be treated as a soft warning if the next step creates durable operating evidence.

It should stop the workflow.

Not because users cannot handle nuance, but because a partial cohort can create a false sense of completeness. The platform may look operational, while the evidence underneath is saying: this is not ready.

Good workflow design makes that boundary visible.

It preserves the source state. It records the reason. It asks the user to refine the scope or wait for the source to become ready. It avoids converting a source-data problem into a downstream audit problem.

This is what fail-closed behavior is for.

It is not a defensive engineering slogan. It is a product decision: if the platform cannot prove the candidate set is complete enough for the action, it should not let the action pretend otherwise.
