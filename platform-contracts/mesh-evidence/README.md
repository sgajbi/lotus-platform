# Mesh Evidence Policies

This directory contains RFC-0091 evidence-pack policies for governed domain products.

Policies classify evidence-pack sections as:

- `public_customer`
- `restricted_customer`
- `operator_only`
- `internal_only`

Evidence packs are generated from derived platform artifacts. They are not hand-written proof and
do not replace repo-native product declarations, telemetry, SLO, or access policy source truth.

Generate a certification-history record and evidence-pack manifest with:

```powershell
python automation/generate_mesh_evidence_pack.py --generated-at-utc 2026-04-20T00:00:00Z --audience customer-authorized
```
