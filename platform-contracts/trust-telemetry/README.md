# Trust Telemetry Contracts

This directory stores the platform-governed live trust telemetry contract family introduced by
RFC-0087.

Trust telemetry is runtime evidence emitted by domain-product producers or consumers. It is not the
same as declared trust metadata in `platform-contracts/domain-data-products/`; declared metadata says
what a product must carry, while telemetry says what the current runtime evidence observed.

Current contract artifacts:

1. `trust-telemetry-snapshot.schema.json`
   Machine-readable schema for one product trust snapshot.
2. `validate_trust_telemetry.py`
   Validator for telemetry snapshot files or directories.

Validation command:

```powershell
python .\automation\validate_trust_telemetry.py .\platform-contracts\trust-telemetry\examples
```

The validator checks that telemetry snapshots:

1. reference a product in the generated domain-product catalog,
2. use governed freshness, completeness, reconciliation, and data-quality states,
3. identify runtime evidence with correlation and emission timestamps,
4. carry blocked reasons when a product is blocked,
5. carry every `required_trust_metadata` field declared by the product,
6. only report additional observed fields declared as conditional metadata and satisfy their
   governed admission checks.

