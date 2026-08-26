# Gate Liveness Standard

The promotion standard above decides *whether a signal deserves a gate*. It does not establish that
a gate which exists is alive. Every rule below was violated somewhere in the estate by a gate that
had passed the promotion standard, so treat this as a separate check, not a restatement.

A gate is alive only if all five hold. Verify each by observation, never by reading the target name.
Rules 1-4 ask whether a verdict is *produced*; rule 5 asks whether it arrives in time to matter.

1. **Reachable.** Some blocking lane invokes it - through `make check`, `make ci`, or an explicit
   workflow step. A `*-gate` target that appears only in `.PHONY` and its own definition is dead
   governance: the Makefile advertises a rule that never runs.
2. **Capable of failing.** The command returns non-zero on a finding. Check the tool, not the
   target name. `radon cc` and `radon mi` have no failing exit code in any mode; `trivy` returns 0
   unless given `--exit-code 1`; `|| true`, `; true` and a `-` prefix on a make recipe line all
   discard the verdict.
3. **Fail-closed on empty input.** A gate that inspected zero files must fail. An absent source
   root, a lane running from the wrong working directory, or a glob that matches nothing must be
   distinguishable from a clean tree.
4. **Observed to have run.** A correct, blocking gate on a trigger that never fires has produced no
   verdict. Check run history, not configuration.
5. **Ordered before the act it governs.** A gate that produces its verdict after the irreversible
   step - publishing, signing, tagging, deploying - reports rather than prevents. Failing the run
   afterwards is not a compensating control, because nothing un-publishes.

### Rule 5 has a distinct tell

Rules 1-4 are found by asking *"did this produce a verdict?"* Rule 5 answers **yes** and still
prevents nothing, so it survives that question. Find it by asking instead: **what is the first
irreversible act in this lane, and does the gate run before it?**

`lotus-risk#216` and `#241` are the same workflow. Fixing the trigger made the gate run for the
first time in seven weeks - and it failed, with the image already in the registry. Rule 4 was
satisfied and the outcome was still an unsigned, unattested, vulnerable artifact available to
consumers. That is why this is a separate rule rather than a footnote to rule 2: a gate can be
reachable, capable of failing, fail-closed, observed to run, and still be a report.

### The failures this prevents

The first four failures are invisible in the place people look. A dead gate, a gate that cannot
fail, and a gate that never ran are each **indistinguishable from a passing gate** in the Actions UI
and in a Makefile read. Absence of a gate is visible; a gate that does nothing is not - which makes
these worse than the gap they appear to close, because an audit asking "does this repository enforce
X?" gets `yes`. Rule 5 is visible only after the action has already escaped the control boundary.

### Measured instances

| rule | instance |
| --- | --- |
| Reachable | `lotus-performance#477` - `container-vulnerability-gate` written with `--exit-code 1`, invoked by no target and no workflow, while CI runs the `--exit-code 0` report beside it |
| Capable of failing | `lotus-risk#225` and the same defect in `lotus-manage` - `complexity-gate` runs `radon cc`/`radon mi` from the blocking `ci` lane |
| Fail-closed on empty | `lotus-risk#232`; `lotus-platform#728` - the `monetary-float-guard` variant four repositories run reports success with no `src/` present |
| Observed to have run | `lotus-risk#216` - `image-release.yml` carrying the only container CVE gate, SBOM, signing and attestation had **0 runs** across 45 commits, because merges were performed under `GITHUB_TOKEN` |
| Ordered before the act | `lotus-risk#241` - the same `image-release.yml` pushes the image (`push: true`, line 52) before scanning it (`exit-code: 1`, line 80). A failing scan stops signing and attestation but does not un-publish, leaving the image present, pullable, **unsigned and unattested** |

Two adjacent shapes that produce the same "green means nothing" outcome:

- **A lane that dies before evaluating.** `lotus-risk#227` referenced a `trivy-action` tag that does
  not exist, so the release supply chain failed at step resolution and never scanned.
- **A gate whose scope is a subset of what it claims.** `lotus-platform#737` - a pull request based
  on a non-main branch runs a subset of the merge gate and reports success, in all nine
  repositories.

### Repository-native check

`automation/gate_liveness_audit.py` detects rules 1 and 2 statically, for one repository or the
whole fleet from `automation/repos.json`:

```powershell
python automation/gate_liveness_audit.py --repos-json automation/repos.json --fail-on-findings
```

Rules 3, 4 and 5 need empty-input execution, run history, and workflow-ordering review respectively,
so they remain explicit review obligations. When adding a gate, prove rule 3 the way any fail-closed
behaviour is proven: run it against an empty or absent input and observe a non-zero exit. For rule 5,
name the first irreversible action and prove every applicable gate precedes it; a quarantined
artifact promoted only after a passing verdict is the exception, not publish-first plus alerting.

The audit obeys rule 3 about itself - it exits non-zero when it inspected zero repositories or zero
gate targets, rather than reporting a vacuous pass.
