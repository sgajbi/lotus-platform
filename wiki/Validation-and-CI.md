# Validation and CI

## Lane model

`lotus-platform` uses:

1. `Remote Feature Lane`
2. `Pull Request Merge Gate`
3. `Main Releasability Gate`
4. `Platform End-to-End Validation`

## Repo-native command mapping

- feature lane:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane feature`
- PR merge gate:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane pr-merge`
- main releasability:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformRepoChecks.ps1 -Lane main-releasability`
- platform validation lane:
  `powershell -ExecutionPolicy Bypass -File automation\Invoke-PlatformValidationLane.ps1 -ValidationProfile core-performance-green-lanes`

## What the gates protect

- central context and documentation contract integrity
- workflow and standards drift detection
- automation and validator correctness
- cross-repository governance posture
- reusable platform validation entrypoints

## Documentation contract posture

Platform documentation is partially protected by unit contract tests, including context-system and
automation README expectations.

When changing platform docs, run the targeted contract packs rather than assuming prose-only safety.

Before running the pack, classify the documentation change through:

- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](../context/TASK-ROUTING-GUIDE.md)

That keeps README, repo-local wiki, deep docs, and platform context from drifting into the wrong
surface even when the tests are green.

## High-signal targeted pack

```powershell
python -m pytest tests/unit/test_engineering_context_system_contract.py tests/unit/test_dev_ingress_status_automation_contract.py tests/unit/test_front_office_runtime_automation_contract.py -q
python automation/validate_engineering_context_system.py
```

## Related references

- [Lotus Documentation Layering](../docs/documentation/LOTUS-DOCUMENTATION-LAYERING.md)
- [Task Routing Guide](../context/TASK-ROUTING-GUIDE.md)
