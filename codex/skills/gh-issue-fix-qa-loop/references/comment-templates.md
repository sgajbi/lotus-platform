# Loop Comment Templates

Use concise, structured issue comments for each iteration.

## QA Requested
```
Loop status: merged_pending_qa
PR merged: #<pr>
QA command: <command>
Expected: QA verifies fix and confirms no regressions.
```

## QA Failed
```
Loop status: qa_failed
QA run/evidence: <run-id or link>
Expected: <expected behavior>
Actual: <actual behavior>
Impact: <severity/scope>
Next: Dev follow-up fix and new PR.
```

## QA Passed / Close
```
Loop status: qa_passed_closed
QA run/evidence: <run-id or link>
Result: Verified fixed.
Action: Closing issue.
```
