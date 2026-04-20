# Mesh SLO Policies

This directory contains RFC-0091 mesh SLO policies for governed domain products.

Policies define blocking or advisory thresholds for freshness, completeness, reconciliation,
data quality, lineage, and escalation ownership. They are product-specific contract inputs for
platform certification; they do not replace repo-native product declarations or runtime telemetry.

Validate policies and evaluate telemetry with:

```powershell
python automation/validate_mesh_slo_policies.py --telemetry-path output/trust-telemetry/collection/snapshots
```

The mesh certification gate consumes these policies and turns violations into certification issues.
