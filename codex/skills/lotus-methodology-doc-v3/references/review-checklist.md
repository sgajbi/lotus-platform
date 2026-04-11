# V3 Review Checklist

Mark all items before finalizing a metric doc.

## Structure
- [ ] All required sections exist in correct order.
- [ ] No placeholder or generic wording remains.

## Correctness
- [ ] Formulas match implementation behavior.
- [ ] Units are explicit (pp vs decimal) and consistent.
- [ ] Annualization/risk-free/MAR/frequency logic is documented when relevant.

## Determinism
- [ ] Algorithm steps are explicit and reproducible.
- [ ] Alignment rules are explicit for multi-series metrics.
- [ ] Edge-case behavior is explicitly documented.

## Validation/Errors
- [ ] Insufficient data behavior documented.
- [ ] Zero denominator/zero variance behavior documented.
- [ ] Alignment-empty behavior documented (if applicable).

## Worked Example
- [ ] Example has concrete numeric inputs.
- [ ] Intermediate values shown in a table.
- [ ] Final metric value shown with arithmetic.
- [ ] Final value mapped to exact output field(s).
