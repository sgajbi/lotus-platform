# V3 Methodology Template

Use this exact section order:

1. `## Metric`
2. `## Endpoint and Mode Coverage`
3. `## Inputs`
4. `## Upstream Data Sources`
5. `## Unit Conventions`
6. `## Variable Dictionary`
7. `## Methodology and Formulas`
8. `## Step-by-Step Computation`
9. `## Validation and Failure Behavior`
10. `## Configuration Options`
11. `## Outputs`
12. `## Worked Example`

## Worked Example Requirements
- Use concrete numeric sample inputs.
- Include a table for key intermediate calculations.
- Show final aggregation step.
- Map final number(s) to exact response field name(s).

## Formula Style
- Use plain text math consistently.
- Define every symbol in `Variable Dictionary`.
- State interpolation rule when quantiles are used.
- State estimator choice when variance/std is used (`ddof=1` where applicable).
