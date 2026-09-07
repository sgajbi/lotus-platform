# Principal Resolution And Capability Grant Contract

## Purpose

This contract defines the shape a downstream service authorizes against after resolving a caller,
and the denials it must prove. It is the downstream half of RFC-0109; the upstream half — resolving
an authenticated session into a principal — is
[`bff-principal-session`](../bff-principal-session/README.md).

A user session and a service credential resolve into the **same** shape, so a domain service never
authorizes against the transport that produced the caller.

This is a source contract and fixture set. It does not host the grant store, implement resolution in
any consumer, choose an identity provider, or certify production identity.

## Ownership Boundary

| Responsibility | Owner |
| --- | --- |
| Authenticated session or service credential issuance | External IdP / bank security authority |
| Versioned resolved-principal contract, fixtures, and validator | `lotus-platform` |
| Grant store implementation | The service that owns tenant membership |
| Resolution and enforcement per write family | `lotus-gateway`, then each domain service |
| Session resolution and delegated calls | `lotus-workbench` and other BFF owners |

## The rules this contract carries

1. **Posture is a deployment fact.** `header-trust` accepts identity headers and is permitted in
   local and dev only. `verified` requires a verified principal and ignores header authority
   entirely. No header, claim or parameter selects the posture, and `verified` never falls back to
   `header-trust` on a verification failure — a fallback turns the strongest control in the chain
   into the weakest.
2. **Three principal kinds.** User, service, and delegated. The delegated form is required rather
   than optional, because a BFF making calls for a signed-in person is exactly that shape.
3. **Delegated authority is the intersection.** A capability must be granted to the application
   *and* to the person; a portfolio must be in scope for both. A shared service identity never
   widens a person's entitlement.
4. **Resolution is five refusals, not five filters.** Verify the principal, resolve tenant
   membership, resolve the grant set, intersect with the route's required capabilities, resolve
   entitlement scope. A request for something outside scope is denied rather than silently narrowed,
   because a narrowed result is indistinguishable from a correct one to both the caller and the
   audit record.
5. **The grant store is owned by the tenant-membership owner**, and its unavailability is a denial.
6. **A denial states its class and nothing further.** It distinguishes unauthenticated from
   unauthorized, and reveals neither which capability was missing nor whether a named resource
   exists — a "no such portfolio" that differs from "not entitled to this portfolio" is an
   enumeration oracle.

## Files

- [`resolved-principal.schema.json`](resolved-principal.schema.json)
- [`resolved-principal.v1.json`](resolved-principal.v1.json)
- [`denial-fixture.schema.json`](denial-fixture.schema.json)
- [`admission-fixture.schema.json`](admission-fixture.schema.json)
- [`examples/`](examples) — one fixture per denial class (13), plus an admitted delegated call

## What a consumer must prove

Every consumer must prove all thirteen denials, not a selection: missing, malformed, expired,
wrong-audience, wrong-issuer, unknown-key-id and revoked credentials; **present but unverified**;
tenant not a member; capability not granted; portfolio outside scope; grant store unavailable; and —
for delegated calls — a capability the application holds but the person does not.

**`present_but_unverified` is the one that matters most, and the easiest to skip.** It is a
well-formed, unexpired, correctly-audienced credential whose signature does not verify against the
issuer's published keys. Every shape assertion passes, so a consumer can satisfy all twelve other
fixtures by validating structure and resolving nothing at all. Fed to a resolver as-is it separates
an implementation that verifies from one that inspects, which is what makes "verified server-side
authority is the source" mean something.

Every credential states `signatureVerifies` explicitly. A fixture that only *says* a credential was
unverified is indistinguishable from a verified one that fails later, so a consumer could produce
the expected refusal only by branching on the denial class — testing the fixture rather than the
resolver.

Each denial also carries `maxProtectedOperationCalls: 0`, and that is a measurement rather than a
claim. A 401 is identical whether the refusal ran before the protected operation was invoked or
after it, so the status code alone cannot tell them apart — only the call count can. Assert it
against a recording client; a boolean cannot distinguish no calls from nobody counting.

The budget covers **the protected operation the request was trying to perform**, not the resolution
lookups that reach the refusal. Key discovery, tenant membership and the grant store are how a
denial is *found* — `grant_store_unavailable` can only be discovered by attempting that call — so
counting them would make the one compliant implementation fail its own fixture.

### Two ways to prove nothing

**A request echo cannot certify.** Comparing a response's `tenant_id` against the one the request
sent compares an input with itself: where a producer builds that field from the request's own policy
context, the assertion holds for every possible implementation, including one that ignores identity
entirely. If such a comparison is kept, name it as echo integrity and do not count it as
authorization evidence. This one is on the record because a consumer shipped it and had to unwind
it.

**Authority never comes from payload content.** A tenant, actor or capability read out of a request
body lets the payload choose its own authorization scope. The resolved principal is the only source;
a body field of the same name is data being described, not authority being asserted.

Passing only the positive case is not an implementation. Neither is passing only the denials: a
resolver that refuses every request satisfies all twelve, which is why an admission fixture is
required alongside them. The admission fixture asserts a capability and a tenant in headers that the
resolved principal does not carry, so an implementation honouring header authority produces a
different result and fails it.

Validate with:

```powershell
python automation/validate_principal_resolution_contracts.py
python -m pytest tests/unit/test_principal_resolution_contracts.py -q
```

## Posture

`grantStoreImplemented`, `productionIdentityCertified` and `supportedFeaturePromoted` are all false
and stay false until live evidence exists. Fixture success is not live enforcement. This contract can
clear only the contract-and-fixture availability gap for `lotus-platform#775`; it cannot clear
production identity, grant-store implementation, or supported-feature promotion.
