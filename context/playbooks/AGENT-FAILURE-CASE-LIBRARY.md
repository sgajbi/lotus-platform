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

### 12. A rename outlives every sentence that described it

Contributed by the `lotus-render` / `lotus-performance` / `lotus-advise` seat.

**Claimed:** `lotus-performance`'s container supply-chain evidence was complete and its acceptance
workflow was documented for operators. The gate wiring had been reviewed and the unit lane was
green.

**Evidence:** consolidating two container scans into one folded the acceptance validation into
`make container-vulnerability-gate` and removed the fixable-only report. Seven documents still
directed operators to `make container-acceptance-gate`, for which `make -n` answers "No rule to make
target", and to a fixable-only artifact for which a repo-wide search finds no producer — the wiki,
the quality scorecard, the CI gate map, the refactor health report, the repository context and two
quality reports. Three more still described the runtime image as installing `requirements.txt` only,
after a second requirements file was added and retained so the licence inventory would cover the
shipped `setuptools`. Every one of those sentences was written while the design was still the
*planned* shape, and nothing re-read them when the shape changed. Found by review, not by any gate.

**Check:** when a change renames or consolidates a target, artifact, command or index, grep the old
name across `*.md`, `wiki/`, scorecards, gate maps and repository context *as part of that change*.
Grep the new name too: a document stating a property for one route family or backend and silent for
its sibling reads as a deliberate difference rather than an omission, which is worse than a stale
reference, because a reader concludes the asymmetry is the design. The trigger is the rename itself,
not a judgement that meaning changed — a rename is observable and "the meaning changed" is not.

Corroborated the same day in two seats within minutes of the rule being circulated, which is the
evidence that the trigger is actionable rather than merely true. In `lotus-report` the same grep
applied to a migration rename found the tenant-leading index shipped for PostgreSQL only, while the
SQLite schema — the default backend — still created the old unscoped shape; contributed by the
`lotus-report` / `lotus-risk` / `lotus-archive` seat. In `lotus-gateway` the grep for the *added*
name found the repository context naming trusted-caller identity derivation for one route family and
silent for the sibling that now does the same thing; contributed by the `lotus-gateway` seat.

**When the grep can become a checker, and when it cannot.** A rename is only mechanically checkable
when the **references** share a common shape *and* a **registry** resolves them — not when the
renamed thing does. `make container-acceptance-gate` qualifies because the Makefile is the registry
that says which targets exist; a 32-hex digest qualifies because its derivation is. A claim with no
registry to check against has no invariant, and needs a reviewer rather than a checker. That
correction matters because the first reading was the other way round: a renamed Make target looks
shapeless, so the rule appeared unrescuable — the renamed thing has no shape, the *reference* does.

Measured before being written down: 55 documented `make` targets against 65 real ones in
`lotus-performance`, two non-matches, both of them flags rather than targets, so one skip rule
sufficed. Falsified by reintroducing the real pre-fix wiki sentence, which fails naming
`container-acceptance-gate`. Contributed by the `lotus-render` / `lotus-performance` /
`lotus-advise` seat, correcting a condition from the `lotus-ai` / `lotus-idea` seat.

Three forms, weakest to strongest, agreed across three seats. **Enumerate and check** fails on
incomplete enumeration — a sweep for one identifier prefix missed two others in the same codebase.
**Pin each pair** works and costs maintenance per pair. **Assert the invariant** needs no enumeration
at all and covers instances added later by people who never read the rule.

### 13. Scoping reads turns a leak into a collision unless the keys carry the scope too

Contributed by the `lotus-ai` / `lotus-idea` seat.

**Claimed:** adding a tenant filter to every read completed a tenancy fix.

**Evidence:** `health_snapshot_id` was derived as `mh_<date>_<portfolio>`, and health snapshots
upsert on that id alone. Two tenants scoring the same portfolio on the same business date derive one
id, so the second write replaces the first's payload while leaving the first's tenant stamp in
place. Every read on that path is then correctly scoped and still wrong: one tenant reads the
other's data, and the other reads nothing. The asymmetry is what hides it — the victim sees
plausible data, and the loser sees an empty result indistinguishable from "no evidence yet".

**Check:** on any change that scopes reads, enumerate every derived identity on the path that
something **looks a record up by or writes on** — primary and surrogate keys, idempotency tokens,
cache keys, replay keys, and any hash used as a lookup or upsert target — and confirm each carries
the scope. Replay keys are the sharpest: a proof-pack id that *is* the replay key hands the second
tenant the first's evidence, and it presents as a legitimate replay rather than an error.

The distinction is collision-bearing versus integrity-bearing, and it matters in both directions. An
**integrity digest must not be scoped**: `lotus.content_hash` is defined in the platform vocabulary
as a source-owned evidence hash, so a consumer recomputes it from the evidence bytes it holds.
Salting it with tenant identity makes every such recomputation disagree, converting a working
integrity check into a permanent mismatch. Scope what is used to *find* a record; leave alone what is
used to *verify* one. A digest that is also a lookup key is the case to split rather than to salt.

Two traps once the scope is being added to keys. Joining is not encoding: `f"{tenant}_{mandate}"` is
ambiguous when either component may contain the separator, and as a primary key the collision
surfaces as a unique violation between two genuinely distinct records, raised on the key rather than
on the tenant-scoped conflict target, so it does not even present as a tenancy problem — hash a
length-prefixed component sequence instead. And never backfill a default tenant onto existing rows:
a nullable column with no backfill leaves pre-fence rows matching no equality predicate, so they are
reachable from no tenant rather than silently attributed to one, including a tenant literally named
`default`.

The falsification that proves this is pinned rather than assumed: replace the derivation with a
constant and confirm the tests claiming to check it now fail. Two did not.

### 14. An assertion is empty when both sides route through the same derivation

Contributed by the `lotus-ai` / `lotus-idea` seat.

**Claimed:** two tests in `tests/unit/dpm/proof_packs/test_proof_pack_builder.py` pinned that a
proof-pack id is derived from the tenant and run identity.

**Evidence:** each asserted
`pack.proof_pack_id == proof_pack_id_for_rebalance_run(tenant_id=..., rebalance_run_id=...)`, and
the builder computes that field by calling the same helper with the same arguments. The assertion is
`f(x) == f(x)`, which holds for every possible `f` — constant, identity or correct. Replacing both
derivations with the literal `"dpp_constant"` left both tests passing. What they actually asserted
was that the builder called the helper, which nobody doubted; they read as derivation checks only
because one side is an attribute access and the other is a call, and that asymmetry is the whole
disguise. Recomputing the expected value with the production helper is the move that feels rigorous,
because it avoids a brittle literal, and it is what converts the test into a tautology.

**Check:** for every assertion of the form `actual == derive(inputs)`, ask whether both sides route
through the same derivation on the same inputs. If they do, keep the convergence line and add a case
that must *not* converge — the convergence case proves the derivation is used, and the divergence
case proves it discriminates. The divergence input must be one that **would have collided** under the
defect being guarded against: an input the derivation never reads passes on a broken implementation
and proves nothing.

Run the two in order, because they answer different questions. The constant substitution is a
**detector**: a constant collides with everything, so it needs no judgement about nearness and it
answers whether the test reads the derivation at all. The near-collision case is a **specification**:
it answers whether the derivation discriminates on the component that matters, and it is the one that
stays in the suite because it names the defect. Running them the other way spends the expensive
judgement on tests that turn out not to read the derivation.

The constant probe is diagnostic and disposable — run it, learn from it, delete it. A suite that ends
up asserting against a constant derivation pins the probe instead of the property.

It detects only tests that route through the derivation at runtime. A test hard-coding the expected
literal also fails against a constant, but for the wrong reason: it would fail against any change at
all. So the probe reports "weak or literal" and the two still have to be told apart by reading. These
two were the recomputation kind; the previous version of the same assertion was the literal kind, and
it was weak for the opposite reason — one test, three states, two of them wrong.

That substitution is how these two were found, and the contributing seat notes they would have been
defended on inspection — which is the reason to run the probe rather than read the test.

Fixed in `lotus-manage` commit `5e443f12`; after adding the divergence half, the constant
substitution fails both tests.

### 15. A stated rule with no wiring reads as a satisfied rule

Contributed by the `lotus-ai` / `lotus-idea` seat, with the negative result from the
`lotus-render` / `lotus-performance` / `lotus-advise` seat.

**Claimed:** a codebase can hold a correct, well-explained statement of a rule and no enforcement
wiring at all. The statement is what stops you looking: you read it, recognise it as right, and move
on. This is distinct from a misconfigured or a skipped control — the code is correct, tested,
covered, and never reached.

**Evidence:** three instances in one `lotus-manage` pull request on 2026-09-07.
`require_mandate_tenant` normalised tenant ids, and its docstring explained why padding must not
create a second tenant; **none of the eight routes annotated with `MandateTenantId` called it**, so
`tenant_id=%20tenant-a` reached the store padded — reads missed rows under `tenant-a` while writes
persisted into a padded namespace nothing later reads. `X-Tenant-Id`'s own description said it
covered preview, create, source-check and selection, and two of the four were wired to a query
parameter, so a caller following the published contract received 422.
`validate_production_cutover_contract` refuses a production start when the persistence profile is
not PRODUCTION or migrations are unapplied; it is correct, tested, and referenced by nothing outside
its own unit test, verified by hand against `src/`, `scripts/`, the Makefile, every workflow and the
packaging entry points. Filed as `lotus-manage#678`.

**Check:** when you read a stated rule — in a docstring, a field description, a comment — and find
it convincing, grep for its enforcer *before moving on*. The trigger is the moment of being
convinced, because that is the moment that stops you looking. One named rule, one `grep -c`, in a
place you have reason to suspect. Zero call sites is the finding; one is worth reading. Two caveats
from running it: a function passed by reference rather than called, as in `Depends(f)` or
`AfterValidator(f)`, counts as zero and is a false positive, and a helper referenced *only* from
`tests/` is the true positive — test references are what make a dead gate look alive in coverage.

**Do not generalise this into a sweep.** Enumerating enforcement-named helpers and reading every
zero was tried across three repositories: four implementations, four distinct bugs, roughly one in
twenty signal, and every sampled candidate false. One pass reported *more* candidates after its
matcher was loosened, which is arithmetically impossible and was the only reason nothing was acted
on. "Is this called" is not textually decidable in Python — methods, dependency injection, framework
registration and dynamic dispatch all reference a function in forms a grep cannot separate from
coincidence, and a checker whose false positives outnumber its findings gets someone to "fix" a
correct one. The trigger has to be a human moment of conviction, not a schedule.

**Repair pattern:** put the rule in the type rather than in a helper someone must remember to call.
Normalisation as an `AfterValidator` on the annotated type is shared by query parameter, header and
body, so a ninth surface added in six months gets it by construction. That beats checking that the
call sites agree, because there is no call site to omit.

### 16. A value's construction is not the decision path

Contributed by the `lotus-ai` / `lotus-idea` seat.

**Claimed:** adding the tenant to `create_wave_request_hash` closed a cross-tenant replay in
`lotus-manage`. The claim was made to a reviewer in writing, on a thread of PR #676.

**Evidence:** it did not. The hash was written on save and never compared on the lookup path, which
returned on the caller-chosen key alone, so the tenant the hash carried never entered the replay
decision and the second tenant was still handed the first's wave — indistinguishable from a
legitimate replay. The derivation had been read, the tenant seen in it, and a property asserted
about a branch that had not been opened. Review caught it; the false security claim stood in the
record for several hours. Fixed in commit `b8d21bc6`, by deriving the stored mapping key from the
tenant and the caller's key rather than by comparing the hash — refusing the second tenant would
have disclosed that another tenant holds the key, so the failure mode is silence and the second
tenant creates its own wave. Pinned afterwards by `fbd938b7`, which asserts the upgrade path rather
than describing it.

**Check:** when claiming a fix closes a vulnerability, name the exact line where the decision is made
and confirm the scoped value reaches it. "The key now contains the tenant" is a fact about a string;
"the lookup refuses another tenant" is a fact about a branch. Only the second is the claim, and the
two are easy to mistake for each other because the first is visible in the diff and the second is
not.

### 17. Retiring a compromised key is not withdrawing it

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat.

**Claimed:** rotating a signing key retains the outgoing key so decisions it already signed stay
verifiable, and withdrawing a key removes it so nothing it signed verifies. Operators treat these as
the same operation with different urgency.

**Evidence:** they are different operations with opposite effects. `lotus-archive` publishes its
verification keys with `not_before_utc` and `not_after_utc`, and retirement moves a key into the
retired set with a closed window — it stays published and keeps verifying every decision inside that
window, which is correct for a rotation and is why history survives one. Apply the same operation to
a **compromised** key and it stays trusted for its entire historical window. The operation succeeds,
the service starts, the published document is well-formed, and every consumer keeps verifying
decisions signed by a key whose private half may be held by someone else. Nothing reports it, because
there is no state to inspect that differs from a correct retirement: the state *is* a correct
retirement. It is a control whose failure mode is a clean green.

The required action is withdrawal: everything the key ever signed must stop verifying, because once
the private half is loose the signature evidences nothing. Blast radius is every decision the key
ever signed, for as long as anyone consults the bundle.

**Withdrawal does not mean deleting the entry.** The governed discovery contract,
[`lifecycle-authority-key-discovery.schema.json`](../../platform-contracts/lifecycle-authority/lifecycle-authority-key-discovery.schema.json),
carries `status` with `active`, `rotated` and `revoked` precisely so a withdrawn key stays published
and says what happened to it. Removing the entry produces "this key was never ours", which is
indistinguishable from an ordinary trust-distribution miss — and that collapses the very distinction
the check below requires. A key is withdrawn by publishing it as `revoked`, so a consumer refuses
everything it signed *and* can say why.

The two operations differ in what they do to verification, not in whether the key stays published:
a rotated key keeps verifying inside its closed window, and a revoked key verifies nothing at any
time.

Underneath it sat a second instance of the same silence: the published windows had no reader. The
verify function had no parameter a window could reach it through, so retention was not merely
unhelpful but exploitable — a retained key vouches for a decision dated after it stopped signing.
The shape recurs one layer along, which is the reason to look again after fixing it: a bundle that
publishes a status a verifier never reads has the same gap as one that publishes a window nobody
reads.

**Check:** two parts, and the second is the one usually skipped. On withdrawal, assert that a decision
which **previously verified now fails**, with a reason naming the key as revoked rather than as
absent — asserting only that the key is gone from the response passes against a consumer that never
consults the bundle, and asserting an unpublished-key reason accepts an implementation that deleted
the entry.
And assert the refusal **reasons are distinguishable**: a boolean verifier cannot separate "this key
was ours and had retired before this decision claims to have been issued", which is evidence of
forgery or back-dating, from "this key was never ours", an ordinary trust-distribution miss. An
operator handling a suspected compromise reads the reason, not the boolean.

### 18. A gate whose scope is a hand-maintained list reports green for what it never looked at

Contributed by the `lotus-report` / `lotus-risk` / `lotus-archive` seat, with a second instance from
the `lotus-platform` seat.

**Claimed:** two gates were protecting what they named. Both passed on every run.

**Evidence:** `lotus-archive`'s `scripts/migration_gate.py` checks a hand-maintained `REQUIRED_FIELDS`
set against the migration DDL — **15 of the 58 fields** on the document metadata model. Meanwhile the
PostgreSQL repository derives its column list from that model and names every field in the INSERT, so
a model field with no column is not a degraded feature: it is **every write failing**. It is invisible
in CI, because the suites run against an in-memory repository with no schema, so a fully green run
proves nothing about whether the column exists. It nearly landed: `make migration-gate` passed before
the migration for a new field was written, because that field was not one of its fifteen names, and
the migration existed only because someone had read the repository code.

The second instance is `lotus-platform`'s adopted branch-protection checker, which compared a
hard-coded scalar allowlist and ignored four controls — two of which decide whether `main` can be
merged at all.

Both were measured as **liveness gaps and not live defects**: all 58 columns exist today and all four
protection fields match their declared expectation. The finding is that neither gate could have said
so. Note the narrower claim — matching the declared expectation is not the same as being the right
posture, and one of those four, unsigned commits being permitted, is a policy position rather than a
correct default. An entry that blurred the two would be doing what this entry is about.

**Check:** wherever a gate's scope is a list, ask what authority the system already derives the same
thing from — a model, a registry, a manifest — and derive the check from that authority instead of
restating it. The tell is that the two lists are *nearly* identical, which is exactly why nobody
notices they have diverged.

Falsify against a real breach, not against the current tree: add a field with no migration and confirm
the gate fails **naming that field**, then add the migration and confirm it passes. Asserting the gate
exits zero today proves nothing — it already did that while measuring a quarter of the fields.

Checking whether the pattern generalises is part of the check. It did not extend to two sibling
repositories: neither has a migration gate, and one names its columns explicitly rather than deriving
them, so a new field there fails to persist rather than breaking every write. Different exposure,
milder, not the same finding — so it stayed scoped rather than becoming an estate sweep.

## Contributing

Add an entry when a failure would otherwise survive only in one session's memory and would change
how a future agent approaches the task. Follow the entry contract above, name the contributing seat,
and keep the case concrete enough to reproduce.

Do not add an entry because one implementation was imperfect. Use
[Skill And Context Promotion](./AGENTIC-CODING-QUALITY-EVALUATION-LOOP.md#skill-and-context-promotion)
to decide whether the lesson instead belongs in a skill, a standard, or a deterministic gate — a case
that can become a gate should become one, and this library is where it waits until it can.
