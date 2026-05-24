---
title: A front-office test should read back the evidence
status: draft
theme: evidence-backed-workflows
audience: front office and platform leaders
source_refs: Grounded in implemented canonical validation hardening where PM operating-quality seed data is read back through governed APIs before UI proof is accepted.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported Lotus product claim.
created_date: 2026-05-24
posted_date:
linkedin_url:
---

A useful front-office test should do more than create a happy-path record.

It should read the evidence back.

That sounds simple, but it changes the quality of the validation. A workflow can show a success
message while the underlying business state is incomplete, stale, or not connected to the governed
source of truth.

For portfolio and advisory workflows, the stronger pattern is:

Create the review state.
Read it back through the supported API.
Check the identifiers and as-of context.
Confirm the UI is showing the same business evidence.
Preserve enough proof that another engineer can inspect the result later.

This matters because front-office users do not experience systems as separate test layers. They
experience a journey: portfolio context, analytics, review, decision, action, and follow-up.

If the test only proves one layer, it may miss the risk in the handoff.

Good validation follows the evidence across the workflow. It proves not just that something
happened, but that the right business state is available, explainable, and supportable.
