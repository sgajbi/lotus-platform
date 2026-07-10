from __future__ import annotations

import argparse
import re
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
PLATFORM_ROOT = Path(__file__).resolve().parents[4]


PROFILE_LENSES = {
    "source-domain": [
        "lens/data-model-quality",
        "lens/transaction-lifecycle",
        "lens/position-lifecycle",
        "lens/validation-idempotency",
        "lens/auditability-lineage",
        "lens/database-operations",
        "lens/api-design-governance",
        "lens/api-documentation-standards",
        "lens/entitlements-tenant-isolation",
        "lens/data-quality-reconciliation",
        "lens/environment-supply-chain-provenance",
    ],
    "analytics": [
        "lens/calculations-methodology",
        "lens/source-contract-dependency-semantics",
        "lens/api-design-governance",
        "lens/api-documentation-standards",
        "lens/observability",
        "lens/operational-supportability",
        "lens/testing-quality",
        "lens/performance-scalability",
        "lens/data-quality-reconciliation",
        "lens/environment-supply-chain-provenance",
    ],
    "workflow": [
        "lens/transaction-lifecycle",
        "lens/validation-idempotency",
        "lens/event-outbox-contracts",
        "lens/evidence-proof-contracts",
        "lens/operational-supportability",
        "lens/capability-publication",
        "lens/operator-control-plane",
        "lens/customer-impact-failure-modes",
        "lens/environment-supply-chain-provenance",
    ],
    "gateway": [
        "lens/api-design-governance",
        "lens/api-documentation-standards",
        "lens/downstream-integration",
        "lens/mapping-anti-corruption",
        "lens/entitlements-tenant-isolation",
        "lens/resilience",
        "lens/capability-publication",
        "lens/api-consumer-experience",
        "lens/environment-supply-chain-provenance",
    ],
    "workbench": [
        "lens/capability-publication",
        "lens/customer-impact-failure-modes",
        "lens/accessibility-inclusive-design",
        "lens/product-workflow-usability",
        "lens/mobile-responsive-device-readiness",
        "lens/observability",
        "lens/entitlements-tenant-isolation",
        "lens/environment-supply-chain-provenance",
    ],
    "ai": [
        "lens/ai-model-governance",
        "lens/ai-data-boundaries",
        "lens/ai-evaluation-quality",
        "lens/ai-explainability-audit",
        "lens/ai-safety-abuse-controls",
        "lens/ai-human-oversight",
        "lens/ai-cost-latency-reliability",
        "lens/ai-agent-tool-governance",
        "lens/entitlements-tenant-isolation",
        "lens/data-governance-privacy-lifecycle",
        "lens/environment-supply-chain-provenance",
    ],
    "platform": [
        "lens/ci-release-evidence",
        "lens/evidence-proof-contracts",
        "lens/repo-organization",
        "lens/agents-context-organization",
        "lens/documentation-runbooks",
        "lens/deployment-environment-parity",
        "lens/environment-supply-chain-provenance",
    ],
}


REPO_PROFILE_HINTS = {
    "lotus-core": "source-domain",
    "lotus-performance": "analytics",
    "lotus-risk": "analytics",
    "lotus-advise": "workflow",
    "lotus-manage": "workflow",
    "lotus-report": "workflow",
    "lotus-render": "workflow",
    "lotus-archive": "workflow",
    "lotus-idea": "workflow",
    "lotus-gateway": "gateway",
    "lotus-workbench": "workbench",
    "lotus-ai": "ai",
    "lotus-platform": "platform",
}


HIGH_SIGNAL_HARDENING_LENSES = [
    "lens/architecture-boundaries",
    "lens/runtime-composition",
    "lens/api-documentation-standards",
    "lens/http-boundary-controls",
    "lens/configuration-secrets",
    "lens/validation-idempotency",
    "lens/auditability-lineage",
    "lens/capability-publication",
    "lens/evidence-proof-contracts",
    "lens/observability",
    "lens/security-privacy",
    "lens/testing-quality",
    "lens/ci-release-evidence",
    "lens/dependency-hygiene",
    "lens/environment-supply-chain-provenance",
    "lens/ai-data-boundaries",
    "lens/ai-evaluation-quality",
    "lens/ai-safety-abuse-controls",
    "lens/ai-agent-tool-governance",
]


DEPLOYABLE_IMAGE_PROVENANCE_CHECKLIST = [
    "image tagged with the Git commit SHA",
    "OCI labels include commit, Git branch/ref, repository URL, version, build time, and CI pipeline/run ID",
    "release image built and pushed by CI only",
    "image digest captured in a release manifest or equivalent immutable evidence",
    "SBOM generated",
    "vulnerability scan passed or records an approved time-bounded exception",
    "image signed",
    "provenance attestation generated",
    "Kubernetes, Helm, or deployment manifests deploy by digest",
    "/version or version/build metadata endpoint exposes the same metadata",
    "same immutable image promoted across environments without rebuilding",
    "no build secrets leaked through Dockerfile ARG/ENV, image history, logs, labels, or runtime metadata",
]


def catalog_labels() -> list[tuple[str, str]]:
    text = (SKILL_ROOT / "references" / "review-lenses.md").read_text(encoding="utf-8")
    rows = re.findall(r"^\| ([^|]+) \| `(lens/[a-z0-9-]+)` \|$", text, flags=re.MULTILINE)
    return [(name.strip(), label.strip()) for name, label in rows]


def infer_profile(repository: str) -> str:
    repo_name = repository.rsplit("/", 1)[-1]
    return REPO_PROFILE_HINTS.get(repo_name, "source-domain")


def render_plan(repository: str, profile: str, limit: int | None) -> str:
    labels_by_label = {label: name for name, label in catalog_labels()}
    first_lenses = PROFILE_LENSES[profile]
    if limit:
        first_lenses = first_lenses[:limit]
    missing = [label for label in first_lenses if label not in labels_by_label]
    if missing:
        raise ValueError(f"Profile references unknown labels: {', '.join(missing)}")

    lines = [
        f"# Issue-Discovery Campaign Plan: {repository}",
        "",
        f"- Profile: `{profile}`",
        "- Source: `codex/skills/lotus-app-issue-discovery/references/review-lenses.md`",
        "",
        "## Startup Commands",
        "",
        "```powershell",
        "git status --short --branch",
        f"gh issue list --repo {repository} --state open --search \"\\\"Issue Discovery Ledger\\\"\" --json number,title,url",
        f"gh issue list --repo {repository} --state open --label issue-discovery --limit 100 --json number,title,labels,url",
        f"gh pr list --repo {repository} --state open --json number,title,headRefName,url",
        "python <lotus-platform>\\codex\\skills\\lotus-app-issue-discovery\\scripts\\validate_issue_discovery_skill.py",
        "```",
        "",
        "## First Lens Queue",
        "",
    ]
    for index, label in enumerate(first_lenses, start=1):
        lines.append(f"{index}. {labels_by_label[label]} - `{label}`")

    hardening = [label for label in first_lenses if label in HIGH_SIGNAL_HARDENING_LENSES]
    if hardening:
        lines.extend(["", "## CI Hardening Candidates", ""])
        for label in hardening:
            lines.append(f"- `{label}`: consider deterministic gate only after a concrete issue pattern is measured and low-noise.")

    if "lens/environment-supply-chain-provenance" in first_lenses:
        lines.extend(["", "## Deployable Image Provenance Checklist", ""])
        for index, item in enumerate(DEPLOYABLE_IMAGE_PROVENANCE_CHECKLIST, start=1):
            lines.append(f"{index}. {item}.")

    lines.extend(
        [
            "",
            "## Ledger Update Requirements",
            "",
            "- Status: `Covered For Now`, `Issues Raised`, `Blocked By Active Fix`, `Needs Recheck`, or `Not Applicable`.",
            "- Proof flags: `Code`, `Docs`, `Dup`, `Labels`, `Ledger`.",
            "- Include inspected paths, standards consulted, duplicate searches, issues, blockers, residual risk, recommendation, and next lens.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Lotus issue-discovery campaign plan from the canonical lens catalog.")
    parser.add_argument("--repository", required=True, help="GitHub repository in owner/name form.")
    parser.add_argument("--profile", choices=sorted(PROFILE_LENSES), help="Review profile. Defaults from repository name.")
    parser.add_argument("--limit", type=int, help="Limit the first lens queue.")
    parser.add_argument("--output", type=Path, help="Output markdown path. Defaults under output/.")
    args = parser.parse_args()

    profile = args.profile or infer_profile(args.repository)
    output = args.output or (
        PLATFORM_ROOT / "output" / f"{args.repository.rsplit('/', 1)[-1]}-issue-discovery-plan.md"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_plan(args.repository, profile, args.limit), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
