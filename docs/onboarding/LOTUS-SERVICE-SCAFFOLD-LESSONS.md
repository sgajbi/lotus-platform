# Lotus Service Scaffold Lessons

This file records reusable scaffold lessons discovered while creating new Lotus
repositories. Promote repeated lessons into `New-Lotus-Service.ps1`,
`LOTUS-BACKEND-SERVICE-SCAFFOLD-GUIDE.md`, and platform standards instead of
solving them only in the generated app.

## 2026-06-21 - lotus-idea

1. Large RFC programs should use a per-RFC folder under `docs/rfcs/` so the
   master RFC and slice evidence files stay together. The top-level RFC index
   should link into that folder.
2. Generated evidence templates must not contain sensitive-content marker strings
   that the generated no-sensitive-content guard rejects. Use business-safe
   wording such as `raw HTTP payload`.
3. Generated Starlette/FastAPI response tests should coerce `response.body` with
   `bytes(response.body)` before decoding so mypy handles the `bytes |
   memoryview[int]` type correctly.
4. New service repositories should distinguish foundation-supported behavior
   from planned business capability in README, wiki, demo claims, and
   supported-features from the first commit.
