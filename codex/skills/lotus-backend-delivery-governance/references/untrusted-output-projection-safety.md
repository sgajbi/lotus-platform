# Untrusted Output Projection Safety

Use this reference when a backend accepts generated, model, provider,
rules-engine, or other untrusted output and then verifies, rejects, stores, or
projects it.

## Required Review

Trace untrusted content through every outcome:

1. accepted,
2. rejected or blocked,
3. fallback,
4. exception and product-safe error,
5. idempotent replay,
6. changed-content conflict,
7. audit and telemetry,
8. in-memory and durable persistence,
9. API response and OpenAPI examples.

A blocked status, failed verifier result, or empty verified-claim list does not
prove that raw content is absent from another response field.

## Implementation Rule

For accepted output, project only deterministic, policy-approved content backed
by verified evidence or claims. For rejected output, replace free text with
deterministic server-owned reason text before returning the domain or application
result.

When replay or audit requires tamper evidence, retain bounded identities,
versioned policy metadata, and a canonical content digest. Do not retain or
return raw rejected text unless a separately authorized forensic store and
access path explicitly requires it.

## Proof

Use adversarial markers and prove they are absent from:

1. first responses and replay responses,
2. product-safe errors and conflict responses,
3. domain/application result representations,
4. audit attributes and telemetry labels,
5. durable rows, JSON payloads, and reload projections,
6. OpenAPI examples and operator diagnostics.

Also prove changed submitted content still produces the required deterministic
conflict or new-version behavior even though the raw text is not retained.
