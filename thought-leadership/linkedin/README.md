# LinkedIn Thought Leadership Workflow

This directory is the governed working area for personal LinkedIn thought-leadership content
inspired by the Lotus ecosystem and adjacent private-banking platform work.

It is not product truth, marketing copy, or a Lotus sales channel. Its purpose is to preserve a
durable content memory so future agents can draft posts that are authentic, non-confidential,
domain-aware, and consistent with the author's professional positioning.

## Positioning

The author should be positioned as a domain-led technology leader in private banking and wealth
platforms, with practical experience across:

1. portfolio analytics and reporting,
2. advisory and mandate workflows,
3. performance and risk analytics,
4. production rollout and front-office adoption,
5. stakeholder alignment and operating-model change,
6. enterprise-grade platform design and supportability.

Posts should build credibility through real problem framing, design judgment, and operating
lessons. They should not hard-sell Lotus or imply unsupported product capability.

Posts must also avoid creating the impression that they reveal or criticize the author's employer,
current work, current platform, internal users, incidents, or operating model. Use industry-wide,
constructive design language unless the user explicitly approves a different framing.

## Folder Contract

1. `backlog/`
   Raw ideas, hooks, and future post concepts.
2. `drafts/`
   Agent- or human-authored posts not yet reviewed.
3. `reviewed/`
   Posts approved for publication but not yet posted.
4. `posted/`
   Posts that were published or manually marked as published.
5. `content-ledger.md`
   Durable index of post status, themes, audience, and publication history.
6. `themes.md`
   Theme map and rotation guidance.
7. `voice-and-style-guide.md`
   Writing principles, guardrails, and review checklist.

## Status Model

Use these statuses in post frontmatter and in the ledger:

1. `idea`
2. `draft`
3. `reviewed`
4. `posted`
5. `retired`

Do not mark a post as `posted` until the user confirms it was actually published or provides the
LinkedIn URL.

## Required Frontmatter

Each post file should start with:

```yaml
---
title:
status:
theme:
audience:
source_refs:
risk_notes:
created_date:
posted_date:
linkedin_url:
---
```

`source_refs` should reference Lotus docs, RFCs, implementation evidence, or real-but-sanitized
professional experience when relevant. Keep source references internal; do not expose confidential
details in the public post.

## Agent Workflow

Before drafting:

1. read `content-ledger.md`,
2. read `themes.md`,
3. read `voice-and-style-guide.md`,
4. inspect recent posts in `drafts/`, `reviewed/`, and `posted/`,
5. pick a theme that has not been overused recently.

When drafting:

1. write as the author, not as a company account,
2. keep the post grounded in one practical idea,
3. avoid confidential employer, client, user, incident, or architecture details,
4. avoid overstating Lotus capabilities,
5. avoid generic motivational content,
6. avoid wording that sounds like criticism of the author's employer or any identifiable bank,
7. keep Lotus and employer experience clearly separate,
8. include a clear professional insight or decision principle.

After drafting:

1. add or update the post file,
2. update `content-ledger.md`,
3. leave status as `draft` unless the user explicitly approves or posts it.
