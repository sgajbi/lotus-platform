# Lotus Codex Skills

This directory is the platform-owned source for Lotus-specific Codex skills introduced by RFC-0074.

The local Codex profile, normally `C:\Users\<user>\.codex\skills`, is a consumer of these artifacts. It is not the source of truth for Lotus skills.

## Scope

This directory contains:

1. Lotus domain and delivery governance skills,
2. platform automation and pulse-monitoring skills,
3. one supporting GitHub issue loop skill used by the Lotus validation lifecycle skill.

It does not own:

1. generic system skills,
2. user-local experimental skills,
3. plugin-provided GitHub skills,
4. non-Lotus skills that are not required by the Lotus workflow.

Unknown local skills must be preserved by future sync automation and must never be deleted by default.

## Manifest

Use [lotus-skill-manifest.json](./lotus-skill-manifest.json) as the governed inventory for:

1. skill name,
2. relative path,
3. ownership category,
4. whether the skill is directly Lotus-owned or a supporting dependency.

Future bootstrap automation must use this manifest to report:

1. present,
2. missing,
3. stale,
4. locally modified,
5. source unavailable.

## Maintenance Rules

When a Lotus skill changes:

1. update the skill under this directory,
2. update `lotus-skill-manifest.json` if skill ownership or path changes,
3. keep stale local-machine paths out of platform-owned skills,
4. avoid hard-coding user-specific workspace paths,
5. keep merge strategy guidance aligned to Lotus repository policy,
6. update tests that validate the governed skill inventory.

## Runtime Boundary

The platform-owned source of truth for Lotus skills is this directory.

The local Codex profile is synchronized from here through governed bootstrap automation:

1. `automation/Bootstrap-LotusDeveloperEnvironment.ps1`
2. `automation/Validate-LotusDeveloperEnvironment.ps1`

Local sync must preserve unknown non-Lotus skills.
