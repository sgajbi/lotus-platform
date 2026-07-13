# Loop Comment Templates

Automation emits these structured fields. Preserve the same evidence when writing a manual update.

## Merged, Main Validation Pending

```text
Loop status: merged_pending_main_validation
PR merged: #<pr>
Main SHA: <sha>
Result: Merge complete; exact-main validation is not yet proven. Issue remains open.
```

## Merged Main

```text
Loop status: merged_main
PR merged: #<pr>
Exact main SHA: <sha>
Primary mainline validation: <name and run URL>
Security/repository-equivalent validation: <name and run URL>
Wiki decision/publication: <reference or explicit no-change decision>
Branch cleanup: <evidence>
Next: QA verification.
```

## QA Failed

```text
Loop status: qa_failed
QA run/evidence: <run ID or URL>
Failure: <expected versus actual and impact>
Result: Issue reopened and returned to active implementation.
```

## QA Passed And Closed

```text
Loop status: qa_passed_closed
QA run/evidence: <run ID or URL>
Result: Verified fixed on main. Issue closed with merged-main retained.
```
