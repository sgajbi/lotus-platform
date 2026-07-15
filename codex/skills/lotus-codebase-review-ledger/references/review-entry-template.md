# Review Entry Template

Use this shape for each ledger row or expanded note.

## Required fields

- Review ID
- Date
- Scope / Pattern
- Status
- Findings
- Actions Taken
- Follow-up
- Evidence / Sign-off

## Example prompts for the reviewer

### Findings

- What concrete defect, debt, or drift was found?
- Why does it matter?
- Is it structural, correctness-related, performance-related, or test-related?

### Actions Taken

- What was changed in code?
- What tests were added or strengthened?
- What docs or RFCs were updated?

### Follow-up

- Is more refactor still needed?
- Is there duplicated logic still remaining?
- Is there a runtime or CI proof still missing?

### Evidence / Sign-off

- Commits
- PRs
- Test commands and results
- Reports or gate artifacts

### Cross-Repository Source Evidence

- Are all required sources represented by exact repository/ref/SHA-256 records?
- Does a canonical ordered collection digest fail closed on omission, substitution, or reordering?
- Is full producer-and-consumer validation distinct from consumer-only validation?
- Which evidence class applies, and which runtime, certification, publication, or promotion claims
  remain explicitly prohibited?
