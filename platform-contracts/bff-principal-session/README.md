# Authenticated BFF Principal Session Contract

## Purpose

This contract defines the platform-owned shape for resolving an authenticated server-side BFF
session into a least-privilege Lotus principal. It exists so Workbench, Gateway, and domain-service
consumers can implement against one governed contract instead of inventing local identity formats.

This is a source contract and fixture harness only. It does not choose a bank identity provider,
deploy production authentication, certify token claims, or promote any RFC-0002 supported feature.

## Ownership Boundary

| Responsibility | Owner |
| --- | --- |
| Authenticated session/token issuer and bank approval | External IdP / bank security authority |
| Versioned Lotus principal contract, fixtures, and validator | `lotus-platform` |
| BFF session resolution and route policy projection | `lotus-workbench` and other BFF owners |
| Gateway/domain-service authorization enforcement | Owning service |
| Lotus Idea opportunity support or production certification | Not this contract |

## Contract Rules

1. Browser-supplied subject, role, capability, tenant, portfolio, actor, or authorization headers are
   never trusted.
2. A BFF may project only least-privilege, route-specific upstream headers derived from a verified
   server-side session.
3. Missing, malformed, expired, revoked, wrong-audience, wrong-issuer, cross-tenant,
   cross-portfolio, capability-escalation, and browser-header override attempts fail closed.
4. Raw tokens, cookies, secrets, unrestricted claims, client identifiers, portfolio identifiers, and
   business payloads must not enter logs, metrics, screenshots, or persisted evidence.
5. Local/dev fixtures are non-certifying and must remain explicitly separated from production
   identity proof.

## Files

- [`bff-principal-session.schema.json`](bff-principal-session.schema.json)
- [`certification-posture.schema.json`](certification-posture.schema.json)
- [`certification-posture.v1.json`](certification-posture.v1.json)
- [`examples/bff-principal-session.valid.json`](examples/bff-principal-session.valid.json)

Validate with:

```powershell
python automation\validate_bff_principal_session_contracts.py
python -m pytest tests\unit\test_bff_principal_session_contracts.py -q
```

## RFC-0002 Boundary

This contract is a prerequisite for `lotus-workbench#436` and the authenticated-principal portion
of Lotus Idea RFC-0002 Slice 11. It can clear only the contract/fixture availability gap. It must
not clear production IdP, authenticated session/token-claims, entitlement-denied browser proof,
supported-feature promotion, client publication, or production certification blockers.
