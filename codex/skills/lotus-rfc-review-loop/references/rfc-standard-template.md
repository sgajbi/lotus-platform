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
11. Test and Validation Evidence
12. Original Acceptance Criteria Alignment
13. Rollout and Backward Compatibility
14. Open Questions
15. Next Actions

Quality rule:
- Do not omit original requirements or implementation details that are needed to understand design intent and alignment.
- The standardized RFC must remain a comprehensive reference, not a short summary.
- For archived RFCs, keep migration rationale, destination ownership, and what remains relevant in current repo.

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
