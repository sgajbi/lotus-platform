# Principal Credential: Wire Format, Key Discovery, And Signed Vectors

## Why this exists

[`principal-resolution`](../principal-resolution/README.md) publishes the shape a downstream
authorizes against and the thirteen denials a consumer must prove. It also states its own limit:
its fixtures carry no signed bytes and no keys, so **nothing in it can make a real verifier fail**.
`present_but_unverified` is an instruction to a test harness, not a property of a payload.

This contract closes that gap. It defines the credential on the wire, how keys are discovered, and
publishes **signed vectors** — real Ed25519 signatures over real bytes. A consumer points its own
verifier at them and either verifies or does not; there is nothing to branch on.

That distinction is measurable, and it is the reason this exists. A structure-only inspector —
three segments, right issuer, right audience, unexpired — **accepts**
[`denial.present_but_unverified.json`](examples/denial.present_but_unverified.json). The verifier
in [`automation/verify_principal_credential.py`](../../automation/verify_principal_credential.py)
refuses it. Trusting the foreign key makes the *same bytes* verify, which proves the refusal is
about the key rather than about malformed or expired content.

## The two credential kinds a consumer needs

Answering lotus-workbench#436's first two questions.

| | **Session credential** | **Delegated credential** |
| --- | --- | --- |
| Minted by | the identity provider | the BFF, from a verified session |
| Presented to | the Workbench BFF | Gateway |
| `aud` | `lotus-workbench-bff` | `lotus-gateway` |
| `sub` | the signed-in person | the signed-in person |
| `act` | absent | the calling application |
| `principal_kind` | `user` | `delegated` |
| Produces | `validatedPrincipal` | the resolved principal Gateway authorizes against |

Both are compact JWS with `alg: EdDSA`. Both resolve into the **same** resolved-principal shape, so
a domain service never authorizes against the transport that produced the caller.

**Verified posture projects no authority headers.** RFC-0109 is explicit that `verified` ignores
header authority entirely, so the delegated call carries a credential and not
`X-Caller-Capabilities`, `X-Tenant-Id` or an actor header. A BFF that forwards both has not moved
posture; it has added a second, weaker path to the same authority.

## Key discovery and revocation

- **Keys**: a JWKS document of `OKP` / `Ed25519` keys, each with a `kid`. See
  [`examples/jwks.json`](examples/jwks.json).
- **Key selection**: the only claim read before verification is `kid`, and only to choose among keys
  this deployment already trusts. The issuer is configured, never taken from the credential — a
  credential that nominates the authority which vouches for it is not evidence.
- **Revocation**: two inputs, credential ids (`jti`) and subjects, so one credential can be revoked
  without revoking the person. Unreachable revocation data is a denial, on the same reasoning as an
  unreachable grant store.

## Refusal order, and why it is a security property

1. missing → `missing_credential`
2. not a decodable three-part JWS, or an algorithm this verifier does not implement →
   `malformed_credential`
3. `kid` names no trusted key → `unknown_key_id`
4. **signature does not verify → `present_but_unverified`**
5. `iss` not the configured issuer → `wrong_issuer`
6. `aud` does not name this service → `wrong_audience`
7. outside its window → `expired_credential`
8. revoked credential or subject → `revoked_principal`

Then RFC-0109's five refusals: tenant membership, grant set, capability intersection, scope.

**Nothing in the payload is believed until step 4 passes.** Checking expiry or issuer first would be
refusing — or accepting — on the strength of bytes nobody signed. `alg` is compared against the one
algorithm implemented and never selects an implementation, which is what makes `alg: none` and
algorithm-confusion unreachable rather than merely blocked.

`not_yet_valid` deliberately shares the `expired_credential` class: a caller learns the credential
is outside its window, not which end, consistent with rule 6.

## Grant store: named owner and interface

Answering lotus-workbench#436's third question.

**Owner: `lotus-core`.** RFC-0109 assigned the grant store to "the service that owns tenant
membership" and asserted that membership "already has one". Measured across the estate on
2026-09-07, **no repository defines a tenants or tenant-membership table**, so that premise was not
backed by an artifact. `lotus-core` is named because it holds the closest existing authority —
`portfolio_party_role_assignments` and `/integration/portfolio-manager-books/{portfolio_manager_id}/memberships`
— and is already the tenant-scoping authority for portfolio data.

This is a naming decision that requires `lotus-core`'s acceptance, and it needs new capability
rather than exposure of an existing table.

**Tenant admission is not tenant membership**, and the distinction is the reason the store is
needed. Core's `TenantContext` admits a tenant id and scopes rows by it; nothing verifies that the
caller *belongs* to that tenant. Under `verified` posture that check is exactly what must exist.

The interface a consumer resolves against, injected rather than imported:

```python
tenant_members(subject: str, tenant_id: str) -> bool
grants_for(subject: str, tenant_id: str) -> GrantSet          # capabilities, portfolio scope
application_grants_for(actor: str, tenant_id: str) -> GrantSet # delegated calls only
```

**`tenant_members` and `grants_for` are required for every credential.
`application_grants_for` is required only for `delegated` credentials**, which are the only kind
whose authority is an intersection with an application's grants; a `user` or `service` credential
resolves without it, and demanding it everywhere would have consumers reject valid non-delegated
requests.

**Where a resolver is required, an absent one is a denial rather than a skipped step.** Not
supplying it leaves membership or entitlement *unanswerable*, which is not the same as answered
negatively: the refusal is `grant_store_unavailable`, not `tenant_not_a_member`, because the second
would assert the subject is not a member when nothing established that.

Any of these may raise `GrantStoreUnavailable`, which is a denial — never an empty grant set. An
empty set is indistinguishable from a principal holding nothing, and the request would be refused
for the wrong reason, or by a permissive consumer not refused at all.

**Today there is no implementation, so `grant_store_unavailable` is the honest current behaviour**,
and it is already one of the published denial classes. A consumer can complete its source slice
against a stub and still prove every refusal.

## What a consumer proves with its own keys

Generate a key pair, publish its public half as a JWKS, mint credentials, and run them through your
resolver. No provisioned identity provider and no managed key custody are needed for that slice.

Prove: real verification including `present_but_unverified`; all thirteen denials; zero protected
calls on any denial; one admitted delegated call; refusal of browser-supplied authority; and
principal-change isolation.

## Regenerating the vectors

```
python automation/generate_principal_credential_vectors.py
```

No private key is committed. Both keys derive from documented 32-byte seeds in the generator, so
the repository holds only public key material and the vectors are reproducible from source. Ed25519
signatures are deterministic (RFC 8032), so regeneration is byte-identical and a drift check is
meaningful. **The seeds are fixture material. They authenticate nothing, and no deployment may
configure them.**

## What this contract does not do

It does not choose or provision an identity provider, host the grant store, implement resolution in
any consumer, or certify a production deployment. Vectors passing is a source-level proof that a
resolver verifies. Live issuer, key custody and promotion remain unclaimed, and no control here may
be recorded as evidence of them.
