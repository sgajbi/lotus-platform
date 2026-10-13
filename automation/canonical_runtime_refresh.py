"""Reviewed incremental handover within the existing canonical reservation."""

from __future__ import annotations

import copy
import re
from collections import Counter

try:
    from automation import canonical_runtime_lease as lease
except ModuleNotFoundError:
    import canonical_runtime_lease as lease


def validate_plan(record: dict, plan: dict, plan_digest: str) -> None:
    fields = {
        "schemaVersion", "reservationId", "holder", "operator", "sourceReceipt",
        "originalScopeDigest", "originalBindingsDigest", "targetScope", "repositoryChanges", "services",
    }
    lease.require(isinstance(plan, dict) and set(plan) in (fields, fields | {"composeConfigDigest"}),
                  "Malformed reviewed refresh plan.")
    lease.require(plan["schemaVersion"] == "lotus.canonical-runtime.refresh.v1"
                  and lease.digest(plan) == plan_digest, "Refresh plan digest differs from review.")
    lease.require(plan["reservationId"] == record["id"] and plan["holder"] == record["holder"]
                  and lease.nonblank(plan["operator"]) and lease.nonblank(plan["sourceReceipt"]),
                  "Refresh requires the original reservation and reviewed operator/source receipt.")
    original, target = record["scope"], plan["targetScope"]
    lease.validate_scope(target)
    lease.require(plan["originalScopeDigest"] == record["scopeDigest"]
                  and plan["originalBindingsDigest"] == lease.digest(record["bindings"]),
                  "Refresh original scope/bindings digest changed.")
    lease.require(target["projects"] == original["projects"] and target["ports"] == original["ports"]
                  and target["sources"].keys() == original["sources"].keys(),
                  "Refresh cannot expand projects, ports or runtime mode.")
    changes = plan["repositoryChanges"]
    changed = {repo for repo in original["sources"] if original["sources"][repo] != target["sources"][repo]}
    lease.require(isinstance(changes, dict) and set(changes) == changed, "Exact changed repository allowlist required.")
    for repo, change in changes.items():
        lease.require(isinstance(change, dict) and set(change) == {"from", "to", "disposition"}
                      and change["from"] == original["sources"][repo] and change["to"] == target["sources"][repo]
                      and change["disposition"] in {"source-only", "service-refresh"},
                      "Reviewed old-to-new source disposition required.")
    services = plan["services"]
    lease.require(isinstance(services, list), "Explicit service allowlist required.")
    lease.require(not services or isinstance(plan.get("composeConfigDigest"), str) and
                  re.fullmatch(r"sha256:[0-9a-f]{64}", plan["composeConfigDigest"]) is not None,
                  "Service refresh requires a reviewed evaluated Compose configuration digest.")
    identities = set()
    for item in services:
        lease.require(isinstance(item, dict) and set(item) == {"repository", "project", "service"}
                      and all(lease.nonblank(value) for value in item.values()), "Malformed refresh service.")
        identity = (item["project"], item["service"])
        lease.require(identity not in identities and item["project"] in original["projects"]
                      and item["repository"] in target["sources"], "Duplicate or unadmitted refresh service.")
        identities.add(identity)
        lease.require(item["repository"] not in changes or changes[item["repository"]]["disposition"] == "service-refresh",
                      "Source-only disposition cannot replace runtime images.")
    lease.require(bool(changes or services), "Empty refresh is not a handover.")
    lease.require(all(change["disposition"] != "service-refresh" or any(
        item["repository"] == repo for item in services
    ) for repo, change in changes.items()), "Image source changes require explicit affected services.")


def validate_resources(resources: list, bindings: list) -> None:
    expected = {item["id"]: item for item in bindings if item["kind"] == "container"}
    lease.require(isinstance(resources, list) and len(resources) == len(expected), "Complete immutable image inventory required.")
    seen = set()
    for item in resources:
        lease.require(isinstance(item, dict) and set(item) == {
            "id", "project", "service", "imageId", "sourceRevision", "repository", "checkout",
        }, "Malformed refresh image inventory.")
        identity = item["id"]
        lease.require(identity in expected and identity not in seen
                      and item["project"] == expected[identity]["project"]
                      and item["checkout"] == expected[identity]["checkout"]
                      and re.fullmatch(r"sha256:[0-9a-f]{64}", item["imageId"] or ""),
                      "Image inventory differs from actual container bindings.")
        seen.add(identity)


def validate_pending(record: dict) -> None:
    pending = record["operation"]["refresh"]
    lease.require(isinstance(pending, dict) and set(pending) == {"plan", "digest", "originalResources", "preparedImages"},
                  "Malformed pending refresh.")
    validate_plan(record, pending["plan"], pending["digest"])
    validate_resources(pending["originalResources"], record["bindings"])
    if pending["preparedImages"] is not None:
        validate_images(pending["plan"], pending["preparedImages"])


def validate_images(plan: dict, images: list) -> None:
    expected = {(item["project"], item["service"]): item for item in plan["services"]}
    lease.require(isinstance(images, list) and len(images) == len(expected), "Every planned service requires immutable image evidence.")
    seen = set()
    for image in images:
        lease.require(isinstance(image, dict) and set(image) == {
            "project", "service", "repository", "checkout", "sourceRevision", "imageId",
        }, "Malformed prepared image evidence.")
        identity = (image["project"], image["service"])
        lease.require(identity in expected and identity not in seen, "Unplanned or duplicate prepared image.")
        service = expected[identity]
        lease.require(image["repository"] == service["repository"]
                      and image["checkout"] == plan["targetScope"]["projects"][image["project"]]
                      and image["sourceRevision"] == plan["targetScope"]["sources"][image["repository"]]
                      and re.fullmatch(r"sha256:[0-9a-f]{64}", image["imageId"] or ""),
                      "Prepared image does not bind the reviewed immutable source/checkout.")
        seen.add(identity)


def admitted(book, holder, now, token):
    record = lease.current(book)
    lease.require(record is not None, "No refresh reservation exists.")
    lease.owner(record, holder, now)
    operation = record["operation"]
    lease.require(operation is not None and operation["token"] == token and "refresh" in operation,
                  "Matching pending refresh operation required.")
    return record, operation["refresh"]


def begin(book, *, holder, scope, bindings, resources, now, plan, plan_digest, token):
    record = lease.current(book)
    lease.require(record is not None, "No acquired refresh reservation.")
    lease.owner(record, holder, now)
    lease.require(record["operation"] is None and lease.nonblank(token), "Unfinished or concurrent operation; refresh refused.")
    validate_plan(record, plan, plan_digest)
    lease.require(scope == plan["targetScope"], "Current source vector differs from reviewed target.")
    lease.validate_bindings(bindings, record["scope"])
    lease.require(bindings == record["bindings"], "Original bindings changed before refresh.")
    validate_resources(resources, bindings)
    for service in plan["services"]:
        lease.require(any(item["project"] == service["project"] and item["service"] == service["service"]
                          for item in resources), "Planned service has no acquired container.")
    record["operation"] = {"token": token, "action": "change", "atUtc": now.isoformat(), "refresh": {
        "plan": copy.deepcopy(plan), "digest": plan_digest, "originalResources": copy.deepcopy(resources), "preparedImages": None,
    }}
    lease.event(book, record, "begin-refresh", holder, now, planDigest=plan_digest,
                originalScopeDigest=record["scopeDigest"], originalBindingsDigest=lease.digest(bindings))
    return record


def preflight(book, *, holder, scope, bindings, resources, now, token):
    record, pending = admitted(book, holder, now, token)
    lease.require(scope == pending["plan"]["targetScope"], "Refresh source vector drifted.")
    lease.require(bindings == record["bindings"] and resources == pending["originalResources"],
                  "Original resources changed before replacement.")
    return record


def prepare(book, *, images, **common):
    record = preflight(book, **common)
    pending = record["operation"]["refresh"]
    lease.require(pending["preparedImages"] is None, "Images already prepared; no silent image replacement.")
    validate_images(pending["plan"], images)
    pending["preparedImages"] = copy.deepcopy(images)
    lease.event(book, record, "prepare-refresh", common["holder"], common["now"],
                planDigest=pending["digest"], images=copy.deepcopy(images))
    return record


def finish(book, *, holder, scope, bindings, resources, now, token, outcome):
    record = lease.current(book)
    lease.require(record is not None, "No pending refresh.")
    lease.owner(record, holder, now, teardown=outcome == "failure")
    operation = record["operation"]
    lease.require(operation is not None and operation["token"] == token and "refresh" in operation,
                  "Matching pending refresh operation required.")
    pending = operation["refresh"]
    lease.require(outcome in {"success", "failure"}, "Truthful refresh outcome required.")
    if outcome == "failure":
        lease.event(book, record, "refresh-failure", holder, now, planDigest=pending["digest"],
                    observedScopeDigest=lease.digest(scope), observedBindingsDigest=lease.digest(bindings))
        return record  # Original authority and unfinished operation remain recoverable.
    lease.require(scope == pending["plan"]["targetScope"], "Refresh source vector drifted.")
    lease.validate_bindings(bindings, scope)
    validate_resources(resources, bindings)
    selected = {(item["project"], item["service"]) for item in pending["plan"]["services"]}
    original = pending["originalResources"]
    untouched = {item["id"] for item in original if (item["project"], item["service"]) not in selected}
    untouched.update(item["id"] for item in record["bindings"] if item["kind"] == "host-process")
    lease.require([item for item in bindings if item["id"] in untouched] == [
        item for item in record["bindings"] if item["id"] in untouched
    ] and [item for item in resources if item["id"] in untouched] == [item for item in original if item["id"] in untouched],
                  "Untouched resource binding/image changed during refresh.")
    before_selected = [item for item in original if (item["project"], item["service"]) in selected]
    after_selected = [item for item in resources if item["id"] not in untouched]
    lease.require(len(after_selected) == len(before_selected), "Incomplete or additional replacement resources.")
    images = pending["preparedImages"]
    lease.require(not selected or images is not None, "Replacement before immutable image preparation refused.")
    expected_images = {(item["project"], item["service"]): item for item in images or []}
    original_bindings = {item["id"]: item for item in record["bindings"]}
    lease.require(len(bindings) == len(record["bindings"]), "Additional or missing runtime bindings.")
    for identity in selected:
        lease.require(sum((item["project"], item["service"]) == identity for item in before_selected)
                      == sum((item["project"], item["service"]) == identity for item in after_selected),
                      "Replacement service cardinality changed.")
        old_ids = {item["id"] for item in before_selected if (item["project"], item["service"]) == identity}
        new_ids = {item["id"] for item in after_selected if (item["project"], item["service"]) == identity}
        lease.require(Counter(lease.digest({k: v for k, v in item.items() if k != "id"})
                              for item in record["bindings"] if item["id"] in old_ids)
                      == Counter(lease.digest({k: v for k, v in item.items() if k != "id"})
                                 for item in bindings if item["id"] in new_ids),
                      "Replacement changed acquired ports/project/checkout multiplicity.")
    for image in after_selected:
        expected = expected_images.get((image["project"], image["service"]))
        lease.require(expected is not None and {key: image[key] for key in expected} == expected,
                      "Replacement image/source differs from prepared evidence.")
        binding = next(item for item in bindings if item["id"] == image["id"])
        allowed = [original_bindings[item["id"]] for item in before_selected
                   if (item["project"], item["service"]) == (image["project"], image["service"])]
        lease.require(any({k: value for k, value in binding.items() if k != "id"} == {
            k: value for k, value in item.items() if k != "id"
        } for item in allowed), "Replacement changed acquired ports/project/checkout.")
    old_digest = record["scopeDigest"]
    record["scope"], record["scopeDigest"] = copy.deepcopy(scope), lease.digest(scope)
    record["bindings"], record["operation"], record["state"] = copy.deepcopy(bindings), None, "active"
    lease.event(book, record, "finish-refresh", holder, now, plan=copy.deepcopy(pending["plan"]),
                planDigest=pending["digest"], originalScopeDigest=old_digest, targetScopeDigest=record["scopeDigest"],
                bindingsDigest=lease.digest(bindings), runtimeImages=copy.deepcopy(resources))
    return record


def recover(book, *, holder, scope, bindings, resources, now, receipt):
    record = lease.current(book)
    lease.require(record is not None, "No refresh to recover.")
    lease.owner(record, holder, now)
    operation = record["operation"]
    lease.require(operation is not None and "refresh" in operation, "No pending refresh to recover.")
    pending = operation["refresh"]
    lease.require(isinstance(receipt, dict) and set(receipt) == {
        "holder", "operator", "sourceReceipt", "scopeDigest", "bindingsDigest", "reservationId", "refreshPlanDigest", "disposition",
    }, "Explicit reviewed refresh recovery receipt required.")
    lease.require(receipt["reservationId"] == record["id"] and receipt["refreshPlanDigest"] == pending["digest"],
                  "Recovery does not bind the pending reservation/plan.")
    lease.handover({key: receipt[key] for key in ("holder", "operator", "sourceReceipt", "scopeDigest", "bindingsDigest")}, holder, scope, bindings)
    if receipt["disposition"] == "complete":
        finish(book, holder=holder, scope=scope, bindings=bindings, resources=resources, now=now,
               token=operation["token"], outcome="success")
    else:
        lease.require(receipt["disposition"] == "abort" and scope == record["scope"]
                      and bindings == record["bindings"] and resources == pending["originalResources"],
                      "Abort requires exact restored original sources/resources.")
        record["operation"] = None
    lease.event(book, record, "recover-refresh", holder, now, receipt=copy.deepcopy(receipt))
    return record
