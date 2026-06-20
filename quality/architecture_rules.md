# Architecture Rules

`lotus-platform` is a platform governance and automation backend. Its executable backend surface is
Python and PowerShell automation, validators, contracts, and CI lane entrypoints rather than a
business-domain HTTP API.

Rules for this refactor:

1. validators and generators should keep parsing, policy, rendering, and file-writing concerns explicit,
2. reusable policy should live in platform contracts, standards, or shared automation modules,
3. generated artifacts must not become hand-edited source truth,
4. repo-check entrypoints must stay aligned with GitHub workflow lanes,
5. broad framework or runtime dependencies require a documented enterprise-readiness reason.
