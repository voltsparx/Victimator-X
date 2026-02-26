import argparse
import signal
import sys
from functools import partial
from pathlib import Path

from .audit import (
    evaluate_password_worker,
    generate_passphrase_suggestions,
    normalize_subject_tokens,
)
from .config import (
    DEFAULT_ENGINE,
    DEFAULT_MAX_CANDIDATES,
    DEFAULT_MAX_LENGTH,
    DEFAULT_MIN_LENGTH,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_POLICY_MIN_LENGTH,
    DEFAULT_WORKERS,
)
from .engine import EngineCoordinator
from .generator import generate_candidate_blocklist
from .healthcheck import run_self_check
from .logging_setup import setup_logger
from .metadata import APP_NAME, ETHICAL_NOTICE, VERSION
from .models import RunSummary, SubjectProfile
from .nano_ai import answer_nano_ai_question, build_nano_ai_guidance
from .reporting import (
    output_paths,
    write_password_audit,
    write_quick_report,
    write_run_summary,
    write_wordlists,
)
from .ui import (
    print_error,
    print_info,
    print_success,
    print_warning,
    prompt_text,
    show_banner,
)
from .utils import load_passwords_from_file, parse_csv, parse_tristate, slugify
from .validation import sanitize_profile, validate_profile


def handle_quit(signum=None, frame=None):
    print_error("Interrupted by user. Exiting safely.")
    raise SystemExit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            f"{APP_NAME} defensive password auditing tool. "
            "Use only on accounts/systems you own or are authorized to assess."
        )
    )
    parser.add_argument("--subject-name", help="Audit subject name.")
    parser.add_argument(
        "--aliases",
        help="Comma-separated alternate names/usernames for weak-pattern analysis.",
    )
    parser.add_argument(
        "--keywords",
        help="Comma-separated personal keywords for weak-pattern analysis.",
    )
    parser.add_argument(
        "--favorite-numbers",
        help="Comma-separated numbers commonly reused in weak passwords.",
    )
    parser.add_argument(
        "--birth-year",
        type=int,
        help="Optional birth year for defensive weak-pattern checks.",
    )
    parser.add_argument("--organization", help="Organization or team context.")
    parser.add_argument("--role", help="Role or account type context.")
    parser.add_argument("--email-hint", help="Known email hint (for weak-pattern detection only).")
    parser.add_argument("--phone-hint", help="Known phone hint (for weak-pattern detection only).")
    parser.add_argument(
        "--mfa-enabled",
        choices=("yes", "no", "unknown"),
        default="unknown",
        help="Whether MFA is enabled for the subject/account.",
    )
    parser.add_argument(
        "--password-manager",
        choices=("yes", "no", "unknown"),
        default="unknown",
        help="Whether a password manager is used.",
    )
    parser.add_argument(
        "--last-rotation-days",
        type=int,
        help="Days since last password rotation (if known).",
    )
    parser.add_argument(
        "--risk-notes",
        help="Comma-separated risk notes (e.g., reuse, phishing incident, shared device).",
    )
    parser.add_argument(
        "--password-file",
        type=Path,
        help="Optional file with passwords to audit (one password per line).",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "async", "threading", "parallel"),
        default=DEFAULT_ENGINE,
        help="Execution engine mode for assessments.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_WORKERS,
        help="Worker count for async/threading/parallel engines.",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=DEFAULT_MIN_LENGTH,
        help="Minimum generated weak-pattern length.",
    )
    parser.add_argument(
        "--max-length",
        type=int,
        default=DEFAULT_MAX_LENGTH,
        help="Maximum generated weak-pattern length.",
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help="Maximum generated weak-pattern candidates.",
    )
    parser.add_argument(
        "--policy-min-length",
        type=int,
        default=DEFAULT_POLICY_MIN_LENGTH,
        help="Minimum required length for policy checks.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Root output directory (logs, wordlists, reports).",
    )
    parser.add_argument("--yes", action="store_true", help="Skip ethical confirmation prompt.")
    parser.add_argument("--no-banner", action="store_true", help="Do not print banner.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("--self-check", action="store_true", help="Run engine/output connectivity checks and exit.")
    parser.add_argument("--ask-ai", help="Ask the nano-ai helper a short question.")
    parser.add_argument("--no-nano-ai", action="store_true", help="Disable nano-ai guidance in output.")
    return parser


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace):
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.min_length < 1:
        parser.error("--min-length must be at least 1")
    if args.max_length < args.min_length:
        parser.error("--max-length must be greater than or equal to --min-length")
    if args.max_candidates < 1:
        parser.error("--max-candidates must be at least 1")
    if args.policy_min_length < 6:
        parser.error("--policy-min-length must be at least 6")
    if args.birth_year and (args.birth_year < 1900 or args.birth_year > 2100):
        parser.error("--birth-year must be in a realistic range (1900-2100)")
    if args.last_rotation_days is not None and args.last_rotation_days < 0:
        parser.error("--last-rotation-days cannot be negative")
    if args.password_file and not args.password_file.exists():
        parser.error(f"--password-file does not exist: {args.password_file}")


def collect_profile(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    wizard_mode: bool,
) -> SubjectProfile:
    interactive = sys.stdin.isatty()

    if not args.subject_name:
        if not interactive:
            parser.error("--subject-name is required in non-interactive mode")
        args.subject_name = prompt_text("Subject name")

    if wizard_mode and interactive and not args.aliases:
        args.aliases = prompt_text("Aliases/usernames (comma-separated)", optional=True)
    if wizard_mode and interactive and not args.keywords:
        args.keywords = prompt_text("Keywords/hobbies (comma-separated)", optional=True)
    if wizard_mode and interactive and not args.favorite_numbers:
        args.favorite_numbers = prompt_text("Favorite numbers (comma-separated)", optional=True)
    if wizard_mode and interactive and args.birth_year is None:
        value = prompt_text("Birth year", optional=True)
        if value:
            try:
                args.birth_year = int(value)
            except ValueError:
                parser.error("Birth year must be numeric")
    if wizard_mode and interactive and not args.organization:
        args.organization = prompt_text("Organization/team", optional=True)
    if wizard_mode and interactive and not args.role:
        args.role = prompt_text("Role/account type", optional=True)
    if wizard_mode and interactive and not args.email_hint:
        args.email_hint = prompt_text("Email hint", optional=True)
    if wizard_mode and interactive and not args.phone_hint:
        args.phone_hint = prompt_text("Phone hint", optional=True)
    if wizard_mode and interactive and args.mfa_enabled == "unknown":
        args.mfa_enabled = prompt_text("MFA enabled? (yes/no/unknown)", optional=True) or "unknown"
    if wizard_mode and interactive and args.password_manager == "unknown":
        args.password_manager = (
            prompt_text("Password manager used? (yes/no/unknown)", optional=True) or "unknown"
        )
    if wizard_mode and interactive and args.last_rotation_days is None:
        value = prompt_text("Days since last password rotation", optional=True)
        if value:
            try:
                args.last_rotation_days = int(value)
            except ValueError:
                parser.error("Last rotation days must be numeric")
    if wizard_mode and interactive and not args.risk_notes:
        args.risk_notes = prompt_text("Risk notes (comma-separated)", optional=True)

    mfa_enabled = parse_tristate(args.mfa_enabled)
    password_manager_used = parse_tristate(args.password_manager)

    profile = SubjectProfile(
        name=args.subject_name,
        aliases=parse_csv(args.aliases),
        keywords=parse_csv(args.keywords),
        favorite_numbers=parse_csv(args.favorite_numbers),
        birth_year=args.birth_year,
        organization=args.organization,
        role=args.role,
        email_hint=args.email_hint,
        phone_hint=args.phone_hint,
        mfa_enabled=mfa_enabled,
        password_manager_used=password_manager_used,
        last_rotation_days=args.last_rotation_days,
        risk_notes=parse_csv(args.risk_notes),
    )
    return sanitize_profile(profile)


def confirm_ethical_use(args: argparse.Namespace) -> bool:
    print_error(f"{ETHICAL_NOTICE} ({APP_NAME} v{VERSION})")

    if args.yes:
        return True
    if not sys.stdin.isatty():
        print_error("Non-interactive mode requires --yes for explicit acknowledgment.")
        return False

    response = input("Type 'I AGREE' to continue: ").strip()
    if response != "I AGREE":
        print_error("Confirmation mismatch. Exiting.")
        return False
    return True


def build_categorized_wordlists(passwords: list[str], assessments: list) -> dict[str, set[str]]:
    categorized = {
        "weak": set(),
        "medium": set(),
        "strong": set(),
        "full": set(passwords),
    }
    for assessment in assessments:
        categorized[assessment.classification].add(assessment.password)
    return categorized


def main(argv: list[str] | None = None) -> int:
    signal.signal(signal.SIGINT, handle_quit)
    parser = build_parser()
    args = parser.parse_args(argv)
    validate_args(parser, args)

    if not args.no_banner:
        show_banner()

    if args.ask_ai:
        print_info(f"Nano AI: {answer_nano_ai_question(args.ask_ai)}")

    if args.self_check:
        ok, messages = run_self_check(args.output_root, args.workers)
        for message in messages:
            if "FAIL" in message:
                print_error(message)
            else:
                print_success(message)
        return 0 if ok else 1

    if not confirm_ethical_use(args):
        return 1

    wizard_mode = not any(
        [
            args.subject_name,
            args.aliases,
            args.keywords,
            args.favorite_numbers,
            args.birth_year,
            args.organization,
            args.role,
            args.email_hint,
            args.phone_hint,
            args.risk_notes,
            args.password_file,
        ]
    )
    profile = collect_profile(args, parser, wizard_mode=wizard_mode)
    errors, warnings = validate_profile(profile)
    if errors:
        for issue in errors:
            print_error(f"Profile validation: {issue}")
        return 1
    for note in warnings:
        print_warning(f"Profile validation: {note}")

    subject_slug = slugify(profile.name)

    paths = output_paths(args.output_root, subject_slug)
    logger = setup_logger(paths["logs_dir"] / "victimator-x.log", verbose=args.verbose)
    logger.info("Starting run for subject=%s engine=%s", profile.name, args.engine)

    candidates = generate_candidate_blocklist(
        profile=profile,
        min_length=args.min_length,
        max_length=args.max_length,
        max_candidates=args.max_candidates,
    )
    logger.info("Generated %d candidate patterns", len(candidates))

    engine = EngineCoordinator(mode=args.engine, workers=args.workers, logger=logger)
    normalized_tokens = normalize_subject_tokens(tuple(profile.all_tokens()))
    worker = partial(
        evaluate_password_worker,
        subject_tokens=normalized_tokens,
        policy_min_length=args.policy_min_length,
    )
    candidate_assessments = engine.map(worker, candidates)

    categorized = build_categorized_wordlists(candidates, candidate_assessments)
    wordlist_paths = write_wordlists(paths["wordlists_dir"], categorized)

    audited_assessments = []
    if args.password_file:
        passwords_from_file = load_passwords_from_file(args.password_file)
        logger.info("Auditing %d explicit passwords from %s", len(passwords_from_file), args.password_file)
        audited_assessments = engine.map(worker, passwords_from_file)
        write_password_audit(paths["reports_dir"], audited_assessments)

    weak_examples = [item for item in sorted(categorized["weak"])[:10]]
    suggestions = generate_passphrase_suggestions(count=5)

    summary = RunSummary(
        subject_name=profile.name,
        subject_slug=subject_slug,
        generated_candidates=len(candidates),
        weak_count=len(categorized["weak"]),
        medium_count=len(categorized["medium"]),
        strong_count=len(categorized["strong"]),
        engine_mode=engine.last_mode,
        workers=args.workers,
        policy_min_length=args.policy_min_length,
        audited_password_count=len(audited_assessments),
        audited_weak_count=len([item for item in audited_assessments if item.classification == "weak"]),
    )
    nano_ai_tips: list[str] = []
    if not args.no_nano_ai:
        nano_ai_tips = build_nano_ai_guidance(
            profile=profile,
            summary=summary,
            audited_assessments=audited_assessments,
        )

    summary_path = write_run_summary(paths["reports_dir"], summary)
    report_path = write_quick_report(
        paths["reports_dir"],
        summary,
        suggestions,
        weak_examples,
        nano_ai_tips,
    )

    print_success(f"App: {APP_NAME} v{VERSION}")
    print_success(f"Subject: {profile.name} ({subject_slug})")
    print_success(f"Generated candidates: {len(candidates)}")
    print_success(
        f"Classified => weak:{len(categorized['weak'])} "
        f"medium:{len(categorized['medium'])} strong:{len(categorized['strong'])}"
    )
    print_success(f"Engine used: {engine.last_mode} with {args.workers} worker(s)")
    print_success(f"Wordlists saved at: {wordlist_paths['full'].parent}")
    print_success(f"Summary saved: {summary_path}")
    print_success(f"Report saved: {report_path}")
    if nano_ai_tips:
        print_info("Nano AI top guidance:")
        for tip in nano_ai_tips[:3]:
            print_info(f"- {tip}")

    logger.info("Run completed. weak=%d medium=%d strong=%d", summary.weak_count, summary.medium_count, summary.strong_count)
    return 0
