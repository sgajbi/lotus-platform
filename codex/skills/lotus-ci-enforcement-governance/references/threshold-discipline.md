# Threshold Discipline

**Baseline-derived** numeric thresholds come in two kinds that need **opposite** treatment. Applying
one discipline to the other has produced real defects in the estate, and the mistake is easy to make
in both directions.

A third kind is out of scope here and must not be treated as either: a **fixed policy threshold** -
a compliance limit, an SLO, or a target such as the `>=99%` meaningful-coverage bar. What separates
these from a ratchet or a band is not their **shape** - a fixed policy threshold is often a ratio,
as that example is - but their **source**: they are chosen independently of what the tree currently
measures. Shape cannot classify a threshold; ask where its value came from. Never re-bank one to the
measured value:
that replaces a policy decision with whatever the tree happens to be today, which is how a target
silently becomes a description.

## Contents

1. [A ratchet belongs at exact equality](#a-ratchet-belongs-at-exact-equality)
2. [A band must never sit on its edge](#a-band-must-never-sit-on-its-edge)
3. [When a threshold blocks legitimate work, suspect the classifier](#when-a-threshold-blocks-legitimate-work-suspect-the-classifier)
4. [Two failure modes to check while doing this](#two-failure-modes-to-check-while-doing-this)
5. [Documented thresholds are a second copy that drifts](#documented-thresholds-are-a-second-copy-that-drifts)

## A ratchet belongs at exact equality

A ratchet is a bound banked from a measurement: a ceiling on something bad, a floor on something
good. Bank it at the measured value with **zero headroom**.

**Re-bank in the direction that tightens.** A ceiling moves *down* to the new measurement; a floor
moves *up*. "Re-bank downward" is only correct for a ceiling - applied to a minimum test-family
breadth floor it would loosen the very gate it claims to tighten.

Headroom is slack the next change spends without anybody deciding to spend it. A ratchet that
regresses fails; a ratchet left above the measurement after an improvement has quietly given that
improvement away.

**An improvement must be banked in the change that produces it.** Assert the relationship, not the
number:

```python
assert declared == measured  # not `declared >= measured`, and not a copied literal
```

A literal pins a *value*; `declared == measured` pins a *relationship*, which stays true at every
future value. Repeating the literal in a second test trains people to update it mechanically, and an
assertion that is always updated mechanically has stopped being a check.

## A band must never sit on its edge

A band constrains a ratio between a floor and a ceiling — a test pyramid is the common case. A band
reached *exactly* is a trap: the next good change breaches it.

`lotus-risk` sat at integration `15.0463%` against a `15%` floor and e2e `3.0093%` against `3%`. At a
total of `866` both still pass (`15.0115%`, `3.0023%`); both first breach at `867`. The repository
was at `864`, so it had room for **two more unit tests, of any kind**, before CI turned red. The
next pull request added four.

So: for a ratchet, zero headroom is correct. For a band, zero headroom is a defect.

## When a threshold blocks legitimate work, suspect the classifier

This is the rule that matters most, because the tempting fix is always the wrong one.

A correctly-banked threshold that blocks good work is usually not evidence the bound is wrong. It is
evidence the gate is **measuring the wrong population** — and the gate is then punishing the
behaviour it exists to encourage.

Two measured instances, one week, two repositories, two different gates, one shape:

- **`lotus-performance#475`** — the test-taxonomy classifier assigned families by path substring and
  had no token for the workspace analytics surface, so 90 tests counted as `uncategorized`. Because
  the gate caps uncategorized tests, **adding any test to that surface turned CI red**, and the only
  way to go green was to edit a governance threshold. Classifying the surface moved uncategorized
  from `969` to `879`, and the ceiling was re-banked to `879` in the same change.
- **`lotus-risk#220`** — the test pyramid gate classified by *directory*, so 130 governance tests
  asserting about `pyproject.toml`, workflows and documentation counted as product unit tests.
  Adding CI-contract coverage made the product pyramid look worse. Correct classification moved
  integration from `14.98%` to `17.39%` and headroom from **−4 unit tests to 117**, without lowering
  a single bound.

Order of operations:

1. Fix the classification so the gate measures the population it claims to measure.
2. Re-bank the ratchet **in the direction that tightens**, in the same change, to the new measured
   value - a ceiling *down*, a floor *up*. Say which one you are moving. A classifier correction can
   raise the measured value of something good, and "re-bank downward" applied to a floor loosens the
   gate it claims to tighten.
3. Never lower a bound, widen an allowance, or add an exception to go green.

## Two failure modes to check while doing this

- **A classifier that over-matches tightens a ratchet silently.** Because `declared == measured`
  moves both numbers together, a token matching too much produces a *lower* ceiling, which reads as
  an improvement. The gate rewards the mistake. Assert what a classification rule matches, not only
  that it matches something.
- **A classification rule that matches nothing is inert.** Derive any guard over a rule set from the
  rule set itself rather than a hand-copied table — a hand-written list covers the entries somebody
  remembered to add. Deriving `lotus-performance`'s token guard from the classifier by AST took
  coverage from 4 tokens to 37 and immediately found two that matched no module at all.

## Documented thresholds are a second copy that drifts

A threshold restated in prose is a copy no gate reads. `lotus-performance#475` re-banked a ceiling
from `969` to `879` and left `969` standing in two durable references, so anyone following the
documented command got exactly the slack the change removed — **looser than enforced, which misleads
toward doing the wrong thing**.

Prefer deleting the copy over checking it: cite the target that declares the threshold. Where a
document must state a number, a check should compare it against the enforced value. Exclude
append-only dated records such as review ledgers, whose rows state the command as it was run at the
time and would be *falsified* by rewriting — and assert that any such exclusion really is a dated
history, so the exclusion list cannot become somewhere to hide live drift.

See `lotus-platform#734` for the estate view of this class.
