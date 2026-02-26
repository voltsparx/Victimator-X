import json
from dataclasses import asdict
from pathlib import Path

from .metadata import APP_NAME, VERSION
from .models import PasswordAssessment, RunSummary
from .utils import sort_passwords


def output_paths(output_root: Path, subject_slug: str) -> dict[str, Path]:
    logs_dir = output_root / "logs"
    wordlists_dir = output_root / "wordlists" / subject_slug
    reports_dir = output_root / "reports" / subject_slug

    logs_dir.mkdir(parents=True, exist_ok=True)
    wordlists_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    return {
        "logs_dir": logs_dir,
        "wordlists_dir": wordlists_dir,
        "reports_dir": reports_dir,
    }


def write_wordlists(wordlists_dir: Path, categorized: dict[str, set[str]]) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    for category in ("weak", "medium", "strong", "full"):
        file_path = wordlists_dir / f"{category}.txt"
        values = categorized.get(category, set())
        file_path.write_text("\n".join(sort_passwords(values)), encoding="utf-8")
        paths[category] = file_path
    return paths


def write_run_summary(reports_dir: Path, summary: RunSummary) -> Path:
    summary_path = reports_dir / "summary.json"
    summary_path.write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")
    return summary_path


def write_password_audit(reports_dir: Path, assessments: list[PasswordAssessment]) -> Path:
    audit_path = reports_dir / "password-audit.json"
    serialized = [asdict(assessment) for assessment in assessments]
    audit_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
    return audit_path


def write_quick_report(
    reports_dir: Path,
    summary: RunSummary,
    suggestions: list[str],
    weak_examples: list[str],
    nano_ai_tips: list[str],
) -> Path:
    report_path = reports_dir / "report.txt"
    lines = [
        f"{APP_NAME} Defensive Audit Report",
        f"{'=' * (len(APP_NAME) + 24)}",
        f"Version: {VERSION}",
        f"Subject: {summary.subject_name}",
        f"Generated candidates: {summary.generated_candidates}",
        f"Weak: {summary.weak_count}",
        f"Medium: {summary.medium_count}",
        f"Strong: {summary.strong_count}",
        f"Engine: {summary.engine_mode} ({summary.workers} workers)",
        "",
        "Top weak examples:",
        *[f"- {item}" for item in weak_examples],
        "",
        "Suggested passphrases:",
        *[f"- {item}" for item in suggestions],
        "",
        "Nano AI Guidance:",
        *[f"- {item}" for item in nano_ai_tips],
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path
