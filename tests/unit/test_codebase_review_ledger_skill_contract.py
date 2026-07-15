from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "codex/skills/lotus-codebase-review-ledger/SKILL.md"
TEMPLATE = ROOT / "codex/skills/lotus-codebase-review-ledger/references/review-entry-template.md"


def test_cross_repository_source_evidence_guardrails_are_durable() -> None:
    skill = SKILL.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")

    for required_rule in (
        "exact closed field set",
        "repository/ref/SHA-256",
        "canonical ordered record",
        "omission, substitution, and reordering fail closed",
        "full_cross_repository",
        "consumer_only",
        "must never validate as full producer-and-consumer proof",
        "must not assert runtime execution",
        "supported-feature promotion",
    ):
        assert required_rule in skill

    for review_prompt in (
        "exact repository/ref/SHA-256 records",
        "canonical ordered collection digest",
        "consumer-only validation",
        "evidence class",
    ):
        assert review_prompt in template
