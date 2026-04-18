# Development Workflow

## Normal working loop

1. load the smallest correct context set
2. use repo-native commands first
3. run targeted local checks
4. push early for GitHub-backed heavy validation
5. monitor asynchronously and fix forward
6. update context, skills, or validators when learning becomes durable

## Common commands

```powershell
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature
powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge
python -m pytest tests/unit -q
python automation/validate_engineering_context_system.py
python automation/validate_lotus_skill_alignment.py
```

## Documentation workflow rule

For `lotus-platform`, README and wiki changes are not free-form prose work. They must stay aligned
with:

- the current repo role and boundaries
- central context system cross-links
- onboarding and automation references
- documentation contract tests

Use:

- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](../context/TASK-ROUTING-GUIDE.md)
- [Lotus Skill Routing Map](../context/LOTUS-SKILL-ROUTING-MAP.md)

When the task is specifically README/wiki standardization across Lotus repos, use the governed
`lotus-readme-wiki-governance` workflow instead of treating the change as ordinary prose cleanup.

## Async GitHub posture

Prefer targeted local proof plus GitHub for the heavy matrix.

Useful commands:

```powershell
gh pr checks <pr-number> --watch=false
gh run list --limit 10
gh run view <run-id> --log-failed
```
