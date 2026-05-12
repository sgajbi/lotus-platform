---
title: Composite performance needs persisted evidence
status: draft
theme: portfolio-analytics-production-readiness
audience: portfolio analytics leaders
source_refs: RFC-049 post-completion draft; based on implemented persisted-fact composite TWR, inspection evidence, source fingerprints, restatement posture, Gateway/Workbench proof, and supported-feature closure.
risk_notes: Industry-wide framing only; no employer, client, internal architecture, incident, active-work, GIPS/compliance claim, or unsupported advanced composite analytics claim.
created_date: 2026-05-12
posted_date:
linkedin_url:
---

Composite performance is where portfolio analytics has to become more disciplined.

A composite return is not just a larger time-weighted return. It depends on which portfolios were
eligible, which member returns were ready, which asset weights were used, and whether any facts were
excluded, restated, blocked, or degraded.

That is why I do not think the best design is to calculate everything on demand from whatever data
is available at request time.

For a banking platform, the stronger pattern is persisted evidence:

Which member-return facts were used?
Which source snapshots and fingerprints support them?
Which restatement version is being shown?
Which members were excluded, and why?
Can an inspector produce an audit-safe explanation without rebuilding the result?

This makes composite performance less like a simple endpoint and more like a data product.

The value is not only the final number. It is the ability to explain the number, support it,
reproduce it, and know when it should not be used.

That is the standard portfolio analytics needs when it moves from a calculation feature into a
production banking capability.
