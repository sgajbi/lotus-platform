---
title: Lineage should survive the handoff
status: draft
theme: evidence-backed-workflows
audience: front office and platform leaders
source_refs: Grounded in the merged source-consumer implementation that preserves source references and source-product lineage while resolving bounded campaign candidates from Core-owned evidence.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported product claim.
created_date: 2026-05-25
posted_date:
linkedin_url:
---

A common weakness in workflow design is that lineage disappears at the handoff.

The source system knows why a record was selected. The workflow system receives the identifier. The user sees the action.

But the evidence that connects those three things gets lost.

In private banking platforms, that is a real product problem. Portfolio actions often depend on mandate context, source ownership, freshness, eligibility, and supportability. If the workflow keeps only the final identifier, it becomes harder to explain why the portfolio was included.

Good workflow design carries lineage forward.

It keeps the source reference, the source-product identity, and the completeness state attached to the action. It lets a reviewer or operator understand not just what happened, but what evidence the system relied on at the time.

That does not require a heavy user experience.

Often it is a compact evidence field, a clear status, and a consistent audit trail.

The principle is bigger than the UI: when a workflow consumes source-owned truth, the source evidence should survive the handoff.
