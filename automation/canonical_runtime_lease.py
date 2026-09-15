"""Durable canonical local-runtime admission; not production IAM."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any

SCHEMA = "lotus.canonical-runtime.reservations.v1"
LIVE = {"acquired", "active"}
FIELDS = {"id", "holder", "purpose", "teardownOwner", "startUtc", "expiryUtc",
          "state", "scope", "scopeDigest", "bindings", "events", "operation"}


class ReservationRefusal(ValueError):
    """Ambiguous, expired or foreign resource authority was refused."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReservationRefusal(message)


def nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError) as exc:
        raise ReservationRefusal("Expected an aware UTC timestamp.") from exc
    require(parsed.utcoffset() == timedelta(0), "Expected an aware UTC timestamp.")
    return parsed


def digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def validate_scope(scope: dict) -> None:
    require(isinstance(scope, dict) and set(scope) == {"projects", "ports", "sources"},
            "Explicit project/port/source scope required.")
    require(isinstance(scope["projects"], dict) and bool(scope["projects"]) and all(
        nonblank(project) and nonblank(root) for project, root in scope["projects"].items()
    ), "Explicit project/checkouts required.")
    ports = scope["ports"]
    require(isinstance(ports, list) and bool(ports) and all(
        type(port) is int and 1 <= port <= 65535 for port in ports
    ), "Valid host ports required.")
    require(ports == sorted(set(ports)), "Ports must be sorted and unique.")
    sources = scope["sources"]
    require(isinstance(sources, dict) and bool(sources) and all(
        nonblank(repo) and isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha)
        for repo, sha in sources.items()
    ), "Full immutable source revisions required.")


def validate_bindings(bindings: list, scope: dict) -> None:
    require(isinstance(bindings, list), "Actual resource inventory required.")
    ids = set()
    for item in bindings:
        require(isinstance(item, dict) and set(item) == {"kind", "id", "project", "checkout", "ports"},
                "Malformed resource binding.")
        require(item["kind"] in {"container", "host-process"} and nonblank(item["id"])
                and item["id"] not in ids, "Unique actual resource identity required.")
        ids.add(item["id"])
        ports = item["ports"]
        require(isinstance(ports, list) and all(type(port) is int for port in ports)
                and ports == sorted(set(ports)) and set(ports) <= set(scope["ports"]),
                "Observed ports outside the admitted scope.")
        if item["kind"] == "container":
            require(scope["projects"].get(item["project"]) == item["checkout"],
                    "Foreign project/checkout cannot become a grant.")
        else:
            require(item["project"] == "host-listener" and item["checkout"] == "" and bool(ports),
                    "Host listeners require actual PID/birth identity and ports.")
    require(bindings == sorted(bindings, key=lambda item: (item["kind"], item["id"])),
            "Inventory must be deterministically ordered.")


def validate_book(book: dict) -> None:
    require(isinstance(book, dict) and set(book) == {"schemaVersion", "revision", "reservations"}
            and book["schemaVersion"] == SCHEMA, "Malformed reservation book.")
    require(type(book["revision"]) is int and book["revision"] >= 0
            and isinstance(book["reservations"], list), "Malformed chronology.")
    ids, revisions = set(), []
    for record in book["reservations"]:
        require(isinstance(record, dict) and set(record) == FIELDS,
                "Malformed reservation; refuse missing/default holder grants.")
        require(all(nonblank(record[key]) for key in ("id", "holder", "purpose"))
                and record["id"] not in ids, "Unique identity, explicit holder and purpose required.")
        ids.add(record["id"])
        require(record["holder"] == record["teardownOwner"], "Holder owns teardown.")
        validate_scope(record["scope"])
        require(digest(record["scope"]) == record["scopeDigest"], "Scope identity changed.")
        require(utc(record["startUtc"]) < utc(record["expiryUtc"])
                <= utc(record["startUtc"]) + timedelta(hours=8), "Bounded expiry must follow start.")
        require(record["state"] in LIVE | {"released", "reclaimed"}, "Unknown lifecycle state.")
        validate_bindings(record["bindings"], record["scope"])
        operation = record["operation"]
        require(operation is None or (isinstance(operation, dict) and set(operation) == {
            "token", "action", "atUtc",
        } and nonblank(operation["token"]) and operation["action"] in {"change", "teardown"}),
                "Malformed admitted operation.")
        if operation:
            utc(operation["atUtc"])
            require(record["state"] in LIVE, "A terminal record cannot retain an operation.")
        require(isinstance(record["events"], list), "Event history required.")
        for entry in record["events"]:
            require(isinstance(entry, dict) and all(nonblank(entry.get(key))
                    for key in ("actor", "action", "atUtc"))
                    and type(entry.get("revision")) is int, "Malformed event history.")
            utc(entry["atUtc"])
            revisions.append(entry["revision"])
        ordered = [entry["revision"] for entry in record["events"]]
        require(ordered == sorted(set(ordered)), "Record event chronology is reversed or duplicated.")
    require(sorted(revisions) == list(range(1, book["revision"] + 1)), "Broken event chronology.")
    require(sum(record["state"] in LIVE for record in book["reservations"]) <= 1,
            "Multiple reservations, including overlapping ports, are refused.")


def empty_book() -> dict:
    return {"schemaVersion": SCHEMA, "revision": 0, "reservations": []}


def current(book: dict) -> dict | None:
    validate_book(book)
    return next((record for record in book["reservations"] if record["state"] in LIVE), None)


def owner(record: dict, holder: str, now: datetime, *, teardown: bool = False) -> None:
    require(nonblank(holder) and record["holder"] == holder,
            f"Held by {record['holder']} for {record['purpose']} since {record['startUtc']} "
            f"until {record['expiryUtc']}; explicit handover required.")
    require(teardown or now < utc(record["expiryUtc"]),
            f"Expired at {record['expiryUtc']}; named reclaim or teardown required.")


def event(book: dict, record: dict, action: str, holder: str, now: datetime, **evidence: Any) -> None:
    book["revision"] += 1
    record["events"].append({"action": action, "actor": holder, "atUtc": now.isoformat(),
                             "revision": book["revision"], **evidence})


def handover(receipt: Any, holder: str, scope: dict, bindings: list) -> None:
    require(isinstance(receipt, dict) and set(receipt) == {
        "holder", "operator", "sourceReceipt", "scopeDigest", "bindingsDigest",
    }, "Live resources/reclaim require an explicit operator handover receipt.")
    require(receipt["holder"] == holder and nonblank(receipt["operator"])
            and nonblank(receipt["sourceReceipt"]), "Explicit handover identities/source required.")
    require(receipt["scopeDigest"] == digest(scope) and receipt["bindingsDigest"] == digest(bindings),
            "Handover does not bind actual resource identities/scope.")


def acquire(book: dict, *, holder: str, purpose: str, expires: str, scope: dict,
            bindings: list, now: datetime, reservation_id: str, receipt: Any = None,
            reclaim: bool = False) -> dict:
    validate_scope(scope)
    validate_bindings(bindings, scope)
    previous = current(book)
    require(all(nonblank(value) for value in (holder, purpose, reservation_id)),
            "Explicit holder, purpose and reservation identity required before mutation.")
    require(now < utc(expires) <= now + timedelta(hours=8), "Future expiry within eight hours required.")
    require(reservation_id not in {record["id"] for record in book["reservations"]}, "Duplicate identity.")
    if previous:
        require(reclaim and now >= utc(previous["expiryUtc"]),
                f"Runtime held by {previous['holder']} until {previous['expiryUtc']}; no second reservation.")
        require(previous["scope"] == scope, "Reclaim preserves exact expired scope.")
        handover(receipt, holder, scope, bindings)
        previous["state"], previous["operation"] = "reclaimed", None
        event(book, previous, "reclaim", holder, now, receipt=receipt)
    else:
        require(not reclaim, "No expired reservation exists to reclaim.")
        if bindings:
            handover(receipt, holder, scope, bindings)
    record = {"id": reservation_id, "holder": holder, "purpose": purpose, "teardownOwner": holder,
              "startUtc": now.isoformat(), "expiryUtc": expires, "state": "acquired", "scope": scope,
              "scopeDigest": digest(scope), "bindings": bindings, "events": [], "operation": None}
    book["reservations"].append(record)
    event(book, record, "acquire", holder, now, receipt=receipt)
    return record


def preflight(book: dict, *, holder: str, scope: dict, bindings: list,
              now: datetime, teardown: bool = False) -> dict:
    record = current(book)
    require(record is not None, "No acquired canonical reservation; unreserved resources are not yours.")
    owner(record, holder, now, teardown=teardown)
    require(record["operation"] is None, "Unfinished operation: explicit holder recovery required.")
    require(record["scope"] == scope, "Projects, ports or sources differ from acquired scope.")
    validate_bindings(bindings, scope)
    require(record["bindings"] == bindings, "Changed resource identities; names cannot manufacture grants.")
    return record


def begin(book: dict, *, holder: str, scope: dict, bindings: list, now: datetime,
          action: str, token: str) -> dict:
    require(action in {"change", "teardown"} and nonblank(token), "Explicit operation required.")
    record = preflight(book, holder=holder, scope=scope, bindings=bindings,
                       now=now, teardown=action == "teardown")
    record["operation"] = {"token": token, "action": action, "atUtc": now.isoformat()}
    event(book, record, "begin", holder, now, operation=record["operation"].copy())
    return record


def operation_preflight(book: dict, *, holder: str, scope: dict, bindings: list,
                        now: datetime, token: str) -> dict:
    record = current(book)
    require(record is not None, "No admitted operation exists.")
    owner(record, holder, now)
    require(record["operation"] is not None and nonblank(token)
            and record["operation"]["token"] == token, "Matching admitted operation token required.")
    require(record["scope"] == scope, "Scope/source changed during operation.")
    validate_bindings(bindings, scope)
    return record  # Read proof inside admitted startup, not arbitrary resource publication.


def finish(book: dict, *, holder: str, scope: dict, bindings: list, now: datetime,
           token: str, outcome: str) -> dict:
    record = current(book)
    require(record is not None, "No admitted operation exists.")
    owner(record, holder, now, teardown=True)  # Record failure/teardown after expiry, never start.
    operation = record["operation"]
    require(operation is not None and nonblank(token) and operation["token"] == token,
            "Matching admitted operation required; arbitrary bind refused.")
    require(record["scope"] == scope, "Scope/source changed during operation; reconcile explicitly.")
    validate_bindings(bindings, scope)
    require(outcome in {"success", "failure"}, "Truthful operation outcome required.")
    released = operation["action"] == "teardown" and outcome == "success" and not bindings
    record["bindings"], record["operation"] = bindings, None
    record["state"] = "released" if released else "active"
    event(book, record, "release" if released else "finish", holder, now, outcome=outcome,
          bindingsDigest=digest(bindings), teardownProved=released, operationAction=operation["action"])
    return record  # Nonzero cleanup outcome remains active, even with empty inventory.


def recover(book: dict, *, holder: str, scope: dict, bindings: list,
            now: datetime, receipt: Any) -> dict:
    record = current(book)
    require(record is not None, "No reservation exists to recover.")
    owner(record, holder, now)
    require(record["scope"] == scope, "Recovery preserves exact source/scope.")
    validate_bindings(bindings, scope)
    handover(receipt, holder, scope, bindings)
    record["bindings"], record["operation"], record["state"] = bindings, None, "active"
    event(book, record, "recover", holder, now, receipt=receipt)
    return record
