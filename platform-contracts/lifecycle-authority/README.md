# Lifecycle Authority Interoperability

This contract family governs how a bank-controlled lifecycle authority communicates signed legal
hold and privacy decisions to Lotus consumers. It standardizes interoperability; it does not make
`lotus-platform`, `lotus-idea`, or another Lotus product the legal, records, or privacy authority.

## Ownership boundary

| Responsibility | Owner |
| --- | --- |
| Approve legal hold and release decisions | Bank legal and records governance |
| Approve erasure and purge decisions | Bank privacy governance |
| Issue signed decisions and publish trusted keys | Bank-controlled authority integration |
| Verify signatures, scope, validity, and replay protection | Consuming Lotus application |
| Govern schemas and producer certification evidence | `lotus-platform` |

The current implementation is design-modular: schemas, semantic rules, and certification evidence
have stable interfaces. It does not create a platform runtime service. A separately deployable
authority adapter is justified only by confirmed bank ownership, workload, failure-isolation, and
operability requirements.

## Contract artifacts

- `lifecycle-authority-decision.schema.json`: signed decision envelope accepted by consumers.
- `lifecycle-authority-key-discovery.schema.json`: Ed25519 trust-key discovery document.
- `producer-certification.v1.json`: fail-closed production certification posture.
- `examples/`: source-safe, non-production conformance fixtures.

Run `python automation/validate_lifecycle_authority_contracts.py` before changing these artifacts.
Production promotion additionally requires live issuer ownership, managed-key rotation and
revocation proof, HTTPS discovery with redirect rejection, consumer replay proof, privacy and legal
approval, and mainline CI evidence. Passing this repository validator alone is not certification.
