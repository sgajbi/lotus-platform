# RFC-0109: Lotus Production Principal And Capability Resolution

- Status: Draft — session half implemented, downstream half specified and unimplemented
- Date: 2026-09-06
- Owners:
  - `lotus-platform` identity and access governance
- Target repositories:
  - `lotus-platform` (contract, fixtures, validator)
  - `lotus-workbench` (BFF session resolution — [#436](https://github.com/sgajbi/lotus-workbench/issues/436))
  - `lotus-gateway` (composition front-door admission)
  - `lotus-manage` (write admission — [#624](https://github.com/sgajbi/lotus-manage/issues/624))
- Resolves: [#563](https://github.com/sgajbi/lotus-platform/issues/563),
  [#775](https://github.com/sgajbi/lotus-platform/issues/775)

## Why this RFC exists

#563 and #775 have been read as two problems. They are one problem seen from two ends, and
holding them apart is why neither has moved: #563 asks how a **user** becomes a principal,
#775 asks how a **downstream service** decides what a caller may do. A design that answers
only one leaves the other with nothing to build against.

They also carry different amounts of unfinished work, which the issues do not say.

## Current state, measured on `8a24180`

**#563's session contract already exists and passes.** `platform-contracts/bff-principal-session/`
landed in `68c9d3a` with a schema, a certification posture, a valid example, a validator and
eight tests. `python automation/validate_bff_principal_session_contracts.py` exits 0.

Its `validatedPrincipal` already carries `subjectRef`, `tenantRef`, `legalEntityRef`,
`bookingCenterRef`, `roles`, `capabilities`, `portfolioScopeRefs`, `mandateScopeRefs`,
`actorRef`, `assuranceLevel`, `sessionIdSha256`, `authTimeUtc`, `expiresAtUtc` and
`impersonationPosture`. Its `routePolicy` carries `requiredCapabilities`, `projectedHeaders`
and `forbiddenBrowserAuthorityHeaders`.

So #563's finding — *"Lotus has no platform-owned, versioned identity/session-to-principal
contract"* — is **stale**, and the remaining work on that issue is consumer adoption and the
ten unmet controls in its certification posture, not contract authorship.

**#775's half does not exist.** `lotus-ai` ships a verified service credential
(`src/app/http/caller_credential.py`): a compact EdDSA JWS whose `sub` names the calling
application, verified against a configured issuer, audience and Ed25519 key map with two active
key ids for rotation, with trust modes `header` and `verified_service_jwt`, failing 401
`CALLER_CREDENTIAL_INVALID` and never downgrading to header trust.

That credential proves **which application** is calling. It does not carry tenant membership or
capability grants. So even with it deployed, Gateway still reads `X-Caller-Capabilities` and the
actor/tenant/region trio as presence-validated headers, which in a header-trust deployment any
reachable client can assert.

**The gap in one sentence:** Lotus can authenticate a user session and can authenticate a calling
application, and has no contract from which a downstream resolves *what that principal may do, in
which tenant*.

## The design

### Two principal kinds, one resolved principal

| | User principal | Service principal |
| --- | --- | --- |
| Established by | Authenticated session at a BFF | Platform-issued service credential |
| Answers | *who* is acting | *which application* is acting |
| Contract | `bff-principal-session` (exists) | `verified_service_jwt` shape (shipped in `lotus-ai`, ungoverned) |
| `sub` names | a person | an application |

Both resolve into the **same** shape before authorization: a tenant, a capability set, and an
entitlement scope. Downstream services authorize against that resolved shape and never against
the transport that produced it. This is what makes the two ends one design — a domain service
should not need to know whether a caller arrived through a browser session or a service credential.

### Environment posture

Following the rollout `lotus-ai` already proved:

| Posture | Principal requirement | Where |
| --- | --- | --- |
| `header-trust` | documented perimeter trust; headers accepted | local and dev only |
| `verified` | verified principal required; header authority ignored entirely | every promoted environment |

`verified` must not fall back to `header-trust` on a verification failure. `lotus-ai`'s
implementation is explicit that a failure is a 401 and "never downgrades to header trust", and that
is the property worth copying, because a fallback turns the strongest control in the chain into the
weakest.

The posture is a deployment fact, not a request fact. No header, claim, or parameter may select it.

### Resolution order

A downstream resolves, in order, and every step is a refusal rather than a filter:

1. verify the principal — fail closed on missing, malformed, expired, revoked, wrong issuer, wrong
   audience, unknown key id;
2. resolve tenant membership — fail closed when absent or when the request names another tenant;
3. resolve the capability grant set for that principal in that tenant;
4. intersect with the route's required capabilities — fail closed on any capability not granted;
5. resolve entitlement scope — fail closed on any identifier outside it.

A request for something outside scope is denied rather than silently narrowed, because a narrowed
result is indistinguishable from a correct one to both the caller and the audit record.

### Denials

A denial states the class and nothing further. The response distinguishes unauthenticated from
unauthorized, and reveals neither which capability was missing nor whether a named portfolio exists
— a "no such portfolio" and a "not entitled to this portfolio" that differ are an enumeration
oracle. No raw token, cookie, session secret, capability set, or portfolio identifier enters logs,
metrics, screenshots, or persisted evidence.

## The mechanism decision

An earlier revision of this RFC asserted that grants carried in a signed token are "the present
defect with a signature on it". That was a conclusion stated as a premise, and it is wrong as
written: a signed token is not an untrusted header, because its issuer, audience and integrity are
verifiable. The real question is not trust but **freshness and revocation**, and it deserves an
argued answer rather than an assertion.

| Requirement | Grants inside the credential | Grants resolved from a store |
| --- | --- | --- |
| Trust | Verifiable: signature, issuer, audience | Verifiable: the store is an authenticated dependency |
| Audience binding | Strong; the credential names its audience | Requires the resolver to bind audience itself |
| Freshness | Bounded by credential lifetime | Current at each request |
| Revocation | Requires a revocation list or short lifetimes | Immediate |
| Availability | No dependency at request time | Fails when the store is unavailable |
| Blast radius of a leak | Whole grant set until expiry | Identity only; grants still resolved |

Neither column is free. Grants in the credential trade revocation latency for availability; a store
trades availability for immediacy.

**Decision: grants are resolved from a store, and the credential carries identity and audience
only.** The reason is specific to this estate rather than general. Lotus entitlements are portfolio
and mandate scoped, and those change through ordinary business operations — a mandate ends, a
portfolio moves adviser, an entitlement is withdrawn during an investigation. A credential lifetime
short enough to make that acceptable would be short enough to require refresh on nearly every
request, which reintroduces the dependency the credential was supposed to remove while keeping its
revocation lag.

The consequence is accepted rather than hidden: **when the grant store is unavailable, requests are
denied.** That is stated as a denial class below rather than left to each consumer to discover, and
it is the cost of the decision.

A hybrid is available and deliberately not chosen now: a credential could carry a coarse capability
set with a fine-grained store lookup for portfolio scope. It is not chosen because two authorities
for one fact is the failure this estate has spent the cycle removing, and no measured performance
requirement yet justifies it. Revisit it with numbers, not with intuition.

## The six questions, answered

### 1. User, service, and delegated actor

Three principal kinds, not two. The third is the one that causes damage when it is missed.

| Kind | `sub` names | Entitlement source |
| --- | --- | --- |
| User | a person | that person's grants |
| Service | an application acting for itself | that application's grants |
| Delegated | an application acting for a person | the **intersection** of both |

**A shared service identity must never widen a user's entitlement.** A delegated call carries both
the application's credential and the user principal it is acting for, and the effective permission
set is the intersection: a capability must be granted to the application *and* to the user, and a
portfolio must be in scope for both. An application trusted broadly does not become a way to reach
portfolios its caller cannot see.

The delegated form is required, not optional, because Workbench's BFF is exactly this shape: a
server-side application making calls on behalf of a signed-in adviser.

### 2. Who owns the grant store

**The service that owns tenant membership owns the grant store.** Platform defines the contract and
does not host it. That follows the estate's existing rule that a fact has one authoritative owner,
and tenant membership already has one.

This is now decided rather than open, because leaving it open blocks the consumers this RFC exists
to unblock: a resolver cannot be implemented against an unnamed authority.

### 3. Audience and scope binding

A credential is accepted only when its `aud` names the service validating it. A credential minted
for Gateway is not valid at Manage, so a leaked or misrouted credential does not become a
general-purpose key. Scope binding is separate and stricter: the resolved grant set is scoped to the
tenant named in the request, and a request naming a tenant the principal has no membership in is
denied before any capability is considered.

### 4. Revocation window and cache behaviour

Resolution is per request. Where caching is required for load, **the cache lifetime is the
revocation window**, and it must be documented as such in the consuming service rather than chosen
for latency alone. A service caching grants for five minutes has a five-minute revocation window and
must say so. The default is no cache.

### 5. Dependency-unavailable denial

When the grant store cannot be reached, the request is **denied**, and the denial is distinguishable
in telemetry from an authorization failure — `unavailable`, not `forbidden`. Consumers must not fall
back to a cached grant set beyond its stated window, and must not fall back to header trust, which
would make the outage the attack.

### 6. Effective permissions for service-on-behalf-of-user

Answered in question 1: the intersection. Stated separately here because it is the case most likely
to be implemented as a union by accident, and a union silently grants every user the application's
full reach.

## Consumer contract shapes and negative fixtures

Each consumer gets an exact shape and the denials it must prove. These are the negative fixtures
platform publishes; a consumer that passes only the positive case has not implemented this contract.

**Every consumer must prove, at minimum:** missing credential; expired credential; wrong audience;
wrong issuer; unknown key id; revoked principal; tenant not a member; capability not granted;
portfolio outside scope; grant store unavailable; and — for delegated calls — a capability the
application holds but the user does not.

**`lotus-workbench` #436.** Resolves a session into a user principal and makes delegated calls. Its
BFF holds an application credential *and* the user principal; it must not project capability or
tenant authority as headers into a `verified` environment, because a downstream that resolves rather
than accepts would ignore them and a downstream that accepts them would be trusting the BFF's
assertion rather than the user's identity. This corrects an earlier revision of this RFC, which gave
Workbench an acceptance that projected route headers while also stating that Gateway ignores header
authority — the two cannot both hold.

**`lotus-gateway`.** Resolves rather than accepts, per write family. The acceptance that matters is
negative and needs no identity provider: a request asserting a capability header it was not granted
is denied under `verified` posture.

**`lotus-manage` #624.** Authorizes writes against the resolved set. An inbound `manage.write` header
with no verified principal is refused under `verified` posture.

**`lotus-platform`.** Publishes the grant and delegated-principal contracts alongside the existing
session schema, with a fixture per denial class above.

## What already exists, and what it does not prove

`platform-contracts/bff-principal-session/` ships today: schema, certification posture, valid
example, validator (exits 0), eight tests. #563's finding that no contract exists is stale and its
opening should be rewritten.

**That existence proves availability of a contract and fixtures. It does not prove authenticated
user-session authentication is implemented.** `certification-posture.v1.json` has all ten required
controls `false`, including `server_side_session_binding_implemented`,
`revocation_logout_and_expiry_verified` and `hostile_browser_header_override_proof`. No consumer,
and not this RFC, may describe schema and fixture availability as working authentication.

## Slices

| Slice | Scope |
| --- | --- |
| 1 | Platform publishes the delegated-principal and grant-resolution contracts, fixtures for every denial class, and a validator |
| 2 | Gateway resolves rather than accepts, per write family, fail-closed under `verified` |
| 3 | Manage authorizes writes against the resolved set |
| 4 | Workbench resolves the session and makes delegated calls without projecting authority headers |
| 5 | Grant store implemented by the tenant-membership owner, with the availability denial proven |
| 6 | **Second-last: code review and governance tightening** — review and loose-end tightening, dead-code and duplicate-logic cleanup, API certification-pattern conformance, OpenAPI/vocabulary/contract/migration/platform-governance conformance, and final test-quality review before closure |
| 7 | **Final: documentation, context, skills, wiki, branch hygiene** — documentation and agent-context updates, wiki updates for operator-facing behaviour, an explicit keep/tighten/add/remove/no-change decision on the identity and access skills and guidance, and branch hygiene with truthful PR/CI evidence |

## Supported-features and evidence posture

Nothing in this RFC promotes a supported feature. `certification-posture.v1.json` remains the
authority on certification, and its ten controls stay `false` until each is separately evidenced.
Local and fixture identity is explicitly non-certifying and cannot clear a production blocker.

## Genuinely external

1. Bank identity-provider selection and approval.
2. Managed key issuance, custody and rotation for the service credential.
3. Production certification sign-off.

Everything else above is implementable and testable today. External identity-provider provisioning
does not prevent defining and testing the interoperability contract.
