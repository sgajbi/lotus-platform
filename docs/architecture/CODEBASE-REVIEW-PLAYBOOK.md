# Codebase Review Playbook

## Purpose

This playbook defines how `lotus-platform` review work is tracked when a change spans
platform governance, shared infrastructure ownership, automation, and cross-repo
operational boundaries.

The goal is to keep RFC implementation and hardening work evidence-based rather than
relying on branch history alone.

Companion ledger:

- [CODEBASE-REVIEW-LEDGER.md](./CODEBASE-REVIEW-LEDGER.md)

## Review units

Use one of these review units:

1. Platform governance review
   - RFC implementation, standards ownership, automation guardrails
2. Shared infrastructure ownership review
   - compose baselines, observability bootstrap, telemetry, messaging ownership
3. Drift detection review
   - validators, automation wiring, evidence artifacts

## Status model

- `In Review`
- `Hardened`
- `Signed Off`

Use:

- `Hardened` when implementation and tests landed but rollout/merge is still pending
- `Signed Off` when the reviewed scope has both implementation and durable evidence

## Sign-off standard

Do not mark a review scope as complete unless it has:

1. explicit ownership or architecture documentation
2. implementation changes where needed
3. meaningful tests or validator evidence
4. automation or operational integration where drift would otherwise recur
