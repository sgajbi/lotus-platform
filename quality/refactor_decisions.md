# Refactor Decisions

## Baseline Slice

Decision: start with a stdlib-only platform quality baseline generator instead of adding Radon,
Vulture, Bandit, pip-audit, or OpenAPI lint dependencies immediately.

Reason: `lotus-platform` currently uses a locked platform automation runtime with only `pytest`,
`requests`, and `PyYAML`. The first slice must establish measured baseline evidence without
expanding the dependency surface before scanner policy, false positives, and lane placement are
understood.
