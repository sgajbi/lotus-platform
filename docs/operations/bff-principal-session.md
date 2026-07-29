# Authenticated BFF Principal Session Operations

## Scope

This runbook governs the source contract for resolving an authenticated server-side BFF session into
a least-privilege Lotus principal. It is an interoperability and validation surface for Workbench,
Gateway, and downstream services. It does not deploy a bank identity provider, certify production
authentication, or promote an RFC-0002 supported feature.

## Evidence Flow

```text
Bank-approved IdP/session authority
  -> server-side BFF session verification
  -> bounded Lotus principal
  -> route-specific least-privilege header projection
  -> Gateway/domain-service authorization
```

The current source-controlled posture stops at contract and fixture availability:

1. the schema defines the trusted issuer/audience/session binding requirements,
2. the fixture models the least-privilege principal and route projection shape,
3. the certification posture remains `not_certified`,
4. production IdP, key discovery, revocation/logout, entitlement-denied browser proof, and
   exact-main consumer evidence remain blockers.

## Operator Checks

Run:

```powershell
python automation\validate_bff_principal_session_contracts.py
python -m pytest tests\unit\test_bff_principal_session_contracts.py -q
```

The platform repo check lane also runs the validator through
`automation\Invoke-PlatformRepoChecks.ps1`.

## Consumer Rules

Workbench, Gateway, and domain services consuming this contract must:

1. derive authority from verified server-side session context only,
2. strip browser-supplied authority headers before any upstream call,
3. project only route-specific headers required by the Gateway capability,
4. fail closed for missing, malformed, expired, revoked, wrong-audience, wrong-issuer,
   cross-tenant, cross-portfolio, capability-escalation, and browser-header override attempts,
5. keep local/dev fixtures explicitly non-certifying,
6. avoid raw tokens, cookies, unrestricted claims, portfolio/client identifiers, request bodies, and
   security headers in persisted evidence, screenshots, logs, and metrics.

## Failure Handling

| Condition | Action |
| --- | --- |
| Platform contract fixture missing or validator red | Stop Workbench/Gateway promotion; fix source contract first. |
| IdP/session authority unavailable | Preserve blocked production identity posture; do not invent local auth. |
| Browser authority override succeeds | Treat as a security defect; block promotion and open/reuse the owning issue. |
| Raw token or claim evidence appears in artifacts | Revoke artifact use, remove sensitive output, and fix the producer. |
| Consumer passes local/dev fixture as certification | Reject the proof; local/dev fixture remains non-certifying. |

Contract source: [Authenticated BFF Principal Session](../../platform-contracts/bff-principal-session/README.md).
