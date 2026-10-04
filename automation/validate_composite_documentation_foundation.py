"""Validate the composite documentation foundation; never execute financial methods.

Schema authority for source-manifest.v1.json and implementation-ledger.v1.json.
Proof is document integrity/traceability only, not domain or environment acceptance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = Path("docs/composite-performance")
INPUT_HASHES = json.loads(r'''{"01_composite_requirements_source_baseline.md":"30ee292c10d81c495ae7c41c89e1babf6fe2e6d8e019580aa37065ece23ea399","02_composite_gaps_and_lotus_readiness.md":"ab4527d0f0e1962d33c39d4dd05dfc911ca93792c5eae4486b0eb35ec8328acf","03_lotus_composite_implementation_requirements.md":"4877241220d23808cb589c9986b679f9230cb9668547f475d68b1de2c8a05fed","04_lotus_composite_agent_execution_brief.md":"83b99a06d2c276090faa4e887c0e1dfc63e24900a39f3d721bf410fc31cb5c93","05_composite_numerical_oracles.json":"faf40e73c552d117ac466c711ac430551f5e20d8907ec20069bc2f9493316f61","README (1).md":"d6baf171916a2670dd1507624b5fa40fddffeece0d4c7d4e92f7ed9ab84b4615"}''')
PUBLICATION_EDITS = json.loads(r'''[{"from":"# Lotus Composite Performance — Gold-Standard Product Requirements","to":"# Lotus Composite Performance — Product Requirements"},{"from":"- [Neutral source baseline](01_composite_requirements_source_baseline.md): faithful normalization, including the source's historical scope qualifications.","to":"- [Immutable neutral source baseline](source/01_composite_requirements_source_baseline.txt): archival provenance, including historical scope qualifications; the current target overrides release restrictions."},{"from":"- [Gaps, bounded Lotus readiness and vendor comparison](02_composite_gaps_and_lotus_readiness.md): source omissions, observed code boundaries and evidence-based market comparison.","to":"- [Current coverage and reader map](README.md): the single implementation ledger, committed-source observations and owning delivery issues."},{"from":"- [Agent execution brief](04_lotus_composite_agent_execution_brief.md): copy-ready implementation instructions and evidence expectations.","to":"- [RFC-0110](../../rfcs/RFC-0110-composite-performance-product-and-delivery-foundation.md): current delivery instructions, ownership and evidence boundaries. The [original execution brief](source/04_lotus_composite_agent_execution_brief.txt) is archival text; its historical companion references are not current product navigation."},{"from":"**CMP-DON-005.** Closeout distinguishes implemented capability, test evidence, target-environment acceptance and commercial comparative claims. The companion vendor table is a research snapshot; superiority claims require current, like-for-like demonstration and cannot be inferred from competitors' undocumented features.","to":"**CMP-DON-005.** Closeout distinguishes implemented capability, test evidence, target-environment acceptance and comparative claims. Comparative claims require current, like-for-like demonstration and cannot be inferred from undocumented features. Historical comparison material is withheld from public product documentation."},{"from":"- **S0 — Supplied source:** Requirements text pasted by the user in this conversation; normalized in `01_composite_requirements_source_baseline.md`. Screenshots and the original sample workbook were not readable/available for validation.","to":"- **S0 — Supplied source:** User-supplied requirements text, normalized in [the immutable source baseline](source/01_composite_requirements_source_baseline.txt). Screenshots and the original sample workbook were not readable/available for validation."},{"from":"Specific Lotus repository evidence and public vendor references are retained in `02_composite_gaps_and_lotus_readiness.md`. Public vendor material is descriptive evidence, not proof of current deployed functionality, performance or GIPS compliance.","to":"Current committed-source observations and their bounded interpretations live in [the implementation ledger](implementation-ledger.v1.json). The historical comparison input is withheld from public publication. Product support, performance and compliance require their own evidence."}]''')
PUBLICATION_NOTE = "Publication note: this neutral public edition preserves the complete LOTUS-CMP-001 v2.0 target. Navigation and comparative-claim wording were edited under Platform #924; the [source manifest](source-manifest.v1.json) records every editorial substitution. The original four published inputs are immutable archives, not current navigation or executable instructions.\n\n"
STATES = {
    "NOT_ASSESSED", "MISSING", "PARTIAL", "IMPLEMENTED_NOT_VERIFIED",
    "VERIFIED_IN_TEST", "VERIFIED_IN_TARGET_ENVIRONMENT",
    "BLOCKED_ON_APPROVED_POLICY_OR_SOURCE",
}
REPOSITORIES = {"lotus-" + name for name in (
    "platform", "core", "manage", "performance", "risk", "report",
    "render", "archive", "gateway", "workbench",
)}
CLASSES = {
    "COMMITTED_SOURCE_OBSERVATION", "OWNER_SOURCE_ASSESSMENT", "UNIT_TEST",
    "INTEGRATION_TEST", "TARGET_ENVIRONMENT_ACCEPTANCE", "SPECIFICATION_ORACLE",
}
CATALOGUES = {
    "analytics": ("CMP-AN-", 40, 3),
    "reports": ("RPT-", 12, 2),
    "scenarios": ("AT-", 105, 3),
    "institutional_decisions": ("DEC-", 16, 2),
    "service_objectives": ("SLO-", 10, 2),
}
ORACLE_SCENARIOS = [43, 44, 25, 26, 19, 51, 50, 52, 52, 63, 65, 67, 70, 74, 58, 58, 71, 46]


class FoundationError(ValueError):
    """A document contract failed; messages name locations, never source values."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise FoundationError(code)


def object_keys(value: object, keys: set[str], code: str) -> None:
    require(isinstance(value, dict) and set(value) == keys, code)


def unique_rows(rows: object, key: str, expected: set[str], code: str) -> dict:
    require(isinstance(rows, list), code + ":array")
    require(all(isinstance(row, dict) and isinstance(row.get(key), str) for row in rows), code + ":row")
    ids = [row[key] for row in rows]
    require(len(ids) == len(set(ids)) and set(ids) == expected, code + ":inventory")
    return {row[key]: row for row in rows}


def issue_ref(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(
        r"https://github.com/sgajbi/lotus-[a-z]+/issues/[1-9][0-9]*", value
    ))


def committed_ref(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{40}", value))


def relative_path(value: object) -> bool:
    return isinstance(value, str) and bool(value) and not (
        value.startswith(("/", "\\")) or "\\" in value or ":" in value
        or ".." in Path(value).parts
    )


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "json:object")
    return value


def source_definitions(text: str, pattern: str) -> dict[str, int]:
    rows = {}
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(pattern, line)
        if match:
            require(match[1] not in rows, "source:duplicate-definition")
            rows[match[1]] = number
    return rows


def validate_publication(root: Path, manifest: dict, primary: str) -> tuple[dict, dict]:
    object_keys(manifest, {
        "schema_version", "programme_issue", "foundation_issue", "source_package_id",
        "archive_semantics", "inputs", "editorial_substitutions", "publication_note",
    }, "manifest:shape")
    require(manifest["schema_version"] == "lotus-composite-source-manifest.v1", "manifest:version")
    require(manifest["programme_issue"] == "https://github.com/sgajbi/lotus-platform/issues/923", "manifest:programme")
    require(manifest["foundation_issue"] == "https://github.com/sgajbi/lotus-platform/issues/924", "manifest:foundation")
    rows = unique_rows(manifest["inputs"], "original_filename", set(INPUT_HASHES), "manifest:inputs")
    published = {
        "01_composite_requirements_source_baseline.md",
        "03_lotus_composite_implementation_requirements.md",
        "04_lotus_composite_agent_execution_brief.md",
        "05_composite_numerical_oracles.json",
    }
    expected_files = set()
    for name, row in rows.items():
        object_keys(row, {"original_filename", "sha256", "publication_status", "archive_path"}, "manifest:input-shape")
        require(row["sha256"] == INPUT_HASHES[name], "manifest:immutable-hash")
        if name in published:
            expected = "source/" + re.sub(r"\.md$", ".txt", name)
            require(row["publication_status"] == "PUBLISHED_IMMUTABLE_ARCHIVE" and row["archive_path"] == expected, "manifest:public-boundary")
            expected_files.add(Path(expected).name)
            raw = (root / DOCS / expected).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == row["sha256"], "archive:hash")
        else:
            require(row["publication_status"] == "WITHHELD_NON_NEUTRAL_RESEARCH" and row["archive_path"] is None, "manifest:withheld-boundary")
    require({path.name for path in (root / DOCS / "source").iterdir()} == expected_files, "archive:file-set")
    require(manifest["editorial_substitutions"] == PUBLICATION_EDITS, "publication:undeclared-edit")
    original = (root / DOCS / "source/03_lotus_composite_implementation_requirements.txt").read_text(encoding="utf-8")
    expected = original
    for edit in PUBLICATION_EDITS:
        require(expected.count(edit["from"]) == 1, "publication:source-edit-count")
        expected = expected.replace(edit["from"], edit["to"])
    expected = expected.replace("Companion documents:", PUBLICATION_NOTE + "Companion documents:")
    require(primary.strip() == expected.strip(), "publication:semantic-drift")
    baseline = (root / DOCS / "source/01_composite_requirements_source_baseline.txt").read_text(encoding="utf-8")
    return (
        source_definitions(original, r"^(?:\*\*|\| )(CMP-[A-Z]+-\d{3})"),
        source_definitions(baseline, r"^\| (SRC-[A-Z]+-\d{2}) \|"),
    )


def validate_evidence(item: object, expected_class: str) -> None:
    require(isinstance(item, dict), "evidence:object")
    required = {"evidence_class", "repository", "commit", "path", "scope", "result", "run_ref"}
    require(required <= set(item), "evidence:required-fields")
    require(item["evidence_class"] == expected_class, "evidence:class")
    require(item["repository"] in REPOSITORIES and committed_ref(item["commit"]), "evidence:source-identity")
    require(relative_path(item["path"]) and isinstance(item["scope"], str) and bool(item["scope"].strip()), "evidence:scope")
    require(item["result"] == "PASS" and isinstance(item["run_ref"], str) and item["run_ref"].startswith("https://github.com/sgajbi/"), "evidence:receipt")
    if expected_class in {"UNIT_TEST", "INTEGRATION_TEST", "TARGET_ENVIRONMENT_ACCEPTANCE"}:
        require(isinstance(item.get("actual_test_ref"), str) and bool(item["actual_test_ref"]), "evidence:actual-test")
    if expected_class == "TARGET_ENVIRONMENT_ACCEPTANCE":
        require(isinstance(item.get("environment"), str) and bool(item["environment"]), "evidence:environment")


def validate_catalogues(ledger: dict, immutable_target: str) -> None:
    """Catalogue rows index specification obligations, not implementation evidence."""
    section = ""
    sections_by_line = {}
    for number, line in enumerate(immutable_target.splitlines(), 1):
        if re.match(r"^## \d+\.", line):
            section = line.removeprefix("## ")
        sections_by_line[number] = section
    for key, (prefix, count, width) in CATALOGUES.items():
        expected_ids = {prefix + str(n).zfill(width) for n in range(1, count + 1)}
        definitions = source_definitions(
            immutable_target, r"^\| (" + re.escape(prefix) + r"\d{" + str(width) + r"}) \|"
        )
        require(set(definitions) == expected_ids, "catalogue:canonical-inventory")
        catalogue = unique_rows(ledger[key], "id", expected_ids, key)
        expected_state = "UNRESOLVED" if key == "institutional_decisions" else "PLANNED"
        keys = {"id", "source_line", "source_ref", "state", "document_ref"}
        if key == "institutional_decisions":
            keys.add("approval_ref")
        for identifier, row in catalogue.items():
            object_keys(row, keys, "catalogue:shape")
            state_error = "decision:approval-boundary" if key == "institutional_decisions" else "catalogue:state"
            require(row["state"] == expected_state, state_error)
            require(
                row["source_ref"] == "source/03_lotus_composite_implementation_requirements.txt"
                and type(row["source_line"]) is int
                and row["source_line"] == definitions[identifier],
                "catalogue:source",
            )
            section_anchor = heading_anchor(sections_by_line[definitions[identifier]])
            require(row["document_ref"] == "requirements.md#" + section_anchor, "catalogue:document-anchor")


def validate_ledger(
    ledger: dict, requirement_lines: dict, baseline_lines: dict,
    fixtures: list, immutable_target: str,
) -> None:
    object_keys(ledger, {
        "schema_version", "schema_ref", "programme_issue", "foundation_issue", "baseline",
        "evidence_classes", "priority_order", "requirements", "source_crosswalk",
        "source_decisions", "analytics", "reports", "scenarios", "institutional_decisions",
        "service_objectives", "workload_profiles", "examples", "current_observations", "semantic_deviations",
    }, "ledger:shape")
    require(ledger["schema_version"] == "lotus-composite-documentation-ledger.v1", "ledger:version")
    require(ledger["schema_ref"] == "../../automation/validate_composite_documentation_foundation.py", "ledger:schema-ref")
    require(set(ledger["evidence_classes"]) == CLASSES, "ledger:evidence-classes")
    require(issue_ref(ledger["programme_issue"]) and issue_ref(ledger["foundation_issue"]), "ledger:issue")
    rows = unique_rows(ledger["requirements"], "requirement_id", set(requirement_lines), "requirements")
    crosswalk = unique_rows(ledger["source_crosswalk"], "source_id", set(baseline_lines), "crosswalk")
    for source_id, row in crosswalk.items():
        require(row["source_line"] == baseline_lines[source_id], "crosswalk:source-line")
        require(row["source_ref"] == "source/01_composite_requirements_source_baseline.txt", "crosswalk:source-ref")
        targets = row["target_ids"]
        require(isinstance(targets, list) and bool(targets) and len(set(targets)) == len(targets) and set(targets) <= set(rows), "crosswalk:exact-targets")
        require(row["mapping_status"] == "SPECIFICATION_MAPPING" and bool(row["rationale"]), "crosswalk:mapping")
    required_keys = {
        "requirement_id", "origin", "component", "contract_api", "method_policy",
        "implementation_state", "evidence", "migration_impact", "documentation", "risk",
        "owner", "next_action", "programme_issue", "related_issues", "test_plan",
    }
    for requirement_id, row in rows.items():
        object_keys(row, required_keys, "requirement:shape")
        origin = row["origin"]
        object_keys(origin, {"kind", "source_ref", "source_line", "source_sha256", "baseline_ids"}, "origin:shape")
        require(origin["kind"] in {"TARGET", "SOURCE_AND_TARGET"}, "origin:kind")
        require(origin["source_ref"] == "source/03_lotus_composite_implementation_requirements.txt", "origin:source")
        require(origin["source_line"] == requirement_lines[requirement_id] and origin["source_sha256"] == INPUT_HASHES["03_lotus_composite_implementation_requirements.md"], "origin:identity")
        expected_sources = {sid for sid, mapped in crosswalk.items() if requirement_id in mapped["target_ids"]}
        require(set(origin["baseline_ids"]) == expected_sources, "origin:crosswalk")
        component = row["component"]
        require(component["repository"] in REPOSITORIES and row["owner"] == component["repository"], "requirement:owner")
        require(component["scope"] == "PLANNED_REQUIREMENT_OWNERSHIP", "component:scope")
        require(all(value in REPOSITORIES for value in component["collaborators"]), "component:collaborators")
        require(row["implementation_state"] in STATES, "requirement:state")
        require(issue_ref(row["programme_issue"]) and all(issue_ref(ref) for ref in row["related_issues"]), "requirement:issue")
        require(all(isinstance(row[key], str) and row[key].strip() for key in ("migration_impact", "documentation", "risk", "next_action")), "requirement:fields")
        require(set(row["method_policy"]["decision_ids"]) <= {"DEC-" + str(n).zfill(2) for n in range(1, 17)}, "method:decision")
        evidence = row["evidence"]
        object_keys(evidence, {"unit", "integration", "e2e", "assessment"}, "evidence:shape")
        for key, evidence_class in (("unit", "UNIT_TEST"), ("integration", "INTEGRATION_TEST"), ("e2e", "TARGET_ENVIRONMENT_ACCEPTANCE")):
            require(isinstance(evidence[key], list), "evidence:array")
            for item in evidence[key]:
                validate_evidence(item, evidence_class)
        if evidence["assessment"] is not None:
            validate_evidence(evidence["assessment"], "OWNER_SOURCE_ASSESSMENT")
        state = row["implementation_state"]
        require(state == "NOT_ASSESSED" or evidence["assessment"] is not None, "state:assessment-required")
        if state in {"VERIFIED_IN_TEST", "VERIFIED_IN_TARGET_ENVIRONMENT"}:
            require(bool(evidence["unit"]) and bool(evidence["integration"]), "state:executable-evidence")
        if state == "VERIFIED_IN_TARGET_ENVIRONMENT":
            require(bool(evidence["e2e"]), "state:environment-evidence")
        if state == "BLOCKED_ON_APPROVED_POLICY_OR_SOURCE":
            require(bool(row.get("method_policy", {}).get("decision_ids")) or bool(evidence["assessment"].get("source_blocker")), "state:blocker")
        api = row["contract_api"]
        require(api["kind"] == "LOGICAL_REQUIREMENT" and api["current_api_ref"] is None, "api:logical-boundary")
        plan = row["test_plan"]
        require(plan["state"] == "PLANNED" and plan["actual_test_ref"] is None and plan["repository"] in REPOSITORIES, "test:planned-boundary")
    validate_catalogues(ledger, immutable_target)
    unique_rows(ledger["source_decisions"], "id", {"SD-" + str(n).zfill(2) for n in range(1, 19)}, "source-decisions")
    for row in ledger["source_decisions"] + ledger["institutional_decisions"]:
        require(row["state"] == "UNRESOLVED" and row["approval_ref"] is None, "decision:approval-boundary")
    profiles = unique_rows(ledger["workload_profiles"], "id", {"S", "M", "L", "D", "H"}, "profiles")
    require(all(row["state"] == "TARGET_NOT_BENCHMARKED" for row in profiles.values()), "profiles:claim")
    examples = unique_rows(ledger["examples"], "oracle_id", {fixture["id"] for fixture in fixtures}, "examples")
    for index, fixture in enumerate(fixtures):
        row = examples[fixture["id"]]
        require(row["fixture_ref"] == f"source/05_composite_numerical_oracles.json#/fixtures/{index}", "example:fixture")
        require(row["evidence_class"] == "SPECIFICATION_ORACLE" and row["state"] == "PLANNED" and row["executed"] is False, "example:proof-boundary")
        require(row["actual_test_ref"] is None and row["current_api_ref"] is None, "example:runtime-boundary")
        require(row["owning_repository"] in REPOSITORIES and issue_ref(row["owning_issue"]), "example:owner")
        require(set(row["requirement_ids"]) <= set(rows) and bool(row["requirement_ids"]), "example:requirement")
        require(row["scenario_ids"] == [f"AT-{ORACLE_SCENARIOS[index]:03}"], "example:scenario")
        require(row["planned_test_name"] == "composite_oracle_" + fixture["id"].lower().replace("-", "_"), "example:test-plan")
    observations = ledger["current_observations"]
    require(isinstance(observations, list), "observations:array")
    for row in observations:
        require(row["evidence_class"] == "COMMITTED_SOURCE_OBSERVATION" and row["repository"] in REPOSITORIES and committed_ref(row["commit"]) and relative_path(row["path"]) and bool(row["meaning"]), "observation:identity")
    require(ledger["semantic_deviations"] == [], "deviation:requires-approved-contract")


def human_projection(ledger: dict) -> str:
    rows = []
    for row in ledger["requirements"]:
        links = []
        for ref in row["related_issues"]:
            repository, _, issue = ref.split("/")[-3:]
            links.append(f"[{repository}#{issue}]({ref})")
        rows.append(f"| [{row['requirement_id']}]({row['documentation']}) | {row['owner']} | {row['implementation_state']} | {', '.join(links)} |")
    return "\n".join(rows)


def validate_worked_examples(text: str, fixtures: list) -> None:
    markers = re.findall(r"<!-- oracle:(OR-\d{2}) -->", text)
    require(len(markers) == len(set(markers)) and set(markers) == {f["id"] for f in fixtures}, "worked:inventory")
    for fixture in fixtures:
        pattern = r"<!-- oracle:" + fixture["id"] + r" -->\s*`{3}json\s*(.*?)\s*`{3}"
        match = re.search(pattern, text, flags=re.DOTALL)
        require(match is not None, "worked:block")
        actual = json.loads(match[1])
        expected = {"oracle_id": fixture["id"], "evidence_class": "SPECIFICATION_ORACLE", "state": "PLANNED", "inputs": fixture["inputs"], "expected": fixture["expected"]}
        require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True), "worked:literal-drift")


def heading_anchor(heading: str) -> str:
    heading = re.sub(r"[^\w\s-]", "", heading.lower())
    return re.sub(r"\s", "-", heading)


def validate_local_links(root: Path, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^\n)]+)\)", text):
        target = target.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme:
            require(parsed.scheme in {"https", "http"}, "link:scheme")
            continue
        destination = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path.resolve()
        if not destination.suffix and destination.parent.name == "wiki":
            destination = destination.with_suffix(".md")
        require(destination.is_relative_to(root.resolve()) and destination.is_file(), "link:missing-local-target")
        if parsed.fragment and destination.suffix == ".md":
            headings = re.findall(r"^#{1,6} (.*)$", destination.read_text(encoding="utf-8"), flags=re.MULTILINE)
            require(unquote(parsed.fragment) in {heading_anchor(h) for h in headings}, "link:missing-heading")


def validate_foundation(root: Path) -> None:
    docs = root / DOCS
    manifest = read_json(docs / "source-manifest.v1.json")
    requirements, baseline = validate_publication(root, manifest, (docs / "requirements.md").read_text(encoding="utf-8"))
    require(len(requirements) == 321 and len(baseline) == 48, "source:inventory-count")
    oracles = read_json(docs / "source/05_composite_numerical_oracles.json")
    require(oracles["return_unit"] == "DECIMAL_RETURN" and oracles["numeric_comparison_absolute_tolerance"] == "0.000000000001", "oracle:precision")
    fixtures = oracles["fixtures"]
    unique_rows(fixtures, "id", {"OR-" + str(n).zfill(2) for n in range(1, 19)}, "oracles")
    ledger = read_json(docs / "implementation-ledger.v1.json")
    immutable_target = (docs / "source/03_lotus_composite_implementation_requirements.txt").read_text(encoding="utf-8")
    validate_ledger(ledger, requirements, baseline, fixtures, immutable_target)
    validate_worked_examples((docs / "worked-examples.md").read_text(encoding="utf-8"), fixtures)
    readme = (docs / "README.md").read_text(encoding="utf-8")
    match = re.search(r"<!-- coverage:start -->\n.*?\n\| --- \| --- \| --- \| --- \|\n(.*?)\n<!-- coverage:end -->", readme, flags=re.DOTALL)
    require(match is not None and match[1] == human_projection(ledger), "coverage:human-drift")
    paths = list(docs.glob("*.md")) + [
        root / "rfcs/RFC-0110-composite-performance-product-and-delivery-foundation.md",
        root / "wiki/Composite-Performance.md",
    ]
    for path in paths:
        validate_local_links(root, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Platform repository root.")
    args = parser.parse_args()
    try:
        validate_foundation(args.root)
    except (FoundationError, OSError, ValueError, KeyError, TypeError) as error:
        print("FAIL composite documentation foundation: " + (str(error) if isinstance(error, FoundationError) else type(error).__name__))
        return 1
    print("PASS composite documentation foundation: 321 requirements; 48 source rows; full catalogues; 18 planned oracles. Document proof only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
