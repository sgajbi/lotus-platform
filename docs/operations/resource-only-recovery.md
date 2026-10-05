# Reviewed resource-only recovery

This operator workflow is separate from normal canonical cleanup. It archives explicitly reviewed,
labelled, unreferenced images or volumes classified `unproven_resource_only_owner`; it does not
infer ownership from a prefix or label. Existing ownership, orphan-retirement and reservation
guards remain unchanged. Local tests are not live restore acceptance or production readiness.

## Admission and exclusions

The operator supplies a closed `lotus.resource-recovery.disposition.v2` JSON object. Its fields
are defined in `automation/resource_recovery/policy.py`, with no inferred defaults:

| Decision | Required fields |
| --- | --- |
| Accountable decision and window | `operator`, UTC `approved_at`, `expires_at` |
| Source and isolated verification | `source_context`, observed `source_daemon`, `verification_context`, observed `verification_daemon` |
| Reviewed evidence | `plan_sha256`, `inventory_sha256`, `primary_head` |
| Immutable discovery | `discovery`: exact capture/receipt paths and hashes, original start/finish, ordered raw native manifest and independent operator attestation |
| Current authority | `runtime_authority`: explicit holder, scope digest, exact source-head map and live-observation schema |
| Reviewed execution closure | absolute `helper_root`, exact `helper_files` path-to-SHA256 map |
| Exact allowlist | `targets`: objects containing only `kind`, full image ID or exact volume `id`, and `inspect_sha256` |
| Private retention and capacity | absolute `archive_root`, `retain_until`, `retention_authority`, immutable full `archiver_image` ID, positive `max_archive_bytes` |

`schema_version` must be `lotus.resource-recovery.disposition.v2`. Intermediate v1 disposition
and retirement schemas refuse; this unmerged helper has no accepted v1 archive to migrate.
The helper closure includes
the wrapper, all five package files, and the existing Docker ownership module. Inspect fingerprints
use the code-owned `fingerprint` function, not Docker labels alone. Plan and inventory are immutable,
independently reviewed discovery provenance, not current permission. Their raw native request/
response manifest must prove full four-kind coverage, matching source daemon and successful
start-based collection within300 seconds. Image-list aliases require inspected tag evidence;
malformed or unexplained duplicate identities refuse. Hash consistency cannot self-approve an
operator decision. No automatic binder or attestation is provided.

Each action obtains NEW parent-owned observations of exact targets, all running/stopped containers,
stable full-ID lists before/after, current protected checkouts, daemons and source/helper scope.
The observation clock begins before its first preflight/read; admission remains at most300 seconds
from START, never completion or a restamped discovery timestamp. Private observations are hashed,
read-locked and journaled with approval/run/operation identity. Each target is reobserved after long
restores; final freshness/fence checks precede source save/mount/removal, with tag-to-ID validation.
Original prepared/archive records are never overwritten by repeated per-target checks.

Exclude registered or existing checkout owners, active canonical roots, any running **or stopped**
container consumer, BuildKit, the archiver image, and unlabelled anonymous volumes. This helper
does not authorize historical issue inventories wholesale. A reviewed disposition is local operator
coordination, not production IAM or a grant.

The primary `<workspace-root>/lotus-platform` reservation module alone admits the operation.
Its original registered FileStream remains held synchronously through all I/O and outcome
publication. Python verifies policy and archive bytes; it receives no mutation capability. Each
Docker command rechecks the handle, primary CLI admission, reviewed helper hashes, primary source
and actual daemon ID. Context names alone cannot establish independent restoration. The reservation
serializes governed callers, not unrelated Docker clients. Double listing detects scan-window drift,
but Docker offers no atomic inspect-plus-save/remove transaction. Require a quiet controlled fixture;
do not claim external-race exclusion or application-consistent database backup.

## Operator procedure

Working directory: the reviewed `lotus-platform` checkout containing the new helper. Supply
`LOTUS_WORKSPACE_ROOT` as the directory holding primary checkouts. Supply absolute paths in
`LOTUS_RECOVERY_DISPOSITION`, `LOTUS_RECOVERY_PLAN`, `LOTUS_RECOVERY_INVENTORY`, and the reviewed
raw SHA256 in `LOTUS_RECOVERY_DISPOSITION_SHA256`. Set `LOTUS_CANONICAL_RUNTIME_HOLDER` to an
explicit already-acquired, unexpired reservation; acquisition is governed by the
[reservation runbook](canonical-runtime-reservation.md). No automatic acquisition is performed.

PowerShell 7.5 or later dry run (Windows PowerShell 5.1 is unsupported):

```powershell
pwsh -NoProfile -File automation/Invoke-ResourceOnlyRecovery.ps1 -Stage DryRun -ProjectsRoot $env:LOTUS_WORKSPACE_ROOT -WorkbenchRepoPath "$env:LOTUS_WORKSPACE_ROOT/lotus-workbench" -RuntimeHolder $env:LOTUS_CANONICAL_RUNTIME_HOLDER -Disposition $env:LOTUS_RECOVERY_DISPOSITION -ExpectedDispositionSha256 $env:LOTUS_RECOVERY_DISPOSITION_SHA256 -Plan $env:LOTUS_RECOVERY_PLAN -Inventory $env:LOTUS_RECOVERY_INVENTORY
```

JSON inspection and approval reads use `ConvertFrom-Json -DateKind String` to preserve
timestamp-shaped metadata exactly; equivalent instants are not equivalent evidence strings.
Never normalize an offset to repair a fingerprint or overwrite historical evidence. An offline
historical derivation must retain raw call hashes, original collection times and separate
derivation provenance; it is not recapture or current runtime authority.

Linux source-only tests
are supported; the Windows canonical listener observer still prevents declaring Linux canonical
runtime execution supported. The dry run performs metadata reads, not archival or retirement.

After reviewing its receipt, invoke the same wrapper with `-Stage ArchiveVerify`. The private
archive directory must already exist, reject reparse paths, and permit access only to the executing
user, SYSTEM and Administrators on Windows (0700 on POSIX). Archive storage must be reviewed for
capacity, confidentiality and retention; archives include image configuration, file bytes and
attributes. Raw child output stays private, not in console/error logs.

Image verification accepts classic Docker-save archives and single-manifest OCI-layout 1.0.0
archives with Docker-save compatibility metadata. Classic configuration IDs remain exact. OCI
source IDs must bind the inspected manifest descriptor; every referenced SHA256 digest, size and
media type is verified independently. Configuration/platform/labels, ordered layers and exact tags
must match the admitted inspection. Raw tar and gzip layers are supported; other encodings,
external blobs and multi-image/index graphs refuse. Gzip content is streamed and its uncompressed
DiffID checked separately, within a cumulative `max_archive_bytes` decompression budget.

Before loading into a **different observed daemon**, both verified manifest/config identities and
all tags must be absent. The wrapper selects exactly one loaded identity from those archive-derived
IDs, then rechecks the archive and restored architecture, OS, configuration, root filesystem and
tags through the CLI. A classic destination may report the exact verified config ID rather than
the source manifest ID; arbitrary IDs or metadata equivalence alone never suffice. Journal entries
retain source ID, permitted restore IDs, archive hash and observed restored ID. Original registry
digests remain archival metadata; loading a tar does not certify registry publication.

Volume verification uses an explicitly supplied immutable worker image containing Python 3 and
GNU tar with numeric ownership, ACL/xattr, sparse and PAX support. It archives a read-only source,
checks before/after filesystem manifests, validates bytes/types/numeric UID/GID/modes, and restores
into a fresh uniquely named volume. The exact restored manifest also compares nanosecond times,
hardlinks, symlinks and xattrs. Unsupported files or lost metadata fail. The kernel limits worker
file size; image archives additionally require operator-provisioned bounded storage capacity.

Only a finished `archive_verified` receipt can admit `-Stage Retire`. Supply its absolute path as
`-VerificationReceipt` and independently reviewed raw SHA256 as
`-ExpectedVerificationReceiptSha256`. The wrapper revalidates archived bytes and restored evidence,
then reobserves each exact target and all consumers before normal `image rm <full-ID>` or
`volume rm <exact-name>`. No force, project-wide removal or prune exists. Multiple image tags may
make normal removal refuse; preserve that failure rather than escalating to force. A successful
native removal is followed by exact absence verification.

### Retirement renewal after a long archive or review

Archive approval, prepared inspection records, archive bytes, verification document and finalized
receipt are immutable provenance. They are not current permission. A live reservation alone cannot
admit retirement without a new complete, start-timed target/consumer observation.

The operator supplies a new closed `lotus.resource-recovery.retirement.v2` disposition.
It contains the original fields plus
`archive_approval_sha256` (raw SHA256 of the **original**, non-renewal disposition) and
`archive_receipt_sha256` (raw SHA256 of its finalized `archive_verified` receipt). Only
`schema_version`, `approved_at` and `expires_at` may differ. Discovery hashes remain unchanged.
Targets/fingerprints, helper files/root, primary source, both contexts/observed daemons, operator,
archive storage, archiver/budget and retention decision must remain identical. Renewal cannot
extend retention, admit another archive or silently chain a renewal as original provenance.

Invoke `-Stage Retire` with the new disposition/hash, original digest-bound discovery plan/inventory and
`-ArchiveDisposition <absolute-original-disposition-path>`. Continue to supply the original
finalized receipt and its independently reviewed hash as the verification parameters. The helper
uses the original approval SHA for archive selection and verifies the full bytes/restored evidence
again. Fresh retirement records are written to the new run directory, never over original
`prepared.json`. The receipt records both current approval and original archive/receipt identities.

The original approval may have expired: its window is checked at its historical decision time,
not treated as live authority. The new approval, independently collected live observations and
primary reservation admission must all be current. The five-minute live freshness limit is unchanged;
expiry, interruption or a changed identity requires explicit recovery/review, not automatic renewal.

## Failure, interruption and retained resources

Receipts are written under private `archive_root/runs/<unique-id>/receipt.json`. A partial archive
is never overwritten; preserve its receipt and obtain a fresh reviewed recovery decision. Each
target's status distinguishes archival request, completed isolated restore, retirement request
and native removal with confirmed absence. Earlier successful targets remain recorded when a
later target fails; `remaining_targets` records the approved targets not yet confirmed absent.
A nonzero child remains nonzero even when failure publication succeeds.
Bounded uppercase refusal codes survive into private receipts and console summaries. Unexpected
messages become generic codes; native stderr and raw configuration never become refusal output.

Verification volumes and loaded verification images are deliberately retained for explicit
operator disposition, including after failure. Volume creation intent and exact helper identity
are journalled before creation. Worker containers also have exact unique names and pre-run intent
receipts; `--rm` is requested on normal completion, not proof of absence after interruption.
Do not call all resources removed from a `retired` source-target
receipt; inspect `helper_resources` and the verification daemon separately. No automatic helper
cleanup or broad historical cleanup is authorized.

Process interruption leaves the canonical operation unfinished. Expiry does not prove Docker
children have stopped or permit another invocation. Follow reservation recovery, inspect child
operations and exact retained resources, and obtain an explicit new decision. Reopening a lock
or possessing its recorded token does not restore admitted authority.

## Verification and promotion

From this checkout, run `python -m pytest tests/unit/test_resource_only_recovery.py -q` and the
repository feature lane. These tests exercise actual archive bytes and policy refusals, not Docker
restore semantics. Promotion additionally requires a reviewed fixture-only reservation, actual
distinct-daemon image restoration, fresh-volume restoration with known bytes/UID/GID/modes,
representative native failures, unrelated-resource equivalence and retained-helper disposition.
No production data, canonical seeds or historical cleanup targets belong in that proof.

Publication follows reviewed PR/main validation and authored wiki synchronization. Issue #935
tracks this bounded capability; parent #934 operational hygiene remains a separate decision.
