from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile

from automation.cost_attribution.application import build_service_cost_attribution
from automation.cost_attribution.domain import ServiceAllocationRequest
from automation.cost_attribution.infrastructure import JsonBillingExportAdapter


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate source-safe service cost attribution"
    )
    parser.add_argument("--billing-export", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--service-id", required=True)
    parser.add_argument(
        "--environment",
        choices=("test", "production-like", "production"),
        required=True,
    )
    parser.add_argument("--region", required=True)
    parser.add_argument("--source-commit-sha", required=True)
    parser.add_argument("--source-ref", required=True)
    parser.add_argument("--pipeline-run-id", required=True)
    parser.add_argument("--generated-at-utc", required=True)
    parser.add_argument("--resource-observation-schema-version", required=True)
    parser.add_argument("--resource-observation-sha256", required=True)
    parser.add_argument("--resource-observation-run-id", required=True)
    parser.add_argument("--shared-cost-numerator", required=True)
    parser.add_argument("--shared-cost-denominator", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.output.resolve() == args.billing_export.resolve():
        raise ValueError("output must not overwrite the authoritative billing export")
    artifact = build_service_cost_attribution(
        billing_export_port=JsonBillingExportAdapter(args.billing_export),
        request=ServiceAllocationRequest(
            repository=args.repository,
            service_id=args.service_id,
            environment=args.environment,
            region=args.region,
            source_commit_sha=args.source_commit_sha,
            source_ref=args.source_ref,
            pipeline_run_id=args.pipeline_run_id,
            resource_observation_schema_version=args.resource_observation_schema_version,
            resource_observation_sha256=args.resource_observation_sha256,
            resource_observation_run_id=args.resource_observation_run_id,
            shared_cost_numerator=Decimal(args.shared_cost_numerator),
            shared_cost_denominator=Decimal(args.shared_cost_denominator),
        ),
        generated_at_utc=datetime.fromisoformat(
            args.generated_at_utc.replace("Z", "+00:00")
        ),
    )
    _write_atomic(args.output, artifact)
    return 0


def _write_atomic(path: Path, artifact: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(artifact, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
