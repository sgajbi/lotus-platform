# Mesh Access Policies

This directory contains RFC-0091 mesh access policies for governed domain products.

Policies define allowed consumers, tenant scope, roles, use cases, customer-visible posture,
operator-visible posture, and audit rationale. They are platform governance inputs for gateway
publication and Workbench discovery; gateway may publish the policy posture, but it must not become
the product authority.

Validate policies with:

```powershell
python automation/validate_mesh_access_policies.py
```
