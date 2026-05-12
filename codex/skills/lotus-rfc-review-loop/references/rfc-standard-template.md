# RFC Standard Template (Lotus)

Use this structure when standardizing an RFC:

1. `# RFC NNN - <Title>`
2. Metadata table:
   - Status
   - Created
   - Last Updated
   - Owners
   - Depends On
   - Related Standards (lotus-platform links)
   - Scope (In repo / Cross-repo / Archive candidate)
3. Executive Summary
4. Original Requested Requirements (Preserved)
5. Current Implementation Reality
6. Requirement-to-Implementation Traceability (table)
7. Design Reasoning and Trade-offs
8. Gap Assessment
9. Deviations and Evolution Since Original RFC
10. Proposed Changes
11. Business Outcomes
12. Supported-Features Ledger
13. Architecture Direction and Source-Authority Boundaries
14. Implementation Slices
15. Test and Validation Evidence
16. Enterprise Data-Mesh, Observability, and API Certification Requirements
17. Documentation, Wiki, and Supported-Features Requirements
18. Original Acceptance Criteria Alignment
19. Rollout, Compatibility, and Endpoint Retirement
20. Risks and Mitigations
21. Open Questions
22. Next Actions

Quality rule:
- Do not omit original requirements or implementation details that are needed to understand design intent and alignment.
- The standardized RFC must remain a comprehensive reference, not a short summary.
- For archived RFCs, keep migration rationale, destination ownership, and what remains relevant in current repo.
- For business application RFCs, use industry-standard domain vocabulary and include business
  outcomes that are useful to product, sales, operations, and engineering stakeholders.
- For new or reopened implementation-bearing RFCs, include the mandatory platform/scaffolding,
  cleanup, implementation proof, second-last hardening/review, and final closure slices.
- Supported-feature claims must stay separate from proposed target state until implementation,
  tests, API certification, live evidence, and wiki/source updates prove support.
- New features must strengthen enterprise posture; they must not increase endpoint sprawl,
  source-authority ambiguity, unbounded telemetry, weak error handling, or superficial tests.

Status values:
- Draft
- Approved
- Implemented
- Partially Implemented
- Deprecated
- Archived

Implementation classification values:
- Fully implemented and aligned
- Partially implemented (requires enhancement)
- Outdated (requires revision)
- No longer relevant to this repository
