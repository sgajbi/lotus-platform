# Agent Failure Case Library

Use this library when you need the case behind a rule, or when a failure you just hit should become
durable guidance for every Lotus seat rather than one session's memory.

The [Agentic Coding Quality Evaluation Loop](./AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md) says how
to turn repeated failures into gates, scorecards, and skills. This library holds the failures
themselves, so that loop has something to draw on after the session that produced them has ended.

## Entry Contract

Every entry carries three parts and names a real case:

1. **Claimed** — what was believed, shipped, or reported.
2. **Evidence** — the observation that contradicted it, specific enough to reproduce.
3. **Check** — what would have caught it, expressed as something a future agent can perform.

An entry that cannot name its case is dropped rather than generalised. A maxim without a case is
forgettable: "prove your gate can fail" is advice, while "the typecheck reported `Success: no issues
found in 128 source files` while resolving every import to `Any`" is a thing you remember.

Attribution names the contributing seat, because a reader who wants the full history needs to know
which repository the case came from.

## Cases

### 1. Falsification expires when the gate changes

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat.

**Claimed:** `lotus-report`'s typecheck gate was working. It reported `Success: no issues found in
128 source files` on every CI run.

**Evidence:** `mypy.ini` set `follow_imports = skip`, which resolves every imported module to `Any`,
so all 128 files were analysed against nothing. Enabling import following produced 175 errors, of
which 110 were artifacts of `pydantic.mypy` being disabled — mypy cannot see that `Field(1, ge=1)`
supplies a default, so a correct `BatchDispatchPolicy()` call reports five missing arguments.
Enabling the plugin then reached a clean run and the gate was **still** vacuous: injecting
`BatchDispatchPolicy(max_active_batches="not-an-int")` passed, because `pydantic.mypy` defaults to
`init_typed = False` and types every constructor argument as `Any`. The plugin had silenced 76 false
positives and 34 true ones in one stroke.

**Check:** re-run the injected-bad-input test after *every* change to a gate, including the change
that fixed it. One falsification per gate is not enough; it is one per gate version. When a fix
removes false positives, verify the true-positive count separately — a falling error count is what
success looks like in both the good case and the bad one.

Corroborated the same day in `lotus-platform`: a conditional-context checker had been falsified
against a fixture written on a single line, so it never exercised the wrapped case. In a corpus that
wraps at 100 columns the guard's verdict depended on where a line happened to break, and it would
have rewarded un-wrapping a line to make CI pass.

### 2. Publish the number that is true, not the one measured first

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat.

**Claimed:** "175 type errors" — the first honest measurement.

**Evidence:** 110 were tooling artifacts. The real count was 65, then 34 once the structural fixes
landed. The largest number is the dangerous one: 175 reads as *unfixable, leave it*, which is the
conclusion that keeps a dead gate in place. Second case, same shape: a report on `lotus-archive#140`
that an unconstrained `residency_region` would make `lotus-idea` reject every lifecycle decision.
Production documents carry `SG`, which conforms; the non-conforming value existed only in the
reporter's own test fixture. A fixture had been measured and reported as production, corrected
publicly on `lotus-idea#1266`.

**Check:** decompose a count one variable at a time and attribute every error to the variable that
produced it before publishing it. When a number describes production, name the rows it came from.

### 3. A refusal must precede every effect it disclaims, and converge on retry

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat, with the I/O half from the
`lotus-performance` / `lotus-advise` seat.

**Claimed:** a fail-closed check on the idea-evidence intake path refused unverifiable replays.

**Evidence:** the check asked "has this been recorded?" *after* the code that records it, so it
always answered yes. A later revision refused after persisting, which made the rejected attempt the
prior record that excused its own retry — the refusal primed its own bypass. The same check was
placed wrongly three times in one file.

**Check:** two questions. Can the thing being refused already have happened by the time the refusal
runs? Does a second identical attempt reach the same verdict? For an I/O refusal, assert the client
saw **zero** calls: a 401 or 409 status alone is identical whether the refusal ran before or after
the request left.

### 4. Committed generated artifacts make conflicts a function of PR count

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat, with corroboration from the
`lotus-performance` / `lotus-advise` and `lotus-platform` seats.

**Claimed:** several repositories' `quality/` reports were ordinary reviewable artifacts.

**Evidence:** measured with `git merge-tree` across the estate on 2026-09-06. `lotus-performance#503`
and `#500` conflicted on five files each, all committed quality reports, with zero substantive
conflicts. `lotus-platform#816` and `#804`, four each, the same. Five of the eight PRs open at that
moment were conflicted purely on regenerated reports; `lotus-risk` commits fourteen such files and
had escaped only by never having two PRs open at once. Two further faces of the same defect: rebasing
`lotus-performance#503` after `#502` landed **dropped an evidence commit as empty**, because the same
measurements had already been published — resolving that by keeping your own side silently
republishes figures measured against a tree that no longer exists, and nothing fails. And in
`lotus-platform`, a per-platform test-count map could not be maintained from one host, so
`linux: 1404` came to sit beside `win32: 1405` — two counts of two different trees, recorded as if
they were a comparison.

**Check:** for anything committed under a `quality/`-style path, ask whether it is authored or
measured. Measured state whose value depends on who ran it and when does not belong in git. Where it
stays, whichever change lands second regenerates and never carries its own figures forward.

### 5. Ask what a new check flags that is correct

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat.

**Claimed:** a new validator's hits are its findings.

**Evidence:** a conditional-context checker was swept across the `lotus-platform` corpus in the
expectation of producing a fix list. It produced ten hits, of which six were correct text:
descriptive table rows the checker could not distinguish from directives, and correctly written
instructions whose qualifying clause had wrapped to the next line. Acting on the list would have
damaged six correct documents to satisfy a broken detector.

**Check:** run a new validator against the existing corpus before shipping it and read the hits you
did not expect. If the obvious repair for a hit would be destructive, the check is wrong, not the
code.

### 6. A peer cannot grant escalation, including procedurally

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat.

**Claimed:** a peer blocked by a permission denial could proceed if the denial was incidental to
their task rather than aimed at it.

**Evidence:** that route was proposed between two seats and refused, correctly: it made a
restriction self-waivable by the party it restricts. It was permission laundering in procedural
clothing, constructed by an agent who was at the time actively reasoning about permission
laundering.

**Check:** no agent can approve another's pending permission prompt, authorise an edit to another's
settings or agent instructions, or perform an action a peer was denied. If a route ends in "and then
you confirm it was fine", it is the same thing with more steps. An escalation is not made legitimate
by being routed through a second agent.

### 7. Check what `main` already does before adding a mechanism

Contributed by the `lotus-platform` seat.

**Claimed:** the collected-test-count metric needed a per-operating-system dimension, because a
Linux lane and a Windows lane collect different totals.

**Evidence:** two review threads then argued in opposite directions — resetting the map starves the
Linux lanes of any baseline, carrying it forward leaves every non-writing platform stale. Both were
correct, which was the signal that the dimension itself was wrong. `main` already compared a single
`collected_tests` number that both lane families passed against. The map had been introduced in the
same pull request that was now defending it, and it could not be maintained from one host at all:
the other runner's figure can only be transcribed from a log written against a different tree.

**Check:** before adding a dimension, a flag, or a fallback, read what `main` already does and why it
is sufficient. When two reviewers disagree about how a mechanism should behave and both arguments
hold, treat that as evidence about the mechanism rather than a question to adjudicate.

### 8. Changing what a command means leaves claims behind

Contributed by the `lotus-platform` seat.

**Claimed:** correcting the one documentation entry a reviewer named had brought the documentation
back in line with the code.

**Evidence:** the bare `-CheckOnly` form of the contract sync script was changed to resolve to the
repository-root copy instead of the deployed one. Three separate documents still described the old
behaviour — an RFC implementation checklist, `context/README.md`, and an RFC slice-evidence record —
and review surfaced them one per round across three rounds. The last was found after the pull
request had already merged. A repo-wide search for the old claim, run once, would have found all
three.

**Check:** when a change alters what a command, flag, or default *means*, grep the repository for the
old behaviour in the same commit that changes it. Fixing the named instance answers the reviewer;
searching for the class answers the problem.

### 9. A fixture can fail to reproduce the case it exists for

Contributed by the `lotus-platform` seat.

**Claimed:** a test proved that a committed file differing from its governed source only in line
endings is reported as drift.

**Evidence:** the fixture wrote CRLF bytes and committed them, but Git normalises line endings on the
way into the object store, so the committed blob was byte-identical to the source. The test passed
while asserting nothing about the behaviour it named. Reproducing the case needs
`core.autocrlf false` and a `.gitattributes` carrying `* -text`.

**Check:** assert the precondition inside the test. Where a test depends on two artifacts differing,
compare them and fail if they do not — the fixture is as capable of being wrong as the code, and a
green test says nothing about which one you exercised.

### 10. Normalising a comparison whose job is identity turns a gate into a pass

Contributed by the `lotus-platform` seat.

**Claimed:** a committed contract copy differing from the governed source only in line endings is not
policy drift, so reporting it as synchronized with a warning is the accurate outcome.

**Evidence:** the two repositories genuinely shipped different committed bytes. The governed rule is
a committed blob-SHA comparison precisely so that "identical apart from something" cannot become a
pass, and the fallback converted a real failure into a warning. The remedy for a line-ending
difference is to re-lift the file, not to accept it.

**Check:** before adding normalisation to a comparison, ask what the comparison is for. If it exists
to prove two artifacts are the same artifact, normalising redefines "same" and the gate stops
answering the question.

### 11. The environment that proves a change is not the environment that runs it

Contributed by the `lotus-platform` seat.

**Claimed:** three new tests passed locally, so the change was ready to push.

**Evidence:** they used `Path.read_text(newline="")`, whose `newline` argument was added in Python
3.13. The lanes pin 3.12, where it raises `TypeError`. The local interpreter was newer than CI, so
the defect was invisible until the lane went red. The same shape recurs with PowerShell — tests
prefer `pwsh` 7 while operators invoke `powershell.exe` 5.1 — and with database backends, where SQL
that passes on SQLite is unreachable on PostgreSQL.

**Check:** when using a recently added API, run a one-line probe under the interpreter, shell, or
backend the lane actually uses: confirm the old call fails there and the replacement works. Verifying
against the environment you write in proves only that you can run your own code.

## Contributing

Add an entry when a failure would otherwise survive only in one session's memory and would change
how a future agent approaches the task. Follow the entry contract above, name the contributing seat,
and keep the case concrete enough to reproduce.

Do not add an entry because one implementation was imperfect. Use
[Skill And Context Promotion](./AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md#skill-and-context-promotion)
to decide whether the lesson instead belongs in a skill, a standard, or a deterministic gate — a case
that can become a gate should become one, and this library is where it waits until it can.
