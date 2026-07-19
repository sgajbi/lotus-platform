from __future__ import annotations

import json
import subprocess
import sys
from argparse import ArgumentParser
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


PLATFORM_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT_DIR = PLATFORM_ROOT / "output"
DEFAULT_OUTPUT_JSON = "rfc-issue-coverage-audit.json"
DEFAULT_OUTPUT_MARKDOWN = "rfc-issue-coverage-audit.md"
STATUS_PREFIX = "status/"
PRIORITY_PREFIX = "priority/"
DUPLICATE_LABELS = {"duplicate", "status/duplicate", "resolution/duplicate"}
SUPERSEDED_LABELS = {"superseded", "status/superseded", "resolution/superseded"}


@dataclass(frozen=True)
class IssueExpectation:
    repository: str
    number: int
    url: str | None
    required_labels: tuple[str, ...]
    source_path: str
    source_name: str
    status: str | None

    @property
    def key(self) -> str:
        return f"{self.repository}#{self.number}"


@dataclass(frozen=True)
class IssueSnapshot:
    repository: str
    number: int
    exists: bool
    state: str | None = None
    title: str | None = None
    url: str | None = None
    labels: tuple[str, ...] = ()
    error: str | None = None

    @property
    def key(self) -> str:
        return f"{self.repository}#{self.number}"


@dataclass(frozen=True)
class IssueAuditRecord:
    repository: str
    number: int
    url: str | None
    state: str | None
    title: str | None
    labels: tuple[str, ...]
    required_labels: tuple[str, ...]
    missing_labels: tuple[str, ...]
    status_labels: tuple[str, ...]
    priority_labels: tuple[str, ...]
    duplicate_posture: str
    referenced_by: tuple[str, ...]
    gh_fix_commands: tuple[str, ...]
    exists: bool = True
    error: str | None = None

    @property
    def status(self) -> str:
        if not self.exists:
            return "missing_issue"
        if self.missing_labels:
            return "missing_labels"
        return "ok"


@dataclass(frozen=True)
class IssueCoverageAudit:
    contract_path: str
    rfc: str
    total_issue_references: int
    unique_issues: int
    ok: int
    missing_issues: int
    missing_label_issues: int
    records: tuple[IssueAuditRecord, ...]
    duplicate_contract_references: tuple[str, ...]

    @property
    def has_failures(self) -> bool:
        return self.missing_issues > 0 or self.missing_label_issues > 0


def _canonical_repository(repository: str | None, fallback_owner: str | None = None) -> str:
    if not repository:
        raise ValueError("Issue reference is missing repository")
    repository = repository.strip()
    if "/" in repository:
        return repository
    if fallback_owner:
        return f"{fallback_owner}/{repository}"
    raise ValueError(f"Issue repository must be owner/repo or fallback owner must be supplied: {repository}")


def _label_for_slice(slice_id: str) -> str:
    return f"rfc/{slice_id}"


def _root_rfc_label(rfc: str) -> str:
    return f"rfc/{rfc}"


def _source_name(node: dict[str, Any]) -> str:
    for key in ("capability", "boundary", "family", "name", "title", "id"):
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unnamed contract entry"


def _walk_contract_nodes(value: Any, path: str = "$") -> list[tuple[str, dict[str, Any]]]:
    nodes: list[tuple[str, dict[str, Any]]] = []
    if isinstance(value, dict):
        if isinstance(value.get("issues"), list):
            nodes.append((path, value))
        for key, item in value.items():
            nodes.extend(_walk_contract_nodes(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            nodes.extend(_walk_contract_nodes(item, f"{path}[{index}]"))
    return nodes


def load_issue_expectations(contract_path: Path, fallback_owner: str | None = None) -> tuple[str, list[IssueExpectation]]:
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    rfc = str(contract.get("rfc") or contract.get("rfcId") or "").strip()
    if not rfc:
        raise ValueError("Contract must include an rfc or rfcId value")

    expectations: list[IssueExpectation] = []
    root_label = _root_rfc_label(rfc)
    for source_path, node in _walk_contract_nodes(contract):
        slice_ids = tuple(str(slice_id).strip() for slice_id in node.get("sliceIds", []) if str(slice_id).strip())
        required_labels = tuple(dict.fromkeys([root_label, *(_label_for_slice(slice_id) for slice_id in slice_ids)]))
        for issue in node.get("issues", []):
            if not isinstance(issue, dict):
                raise ValueError(f"{source_path}.issues contains a non-object issue reference")
            repository = _canonical_repository(str(issue.get("repository") or ""), fallback_owner)
            number = issue.get("number")
            if not isinstance(number, int):
                raise ValueError(f"{source_path}.issues contains an issue without an integer number")
            expectations.append(
                IssueExpectation(
                    repository=repository,
                    number=number,
                    url=issue.get("url") if isinstance(issue.get("url"), str) else None,
                    required_labels=required_labels,
                    source_path=source_path,
                    source_name=_source_name(node),
                    status=node.get("status") if isinstance(node.get("status"), str) else None,
                )
            )
    return rfc, expectations


def load_issue_snapshots_from_json(path: Path) -> dict[str, IssueSnapshot]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "issues" in raw:
        raw_issues = raw["issues"]
    else:
        raw_issues = raw
    if not isinstance(raw_issues, list):
        raise ValueError("Issue snapshot JSON must be a list or an object with an issues list")

    snapshots: dict[str, IssueSnapshot] = {}
    for item in raw_issues:
        if not isinstance(item, dict):
            raise ValueError("Issue snapshot entries must be objects")
        repository = _canonical_repository(str(item.get("repository") or ""))
        number = item.get("number")
        if not isinstance(number, int):
            raise ValueError("Issue snapshot entry is missing an integer number")
        labels = tuple(
            sorted(
                label.get("name", label) if isinstance(label, dict) else str(label)
                for label in item.get("labels", [])
            )
        )
        snapshot = IssueSnapshot(
            repository=repository,
            number=number,
            exists=bool(item.get("exists", True)),
            state=str(item.get("state")) if item.get("state") is not None else None,
            title=str(item.get("title")) if item.get("title") is not None else None,
            url=str(item.get("url")) if item.get("url") is not None else None,
            labels=labels,
            error=str(item.get("error")) if item.get("error") is not None else None,
        )
        snapshots[snapshot.key] = snapshot
    return snapshots


def _gh_issue_snapshot(repository: str, number: int) -> IssueSnapshot:
    command = [
        "gh",
        "issue",
        "view",
        str(number),
        "--repo",
        repository,
        "--json",
        "number,state,title,labels,url",
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        error = (completed.stderr or completed.stdout or "gh issue view failed").strip()
        return IssueSnapshot(repository=repository, number=number, exists=False, error=error)

    payload = json.loads(completed.stdout)
    labels = tuple(sorted(label["name"] for label in payload.get("labels", [])))
    return IssueSnapshot(
        repository=repository,
        number=number,
        exists=True,
        state=payload.get("state"),
        title=payload.get("title"),
        url=payload.get("url"),
        labels=labels,
    )


def fetch_issue_snapshots(expectations: list[IssueExpectation]) -> dict[str, IssueSnapshot]:
    snapshots: dict[str, IssueSnapshot] = {}
    for expectation in sorted({expectation.key: expectation for expectation in expectations}.values(), key=lambda item: item.key):
        snapshots[expectation.key] = _gh_issue_snapshot(expectation.repository, expectation.number)
    return snapshots


def _referenced_by(expectations: list[IssueExpectation]) -> tuple[str, ...]:
    return tuple(
        f"{expectation.source_path}: {expectation.source_name}"
        for expectation in expectations
    )


def _gh_fix_commands(expectations: list[IssueExpectation], missing_labels: tuple[str, ...]) -> tuple[str, ...]:
    commands: list[str] = []
    first = expectations[0]
    for label in missing_labels:
        commands.append(
            f'gh issue edit {first.number} --repo {first.repository} --add-label "{label}"'
        )
    return tuple(commands)


def _duplicate_posture(snapshot: IssueSnapshot) -> str:
    label_set = set(snapshot.labels)
    title = (snapshot.title or "").lower()
    if label_set & DUPLICATE_LABELS or "duplicate" in title:
        return "duplicate"
    if label_set & SUPERSEDED_LABELS or "superseded" in title:
        return "superseded"
    return "active"


def audit_issue_coverage(
    contract_path: Path,
    expectations: list[IssueExpectation],
    snapshots: dict[str, IssueSnapshot],
    rfc: str,
) -> IssueCoverageAudit:
    grouped: dict[str, list[IssueExpectation]] = {}
    for expectation in expectations:
        grouped.setdefault(expectation.key, []).append(expectation)

    records: list[IssueAuditRecord] = []
    duplicate_contract_references = tuple(
        sorted(key for key, values in grouped.items() if len(values) > 1)
    )
    for key, grouped_expectations in sorted(grouped.items()):
        snapshot = snapshots.get(key)
        if snapshot is None:
            first = grouped_expectations[0]
            snapshot = IssueSnapshot(
                repository=first.repository,
                number=first.number,
                exists=False,
                error="issue was not present in the supplied issue snapshot",
            )
        required_labels = tuple(sorted({label for expectation in grouped_expectations for label in expectation.required_labels}))
        labels = tuple(sorted(snapshot.labels))
        missing_labels = tuple(label for label in required_labels if label not in labels)
        status_labels = tuple(label for label in labels if label.startswith(STATUS_PREFIX))
        priority_labels = tuple(label for label in labels if label.startswith(PRIORITY_PREFIX))
        records.append(
            IssueAuditRecord(
                repository=snapshot.repository,
                number=snapshot.number,
                url=snapshot.url or grouped_expectations[0].url,
                state=snapshot.state,
                title=snapshot.title,
                labels=labels,
                required_labels=required_labels,
                missing_labels=missing_labels,
                status_labels=status_labels,
                priority_labels=priority_labels,
                duplicate_posture=_duplicate_posture(snapshot),
                referenced_by=_referenced_by(grouped_expectations),
                gh_fix_commands=(
                    _gh_fix_commands(grouped_expectations, missing_labels)
                    if snapshot.exists
                    else ()
                ),
                exists=snapshot.exists,
                error=snapshot.error,
            )
        )

    missing_issues = sum(1 for record in records if not record.exists)
    missing_label_issues = sum(1 for record in records if record.exists and record.missing_labels)
    ok = sum(1 for record in records if record.status == "ok")
    return IssueCoverageAudit(
        contract_path=str(contract_path),
        rfc=rfc,
        total_issue_references=len(expectations),
        unique_issues=len(grouped),
        ok=ok,
        missing_issues=missing_issues,
        missing_label_issues=missing_label_issues,
        records=tuple(records),
        duplicate_contract_references=duplicate_contract_references,
    )


def render_markdown(audit: IssueCoverageAudit) -> str:
    lines = [
        "# RFC Issue Coverage Audit",
        "",
        f"- Contract: `{audit.contract_path}`",
        f"- RFC: `{audit.rfc}`",
        f"- Issue references: {audit.total_issue_references}",
        f"- Unique issues: {audit.unique_issues}",
        f"- OK: {audit.ok}",
        f"- Missing issues: {audit.missing_issues}",
        f"- Issues with missing labels: {audit.missing_label_issues}",
        "",
        "| Issue | State | Status | Priority | Duplicate posture | Missing labels | Referenced by |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for record in audit.records:
        issue = f"{record.repository}#{record.number}"
        if record.url:
            issue = f"[{issue}]({record.url})"
        missing = ", ".join(f"`{label}`" for label in record.missing_labels) if record.missing_labels else "-"
        status = ", ".join(f"`{label}`" for label in record.status_labels) if record.status_labels else "-"
        priority = ", ".join(f"`{label}`" for label in record.priority_labels) if record.priority_labels else "-"
        referenced_by = "<br>".join(record.referenced_by)
        lines.append(
            f"| {issue} | `{record.state or 'missing'}` | {status} | {priority} | "
            f"`{record.duplicate_posture}` | {missing} | {referenced_by} |"
        )

    commands = [command for record in audit.records for command in record.gh_fix_commands]
    if commands:
        lines.extend(
            [
                "",
                "## Suggested Label Fix Commands",
                "",
                "The auditor is read-only by default. Review these commands before applying labels:",
                "",
                "```powershell",
                *commands,
                "```",
            ]
        )

    if audit.duplicate_contract_references:
        lines.extend(
            [
                "",
                "## Duplicate Contract References",
                "",
                "These issues are referenced by more than one contract entry. This can be valid for shared blockers, but it should be explicit in closure evidence:",
                "",
                *[f"- `{key}`" for key in audit.duplicate_contract_references],
            ]
        )

    return "\n".join(lines) + "\n"


def write_outputs(audit: IssueCoverageAudit, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / DEFAULT_OUTPUT_JSON
    markdown_path = output_dir / DEFAULT_OUTPUT_MARKDOWN
    json_path.write_text(json.dumps(asdict(audit), indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(audit), encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = ArgumentParser(description="Audit RFC issue references against GitHub issue labels.")
    parser.add_argument("--contract", type=Path, required=True, help="Path to a JSON RFC issue-reference contract.")
    parser.add_argument(
        "--issues-json",
        type=Path,
        help="Optional issue snapshot JSON for tests/offline audits. Live GitHub is queried when omitted.",
    )
    parser.add_argument(
        "--fallback-owner",
        help="Owner to prepend when contract issue repositories use bare repo names.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for JSON/Markdown audit reports.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when missing issues or labels are found.",
    )
    args = parser.parse_args()

    rfc, expectations = load_issue_expectations(args.contract, args.fallback_owner)
    if not expectations:
        print(f"No issue references found in {args.contract}", file=sys.stderr)
        return 1
    snapshots = (
        load_issue_snapshots_from_json(args.issues_json)
        if args.issues_json
        else fetch_issue_snapshots(expectations)
    )
    audit = audit_issue_coverage(args.contract, expectations, snapshots, rfc)
    json_path, markdown_path = write_outputs(audit, args.output_dir)
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")
    if args.strict and audit.has_failures:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
