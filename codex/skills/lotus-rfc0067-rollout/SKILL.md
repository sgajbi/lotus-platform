---
name: lotus-rfc0067-rollout
description: Use when rolling out RFC-0067 OpenAPI quality, API vocabulary inventory, and no-alias governance for a Lotus application, then syncing inventory into lotus-platform and running cross-app vocabulary validation.
---

# Lotus RFC-0067 Rollout

Use this skill when implementing RFC-0067 for a Lotus app that is not yet aligned.

## Inputs

- Target app repo path (for example `<workspace>\lotus-performance`)
- Platform repo path (`<workspace>\lotus-platform`)
- App name (`lotus-performance`, `lotus-gateway`, etc.)

## Workflow

1. Baseline and gap scan:
- run app OpenAPI gate and contract scans
- search for alias patterns in source:
```powershell
rg -n "alias=|populate_by_name|model_dump\(by_alias=True\)|validation_alias|serialization_alias|AliasChoices" <app>\app <app>\core <app>\engine <app>\adapters <app>\main.py
```

2. Implement app-level controls:
- strengthen `scripts/openapi_quality_gate.py` to require:
  - operation `summary`, `description`, `tags`
  - success and error responses
  - schema property `description` and `example(s)`
- add `scripts/no_alias_contract_guard.py`
- add `scripts/api_vocabulary_inventory.py` with:
  - generation mode
  - `--validate-only` drift mode
  - validations for RFC-0067 invariants
- wire Makefile targets:
  - `no-alias-gate`
  - `api-vocabulary-gate`
  - include both in `check`/`ci`

3. Canonicalize contracts:
- remove alias usage from API-facing request/response/query contracts
- use snake_case contract fields and parameters
- update impacted tests and fixtures

4. Ensure OpenAPI completeness:
- if schema gaps are broad, add deterministic enrichment in app code and test it
- add/extend unit tests so enrichment logic is covered and stable

5. Generate app inventory artifact:
```powershell
python scripts/api_vocabulary_inventory.py
python scripts/api_vocabulary_inventory.py --validate-only
```
- store at:
`docs/standards/api-vocabulary/<app>-api-vocabulary.v1.json`

6. Run app gates:
```powershell
make check
make ci-local
```

7. Sync to platform:
- copy inventory to:
`lotus-platform/platform-contracts/api-vocabulary/<app>-api-vocabulary.v1.json`
- update `lotus-platform/platform-contracts/api-vocabulary/README.md`
- run cross-app gate:
```powershell
python lotus-platform/platform-contracts/api-vocabulary/validate_api_vocabulary_catalog.py
```

8. PR readiness:
- include app code + app inventory + platform inventory sync
- include evidence of:
  - `no-alias` pass
  - OpenAPI quality pass
  - app inventory drift check pass
  - platform cross-app validator pass

## Notes

- Keep endpoint usage rows in inventory free of duplicated attribute metadata.
- Preserve fallback compatibility logic only if needed for upstream transition; avoid alias support in contract models.
- If a monetary-float allowlist uses line-sensitive findings, refresh it only when approved and explain why.
## Continuous Skill Improvement

At the end of any meaningful use of this skill, decide whether the work exposed a repeatable failure
mode, missing step, weak trigger, validation gap, or context-routing gap. If yes, update the
platform-owned skill source under `lotus-platform/codex/skills/<skill-name>` or its relevant
reference/script in the same delivery slice when the improvement is small and safe. For broader
learning, create a focused follow-up issue or PR instead of relying on chat memory.

Use this decision order:

1. tighten this skill when future agents need different behavior;
2. update `context/LOTUS-SKILL-ROUTING-MAP.md` when routing or overlap changed;
3. update central or repo-local context when source-of-truth changed;
4. add or adjust validators, scaffolds, or gates when deterministic enforcement is better than prose;
5. record an explicit no-change decision in PR evidence, the review ledger, or the task ledger when no durable update is justified.


