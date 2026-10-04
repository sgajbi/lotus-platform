# Worked composite specification examples

All data are synthetic. These 18 examples are **SPECIFICATION_ORACLE / PLANNED**, not executed Lotus API responses or certified method support. The original [oracle JSON](source/05_composite_numerical_oracles.json) is immutable. The [ledger](implementation-ledger.v1.json) binds each example to exact requirements, scenarios, owning issues and planned executable test names. Owners supply actual source-safe routes, DTO serializers or deterministic no-I/O factories when implemented, following the [endpoint parity standard](../../docs/standards/Endpoint%20Example%20Parity%20Standard.md).

Returns are decimal returns: 0.01 means 1%. Monetary units and estimator/fee/currency/time/approval identity must be declared by the owning method. Numeric comparison tolerance is absolute 10^-12 for specification calculations; categorical outcome, identity, completeness and approval state require exact equality. Display rounding does not change retained precision. The document guard only checks fixture integrity, traceability and exact documented literals. It contains no financial engine.

## OR-01

Beginning-asset weighted monthly return. 100/400 and 300/400 give weights 25%/75%. Contributions are +2.5 and -1.5 percentage points, so the composite earns +1%, not an equal-weight +4%.

Binding: CMP-WGT-001; AT-043; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_01`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-01 -->
```json
{
  "oracle_id": "OR-01",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "assets": [
      "100",
      "300"
    ],
    "returns": [
      "0.10",
      "-0.02"
    ]
  },
  "expected": {
    "weights": [
      "0.25",
      "0.75"
    ],
    "contributions": [
      "0.025",
      "-0.015"
    ],
    "return": "0.01"
  }
}
```

## OR-02

Geometric two-month chain. (1.01 × 1.02) − 1 = 0.0302, or 3.02%; addition gives a different result.

Binding: CMP-RET-008; AT-044; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_02`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-02 -->
```json
{
  "oracle_id": "OR-02",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "monthly_returns": [
      "0.01",
      "0.02"
    ]
  },
  "expected": {
    "cumulative_return": "0.0302"
  }
}
```

## OR-03

Monthly flow netting. Under the proposed ABS_NET policy, +150 − 100 = +50, and abs(50)/1000 = 5%, below the 10% threshold. This example does not approve that policy.

Binding: CMP-FLW-002; AT-025; lotus-manage; [owning work](https://github.com/sgajbi/lotus-manage/issues/714); planned test `composite_oracle_or_03`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-03 -->
```json
{
  "oracle_id": "OR-03",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "prior_month_end_aum": "1000",
    "signed_external_flows": [
      "150",
      "-100"
    ],
    "threshold": "0.10",
    "policy": "ABS_NET"
  },
  "expected": {
    "net_flow": "50",
    "ratio": "0.05",
    "flow_rule": "PASS"
  }
}
```

## OR-04

Withdrawal at threshold. Under the proposed ABS_NET inclusive threshold, abs(-100)/1000 = 10%; it fails at equality. Signed-net policy is a distinct supported choice.

Binding: CMP-FLW-002; AT-026; lotus-manage; [owning work](https://github.com/sgajbi/lotus-manage/issues/714); planned test `composite_oracle_or_04`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-04 -->
```json
{
  "oracle_id": "OR-04",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "prior_month_end_aum": "1000",
    "signed_external_flows": [
      "-100"
    ],
    "threshold": "0.10",
    "policy": "ABS_NET"
  },
  "expected": {
    "ratio": "0.10",
    "flow_rule": "FAIL"
  }
}
```

## OR-05

Cash exactly at threshold. 50/1000 = 5%; the maximum cash ratio permits equality. This does not approve the institution's cash definition.

Binding: CMP-ELG-010; AT-019; lotus-manage; [owning work](https://github.com/sgajbi/lotus-manage/issues/714); planned test `composite_oracle_or_05`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-05 -->
```json
{
  "oracle_id": "OR-05",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "cash": "50",
    "aum": "1000",
    "maximum_ratio": "0.05"
  },
  "expected": {
    "ratio": "0.05",
    "cash_rule": "PASS"
  }
}
```

## OR-06

Reference currency translation. (1.02 × 1.4/1.3) − 1 gives the unhedged reporting-currency return. The quote direction is reporting units per native unit.

Binding: CMP-FX-002; AT-051; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_06`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-06 -->
```json
{
  "oracle_id": "OR-06",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "native_return": "0.02",
    "begin_fx_reporting_per_native": "1.3",
    "end_fx_reporting_per_native": "1.4"
  },
  "expected": {
    "reporting_return": "0.0984615384615384615384615384615384615384615384615"
  }
}
```

## OR-07

Single-period Modified Dietz. (130 − 100 − 20)/(100 + 0.5 × 20) = 10/110. Modified Dietz is a distinct method, not automatically identical to daily TWR.

Binding: CMP-RET-003; AT-050; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_07`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-07 -->
```json
{
  "oracle_id": "OR-07",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "begin_value": "100",
    "end_value": "130",
    "external_flow": "20",
    "remaining_period_weight": "0.5"
  },
  "expected": {
    "return": "0.090909090909090909090909090909090909090909090909091"
  }
}
```

## OR-08

24-month annualization. (1.21)^(12/24) − 1 = 10% with 24 complete months.

Binding: CMP-RET-010; AT-052; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_08`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-08 -->
```json
{
  "oracle_id": "OR-08",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "cumulative_return": "0.21",
    "complete_months": 24
  },
  "expected": {
    "annualized_return": "0.1"
  }
}
```

## OR-09

Six-month GIPS presentation. The six-month cumulative return remains 10%; the proposed GIPS presentation has a null annualized return and an explicit short-period reason.

Binding: CMP-RET-010; AT-052; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_09`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-09 -->
```json
{
  "oracle_id": "OR-09",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "cumulative_return": "0.10",
    "complete_months": 6,
    "presentation": "GIPS"
  },
  "expected": {
    "cumulative_return": "0.10",
    "annualized_return": null,
    "reason": "PERIOD_LESS_THAN_ONE_YEAR"
  }
}
```

## OR-10

36-month sample annualized standard deviation. Use all 36 specified monthly observations, sample denominator n−1 and sqrt(12) annualization. This is time-series volatility, not member dispersion.

Binding: CMP-AN-006; AT-063; lotus-risk; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_10`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-10 -->
```json
{
  "oracle_id": "OR-10",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "monthly_returns": [
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0",
      "0.01",
      "-0.01",
      "0"
    ],
    "sample_denominator": "n-1",
    "annualization_factor": 12
  },
  "expected": {
    "annualized_stddev": "0.028685486624025447359251612312634999636325098375955"
  }
}
```

## OR-11

Full-year member dispersion sample method. Six full-year member annual returns produce sample dispersion about 1.87082869%. Full-year eligibility, estimator and threshold applicability require separate approval.

Binding: CMP-AN-004; AT-065; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/608); planned test `composite_oracle_or_11`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-11 -->
```json
{
  "oracle_id": "OR-11",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "full_year_member_annual_returns": [
      "0.01",
      "0.02",
      "0.03",
      "0.04",
      "0.05",
      "0.06"
    ],
    "method": "EQUAL_WEIGHT_SAMPLE_STDDEV"
  },
  "expected": {
    "dispersion": "0.018708286933869706927918743661582746508780099038894"
  }
}
```

## OR-12

Maximum drawdown including initial wealth. Starting wealth 1 is part of the peak path; the drop from 1.10 to 0.880 is −20%. The final rise does not erase that drawdown.

Binding: CMP-AN-013; AT-067; lotus-risk; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_12`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-12 -->
```json
{
  "oracle_id": "OR-12",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "period_returns": [
      "0.10",
      "-0.20",
      "0.05"
    ]
  },
  "expected": {
    "wealth": [
      "1",
      "1.10",
      "0.880",
      "0.92400"
    ],
    "maximum_drawdown": "-0.20"
  }
}
```

## OR-13

Carino linked member contribution. Carino linking allocates the geometric 3.02% total across both members. Preserve linked precision and reconcile the sum, including negative contribution.

Binding: CMP-CON-001; AT-070; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_13`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-13 -->
```json
{
  "oracle_id": "OR-13",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "period_returns": [
      "0.01",
      "0.02"
    ],
    "A_contributions": [
      "0.025",
      "0.005"
    ],
    "B_contributions": [
      "-0.015",
      "0.015"
    ]
  },
  "expected": {
    "A_linked_contribution": "0.030274630541907723798278421725685604316257567000362",
    "B_linked_contribution": "-0.000074630541907723798278421725685604316257567000360925",
    "sum": "0.030200000000000000000000000000000000000000000000001",
    "cumulative_return": "0.0302"
  }
}
```

## OR-14

Portfolio weight concentration. 0.25² + 0.75² = 0.625; 1/HHI = 1.6 effective members. This is not the raw member count of two.

Binding: CMP-AN-029; AT-074; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_14`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-14 -->
```json
{
  "oracle_id": "OR-14",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "weights": [
      "0.25",
      "0.75"
    ]
  },
  "expected": {
    "hhi": "0.625",
    "effective_member_count": "1.6"
  }
}
```

## OR-15

One-year money-weighted return. The one-year investor equation −100 + 110/(1+r) = 0 gives IRR 10%. Multi-root and no-root paths need separate negative tests.

Binding: CMP-MWR-001; AT-058; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_15`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-15 -->
```json
{
  "oracle_id": "OR-15",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "investor_cashflows": [
      "-100",
      "110"
    ],
    "year_fractions": [
      "0",
      "1"
    ]
  },
  "expected": {
    "irr": "0.10"
  }
}
```

## OR-16

Private-capital multiples. Distributions/paid-in = 0.4, residual/paid-in = 0.9 and their sum = 1.3; missing or zero paid-in cannot be assumed valid.

Binding: CMP-AN-039; AT-058; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_16`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-16 -->
```json
{
  "oracle_id": "OR-16",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "paid_in": "100",
    "distributions": "40",
    "residual_value": "90"
  },
  "expected": {
    "dpi": "0.4",
    "rvpi": "0.9",
    "tvpi": "1.3"
  }
}
```

## OR-17

Brinson-Fachler single-period reconciliation. Portfolio 6.8% minus benchmark 5.5% equals 1.3 percentage points. Allocation, selection and interaction effects must reconcile under this Brinson-Fachler convention.

Binding: CMP-ATT-001; AT-071; lotus-performance; [owning work](https://github.com/sgajbi/lotus-platform/issues/923); planned test `composite_oracle_or_17`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-17 -->
```json
{
  "oracle_id": "OR-17",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "portfolio_weights": [
      "0.6",
      "0.4"
    ],
    "benchmark_weights": [
      "0.5",
      "0.5"
    ],
    "portfolio_group_returns": [
      "0.10",
      "0.02"
    ],
    "benchmark_group_returns": [
      "0.08",
      "0.03"
    ]
  },
  "expected": {
    "portfolio_return": "0.068",
    "benchmark_return": "0.055",
    "allocation": [
      "0.0025",
      "0.0025"
    ],
    "selection": [
      "0.01",
      "-0.005"
    ],
    "interaction": [
      "0.002",
      "0.001"
    ],
    "active_return": "0.013"
  }
}
```

## OR-18

Mandatory month gap blocks requested chain. A required middle month is absent. The full three-period return is null with REQUIRED_PERIOD_UNAVAILABLE; 3.02% from the two surviving months is explicitly forbidden.

Binding: CMP-RET-011; AT-046; lotus-performance; [owning work](https://github.com/sgajbi/lotus-performance/issues/540); planned test `composite_oracle_or_18`. Runtime/API binding: absent; owning execution has not been supplied.

<!-- oracle:OR-18 -->
```json
{
  "oracle_id": "OR-18",
  "evidence_class": "SPECIFICATION_ORACLE",
  "state": "PLANNED",
  "inputs": {
    "monthly_returns": [
      "0.01",
      null,
      "0.02"
    ],
    "required_periods": 3
  },
  "expected": {
    "cumulative_return": null,
    "reason": "REQUIRED_PERIOD_UNAVAILABLE",
    "forbidden_survivor_chain": "0.0302"
  }
}
```

## Additional typed unavailable and control scenarios

AT-037 refuses asset-weighted calculation without weighting assets; AT-038 preserves composite-only evidence depth and makes member analytics unavailable. AT-047 distinguishes no eligible population from missing eligible-member data. AT-055/056 require separate actual-net versus model-net authority. AT-075 keeps normal policy exclusion separate from technical degradation. AT-076–085 cover exact freeze scope, stale-write conflicts, independent approval, immutable replacement and report version consistency.

These are scenario obligations, not invented current response DTOs or supported HTTP routes. Owners must assert the actual typed reason/status, source identity, precision, approvals and response shape in positive and negative tests. The first Excel example must consume an immutable approved Performance dataset and prove numeric cells, units, unavailable reasons and manifest identity; a UI screenshot or spreadsheet formula is not evidence that the financial calculation passed.
