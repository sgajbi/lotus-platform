# Financial Rounding and Precision Standard

Version: `1.1.0`  
Status: `MANDATORY`  
Owner: `PBWM Platform Governance (PPD)`  
Change control: RFC required (see `rfcs/RFC-0063-platform-wide-rounding-and-precision-standard.md`)

## Non-Negotiable Financial Correctness

All monetary and financial calculations across lotus-core, lotus-performance, lotus-manage, lotus-report, and lotus-gateway must be deterministic, reproducible, and consistent for equivalent inputs.  
Service-local ad hoc rounding behavior is prohibited.

## Canonical Rules

1. Internal/intermediate calculations must use `Decimal` (or equivalent arbitrary precision).
2. `float`/`double` is prohibited for monetary calculations and storage.
3. Intermediate values must not be prematurely rounded.
4. Rounding is allowed only at defined output boundaries (API response, report/export payload, persisted presentation snapshot).
5. Canonical rounding mode is `ROUND_HALF_EVEN` unless explicitly overridden by this standard.

## Precision Matrix

| Data Type | Internal Precision | Final Output Scale | Rounding Mode |
|---|---|---|---|
| Price | Decimal high precision | 6 dp | HALF_EVEN |
| FX rate | Decimal high precision | 8 dp | HALF_EVEN |
| Units / quantity | Decimal high precision | 6 dp | HALF_EVEN |
| Market value / money amount | Decimal high precision | 2 dp | HALF_EVEN |
| Performance metric (return %) | Decimal high precision | 6 dp | HALF_EVEN |
| Risk metric | Decimal high precision | 6 dp | HALF_EVEN |

## Intermediate vs Final

- Intermediate:
  - Intermediate calculations do not round.
  - Keep raw `Decimal` precision throughout domain calculations.
  - Avoid API/model serialization before finishing all operations.
  - Test naming convention should include `intermediate_precision_preserved`.
- Final:
  - Apply canonical quantization exactly once at output boundary per field type.
  - All equivalent cross-service scenarios must emit equivalent rounded values.

## Input Normalization

1. Normalize inbound numeric payloads to `Decimal` at service boundaries.
   - Preferred helper name: `normalize_input(value, semantic_type)`.
2. Validate scale and format by semantic type:
   - Money: accept <= 8 dp input, normalize and preserve for intermediate calculation.
   - Quantity: accept <= 12 dp input.
   - FX/price/risk/performance inputs: accept <= 12 dp input.
3. If external data has higher precision:
   - preserve internally,
   - round only at outbound boundary according to matrix.
4. Reject malformed numeric payloads (`422`) with clear field-level message.
   - Canonical error form includes `Invalid numeric value` or `scale <n> exceeds max <m>`.

## Configuration Model

Central defaults are mandatory:

- `rounding_mode = HALF_EVEN`
- `money_scale = 2`
- `price_scale = 6`
- `fx_rate_scale = 8`
- `quantity_scale = 6`
- `performance_scale = 6`
- `risk_scale = 6`
- `rounding_policy_version = 1.1.0`
- `ROUNDING_POLICY_VERSION = "1.1.0"`

Service-level overrides are allowed only for non-financial, explicitly documented use cases and must reference an approved RFC.

Compatibility rules:

1. `rounding_policy_version` must be exposed in service precision helper modules.
2. Policy upgrades must preserve field names and semantic types.
3. Any breaking policy change requires a new RFC plus migration notes.

## Implementation Standard

1. Reuse shared precision helper module in each backend service:
   - parse to decimal
   - quantize by semantic type (`quantize_*`)
   - normalize outbound payloads
2. Convert metrics/output values via helper before serialization.
3. Observability latency values may remain float and are out of financial scope.

## Testing and Validation Standard

Minimum required tests per service:

1. Unit:
   - boundary rounding (`0.005`, midpoint, negative midpoint)
   - invalid numeric parsing
   - quantization by each semantic type
2. Integration:
   - API responses return canonical scales
   - equivalent scenario consistency inside service boundaries
3. Cross-service golden:
   - same input vector across lotus-core/lotus-performance/lotus-manage/lotus-report returns identical rounded outputs for shared fields.

## CI Guardrail: Monetary Float Usage

To prevent drift, each backend repo must run a monetary-float guard in CI:

1. Scan source files for monetary/analytics semantic fields typed as `float`.
2. Fail CI on new findings not present in approved baseline allowlist.
3. Baseline file location per repo:
   - `docs/standards/monetary-float-allowlist.json`
4. Every allowlist entry must include:
   - `finding`
   - `justification`
   - `owner`
   - `review_by` (`YYYY-MM-DD`)
5. Stale allowlist entries (`review_by` in the past) fail CI.
6. Baseline updates require dedicated PR and explicit review rationale.

Deviation handling:

- Any deviation from this standard requires RFC approval and remediation timeline.

## Migration and Backward Compatibility

1. Existing endpoints must preserve field names; only numeric normalization/precision changes are allowed.
2. Any externally visible numeric precision change must be called out in release notes.
3. Migration rollout order:
   - PPD standard + RFC
   - lotus-core/lotus-performance/lotus-manage/lotus-report helpers + boundary wiring
   - lotus-gateway response shaping alignment
   - cross-service golden validation

