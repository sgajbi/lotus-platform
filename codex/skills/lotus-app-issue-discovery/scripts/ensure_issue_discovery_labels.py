from __future__ import annotations

import argparse
import subprocess
import sys


LABELS = [
    ("issue-discovery", "6f42c1", "Raised from governed Lotus issue-discovery review"),
    ("impact/correctness", "d73a4a", "Wrong business, calculation, lifecycle, or API behavior risk"),
    ("impact/security", "b60205", "Security, privacy, authorization, secrets, or abuse risk"),
    ("impact/operability", "fbca04", "Readiness, diagnostics, recovery, or supportability risk"),
    ("impact/performance", "0e8a16", "Latency, scalability, query, batching, or resource risk"),
    ("impact/architecture", "5319e7", "Boundary, dependency, modularity, contract, or ownership risk"),
    ("lens/architecture-boundaries", "1f6feb", "Lens: architecture boundaries and dependency direction"),
    ("lens/runtime-composition", "1f6feb", "Lens: process-local runtime wiring, dependency injection, startup/shutdown"),
    ("lens/api-design-governance", "1f6feb", "Lens: API design, routing, OpenAPI, pagination, filtering, sorting, errors"),
    ("lens/api-documentation-standards", "1f6feb", "Lens: API docs, standards, endpoint catalogs, duplicate endpoint posture"),
    ("lens/http-boundary-controls", "1f6feb", "Lens: HTTP boundary controls, CORS, trusted hosts, request limits, secure headers"),
    ("lens/application-layer", "1f6feb", "Lens: application services and use-case orchestration"),
    ("lens/domain-layer", "1f6feb", "Lens: domain models, policies, calculations, validation, state transitions"),
    ("lens/ports-adapters", "1f6feb", "Lens: ports, adapters, repositories, clients, publishers"),
    ("lens/infrastructure", "1f6feb", "Lens: infrastructure repositories, clients, config, adapters"),
    ("lens/configuration-secrets", "1f6feb", "Lens: configuration, secrets, environment profiles, safe defaults"),
    ("lens/downstream-integration", "1f6feb", "Lens: downstream clients, source contracts, timeouts, retries, error mapping"),
    ("lens/mapping-anti-corruption", "1f6feb", "Lens: DTO, event, row, and source anti-corruption mapping"),
    ("lens/unit-of-work-transactions", "1f6feb", "Lens: unit of work, commits, rollback, multi-write flows"),
    ("lens/event-outbox-contracts", "1f6feb", "Lens: events, outbox, schema versions, replay, DLQ, delivery idempotency"),
    ("lens/data-product-trust-telemetry", "1f6feb", "Lens: data mesh, product declarations, runtime trust telemetry"),
    ("lens/capability-publication", "1f6feb", "Lens: supported-feature, Gateway, Workbench, and capability publication truth"),
    ("lens/evidence-proof-contracts", "1f6feb", "Lens: proof artifacts, certification evidence, scorecards, and evidence contracts"),
    ("lens/source-contract-dependency-semantics", "1f6feb", "Lens: source contracts, dependency semantics, lifecycle identity"),
    ("lens/database-operations", "1f6feb", "Lens: database operations, indexes, query plans, locks, migrations, pooling"),
    ("lens/data-model-quality", "1f6feb", "Lens: data models, migrations, indexes, identifiers, temporal and lineage fields"),
    ("lens/transaction-lifecycle", "1f6feb", "Lens: transaction lifecycle, linked legs, reversals, corrections"),
    ("lens/position-lifecycle", "1f6feb", "Lens: position lifecycle, lots, availability, collateral, restatements"),
    ("lens/calculations-methodology", "1f6feb", "Lens: calculations, methodology, precision, FX, income, cashflows"),
    ("lens/domain-vocabulary", "1f6feb", "Lens: domain vocabulary in APIs, models, docs, metrics, tests"),
    ("lens/validation-idempotency", "1f6feb", "Lens: validation, duplicate handling, idempotency, conflict semantics"),
    ("lens/auditability-lineage", "1f6feb", "Lens: auditability, lineage, source identity, correlation, evidence"),
    ("lens/observability", "1f6feb", "Lens: monitoring, logs, metrics, tracing, health, readiness"),
    ("lens/security-privacy", "1f6feb", "Lens: authn, authz, CORS, headers, secrets, sensitive data"),
    ("lens/resilience", "1f6feb", "Lens: timeouts, retries, backoff, degradation, downstream errors"),
    ("lens/performance-scalability", "1f6feb", "Lens: indexes, query shape, batching, pagination, caching, pooling"),
    ("lens/testing-quality", "1f6feb", "Lens: unit, integration, contract, API, security, regression, E2E tests"),
    ("lens/ci-release-evidence", "1f6feb", "Lens: CI lanes, repo-native gates, release evidence, branch and PR hygiene"),
    ("lens/documentation-runbooks", "1f6feb", "Lens: README, wiki, architecture docs, API catalog, runbooks"),
    ("lens/operational-supportability", "1f6feb", "Lens: runbooks, dashboards, alerts, replay, recovery, support APIs"),
    ("lens/dead-code-duplication", "1f6feb", "Lens: dead code, duplicate logic, stale paths, and maintainability-impact cleanup"),
    ("lens/dependency-hygiene", "1f6feb", "Lens: dependencies, lockfiles, scanners, vulnerable packages, and supply-chain posture"),
    ("lens/repo-organization", "1f6feb", "Lens: repo layout, generated artifacts, hygiene, scripts"),
    ("lens/remote-repository-hygiene", "1f6feb", "Lens: GitHub repo metadata, stale remote branches, settings, and branch hygiene"),
    ("lens/agents-context-organization", "1f6feb", "Lens: AGENTS, repo context, skill routing, procedural memory"),
]


def run(command: list[str], dry_run: bool) -> None:
    if dry_run:
        print(" ".join(command))
        return
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create or update canonical Lotus issue-discovery labels in a GitHub repository."
    )
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form.")
    parser.add_argument("--dry-run", action="store_true", help="Print gh commands without executing them.")
    args = parser.parse_args()

    for name, color, description in LABELS:
        run(
            [
                "gh",
                "label",
                "create",
                name,
                "--repo",
                args.repo,
                "--color",
                color,
                "--description",
                description,
                "--force",
            ],
            args.dry_run,
        )

    print(f"Ensured {len(LABELS)} issue-discovery labels in {args.repo}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}: {' '.join(exc.cmd)}", file=sys.stderr)
        raise SystemExit(exc.returncode)
