# Repository Engineering Context Contract

This contract defines the minimum required shape for `REPOSITORY-ENGINEERING-CONTEXT.md` across the Lotus ecosystem.

## Purpose

Each repository-local context document must provide repository truth without duplicating platform-wide policy prose.

It should help a new agent understand:

1. what the repository owns,
2. how it fits the ecosystem,
3. what commands and validations matter,
4. what current-state realities and constraints matter now.

It is part of the small startup set, so it must be concise enough to load routinely. Detailed
contracts and procedures belong in purpose-owned documents; active tasks and delivery history
belong in GitHub issues or the governed task ledger.

## Required Sections

Each `REPOSITORY-ENGINEERING-CONTEXT.md` must include:

1. `Repository Role`
2. `Business And Domain Responsibility`
3. `Current-State Summary`
4. `Architecture And Module Map`
5. `Runtime And Integration Boundaries`
6. `Repo-Native Commands`
7. `Validation And CI Expectations`
8. `Standards And RFCs That Govern This Repository`
9. `Known Constraints And Implementation Notes`
10. `Context Maintenance Rule`
11. `Cross-Links`

## Cross-Link Requirements

Each repository-local document must link back to:

1. `lotus-platform/context/LOTUS-QUICKSTART-CONTEXT.md`
2. `lotus-platform/context/LOTUS-ENGINEERING-CONTEXT.md`
3. `lotus-platform/context/CONTEXT-REFERENCE-MAP.md`

## Writing Rules

Repository-local documents should:

1. stay concrete and operational,
2. prefer current-state truth over aspirational language,
3. describe established local patterns and real commands,
4. avoid restating broad platform policy unless local interpretation is needed,
5. be updated when repository behavior, ownership, commands, or dominant patterns change.
6. route task-specific reading by explaining when and why a deeper source is needed,
7. summarize current posture without enumerating implementation chronology,
8. use repository-relative or canonical links and defined placeholders instead of personal paths.

They should not contain PR timelines, completed-issue diaries, transient CI status, repeated
service inventories, or detailed standards already authoritative elsewhere. Git history preserves
removed historical context when obsolete entries are consolidated.

## Maintenance Rule

Each repository-local document must state when it should be updated.

At minimum, it must require updates when:

1. repository responsibilities change,
2. commands or validation flow change,
3. runtime boundaries or major integrations change,
4. dominant implementation patterns change,
5. current-state rollout posture materially changes.
