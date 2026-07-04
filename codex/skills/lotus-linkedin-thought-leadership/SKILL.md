---
name: lotus-linkedin-thought-leadership
description: Draft, review, and maintain Sandeep's LinkedIn thought-leadership content system for private banking, portfolio analytics, advisory, mandates, reporting, production readiness, and Lotus-adjacent platform-building. Use when asked to create LinkedIn posts, plan posting cadence, update the thought-leadership ledger, or continue the personal-brand workflow.
---

# Lotus LinkedIn Thought Leadership

Use this skill when supporting Sandeep's personal LinkedIn content workflow.

## Source Directory

Primary repo content lives in:

`lotus-platform/thought-leadership/linkedin/`

Before drafting or reviewing, read:

1. `content-ledger.md`
2. `themes.md`
3. `voice-and-style-guide.md`
4. recent files in `drafts/`, `reviewed/`, and `posted/`

## Positioning

Position Sandeep as a domain-led technology leader in private banking and wealth platforms.

Core credibility areas:

1. portfolio analytics and reporting,
2. advisory and mandates,
3. performance and risk analytics,
4. solution shaping and stakeholder alignment,
5. production rollout and supportability,
6. enterprise-grade application design.

The goal is personal brand building, not direct Lotus marketing.

## Drafting Rules

Posts should:

1. make one clear point,
2. sound human and practitioner-led,
3. be rooted in real domain, product, delivery, or operating lessons,
4. avoid confidential employer, client, production incident, or internal architecture details,
5. avoid unsupported Lotus capability claims,
6. avoid wording that could be read as criticism of the author's employer or an identifiable bank,
7. keep Lotus clearly separate from employer work,
8. avoid generic motivational language,
9. target 120-220 words unless the user asks otherwise.

Use one of these patterns:

1. problem, insight, principle,
2. misconception, better framing, example,
3. field lesson, implication, design rule,
4. domain concept, why it matters, what good looks like,
5. leadership lesson, product impact, practical takeaway.

## Workflow

When the user asks for new posts:

1. inspect the ledger and recent posts,
2. choose a theme that has not been overused,
3. draft 1-3 variants if useful,
4. write files under `drafts/` unless the user only wants text in chat,
5. update `content-ledger.md`.

When the user says a post was published:

1. move the file from `reviewed/` or `drafts/` to `posted/`,
2. set status to `posted`,
3. update `posted_date` and `linkedin_url` when provided,
4. update `content-ledger.md`.

Do not mark anything as posted without explicit user confirmation.

## Employer-Safe Framing

Sandeep works in a major bank. Treat that as a safety constraint.

Always:

1. frame observations as industry-wide design principles,
2. use constructive language about what good platforms need,
3. avoid active-work, rollout, location, incident, team, vendor, or internal architecture clues,
4. avoid "many banks fail", "most platforms are broken", or similar negative generalizations,
5. never imply Sandeep's employer uses Lotus,
6. rewrite any post that could reasonably be inferred as employer commentary.

## Public Safety

Reject or rewrite content that includes:

1. client or employer-confidential information,
2. traceable production incident details,
3. internal bank architecture,
4. private user behavior,
5. investment advice,
6. regulatory advice,
7. unproved product claims.

## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work revealed a repeatable failure,
missing content-ledger step, weak trigger, safety-review gap, context-routing gap, or
documentation/source-of-truth drift that should change future agent behavior.

When the lesson is durable, update the platform-owned skill source under
`lotus-platform/codex/skills`, and update the routing map, context, validators, scaffolds, gates, or
templates that enforce the new behavior. When no durable change is needed, record the explicit
no-skill/no-context decision in the PR, issue, ledger, or final evidence.
