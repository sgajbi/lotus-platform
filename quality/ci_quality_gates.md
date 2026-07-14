# CI Quality Gates

The enterprise refactor starts with report-only quality measurement. Gates should become blocking
only after the signal is deterministic, low-noise, locally runnable, and tied to a clear engineering
failure mode.

Initial gate posture:

1. `automation/generate_enterprise_backend_quality_baseline.py --check` is wired into
   `automation/Invoke-PlatformRepoChecks.ps1` to keep the quality reporting surface present,
2. `--check` compares stable material metrics in `quality/baseline_report.json` against the current
   repository, including source/Python file counts, Python function count, maximum complexity,
   maximum function length, and collected unit tests,
3. baseline metrics remain report-only while the refactor identifies stable thresholds, but stale
   checked-in quality evidence now fails deterministically,
4. exact total source-line count is not freshness-gated because it proved noisy during write/check
   sequencing; use it as context rather than a blocking freshness signal,
5. future blocking gates should prefer architecture-boundary drift, first-party security findings,
   OpenAPI/vocabulary drift, duplicate implementation hotspots, and unsafe production patterns.
