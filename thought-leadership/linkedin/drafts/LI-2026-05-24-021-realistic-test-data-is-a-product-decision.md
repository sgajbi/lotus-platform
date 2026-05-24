---
title: Realistic test data is a product decision
status: draft
theme: production-readiness
audience: front office and platform leaders
source_refs: Grounded in implemented canonical front-office validation work that added a governed multi-portfolio explicit-list scenario to the demo-data contract and required live validation evidence before claiming RFC36-43 feature coverage.
risk_notes: Industry-wide framing only; no employer, client, production incident, internal architecture, bank adoption, regulatory, investment, AI, or unsupported Lotus product claim.
created_date: 2026-05-24
posted_date:
linkedin_url:
---

Realistic test data is not a testing detail.

It is a product decision.

For front-office platforms, a single portfolio can prove that a screen loads, an API responds, and a workflow path exists. But it may not prove that the workflow behaves like an operating process.

Portfolio managers often think in books, mandates, exceptions, lists, and cohorts. A validation set that never moves beyond one account can miss the questions that matter:

Can the workflow handle more than one portfolio?
Are the portfolio identifiers and mandate context preserved?
Does the validation prove the same business state through API and UI evidence?
Are unsupported discovery or execution claims kept out of the narrative?

The better pattern is governed canonical data.

Define the portfolio identities, scenario purpose, minimum evidence, and supportability threshold in a contract. Then make the live validation fail when the scenario is not actually proved.

That turns demo data from a convenience into a control.

It also keeps product language honest: the platform can say exactly what was validated, and just as importantly, what was not claimed.
