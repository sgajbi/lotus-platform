# CI Quality Gates

The enterprise refactor starts with report-only quality measurement. Gates should become blocking
only after the signal is deterministic, low-noise, locally runnable, and tied to a clear engineering
failure mode.

Initial gate posture:

1. `automation/generate_enterprise_backend_quality_baseline.py --check` is wired into
   `automation/Invoke-PlatformRepoChecks.ps1` to keep the quality reporting surface present,
2. baseline metrics remain report-only while the refactor identifies stable thresholds,
3. future blocking gates should prefer architecture-boundary drift, first-party security findings,
   OpenAPI/vocabulary drift, duplicate implementation hotspots, and unsafe production patterns.
