import secrets
from dataclasses import asdict

from .config import COMMON_WEAK_PASSWORDS, DEFAULT_POLICY_MIN_LENGTH
from .models import PasswordAssessment
from .policy import (
    estimate_entropy_bits,
    has_repeated_chars,
    has_sequence,
    policy_violations,
)

PASS_PHRASE_WORDS = [
    "anchor",
    "planet",
    "forest",
    "silver",
    "candle",
    "rocket",
    "harbor",
    "falcon",
    "maple",
    "sunset",
    "river",
    "galaxy",
]


def normalize_subject_tokens(subject_tokens: tuple[str, ...] | set[str] | list[str]) -> tuple[str, ...]:
    normalized = {token.strip().lower() for token in subject_tokens if token and len(token.strip()) >= 3}
    return tuple(sorted(normalized))


def evaluate_password(
    password: str,
    subject_tokens: tuple[str, ...] = (),
    policy_min_length: int = DEFAULT_POLICY_MIN_LENGTH,
) -> PasswordAssessment:
    lowered = password.lower()
    reasons: list[str] = []
    suggestions: list[str] = []
    penalties = 0

    if lowered in COMMON_WEAK_PASSWORDS:
        reasons.append("Found in common weak-password list")
        penalties += 35

    for token in subject_tokens:
        if token in lowered:
            reasons.append("Contains personal/profile information")
            penalties += 25
            break

    if has_sequence(password):
        reasons.append("Contains predictable character sequence")
        penalties += 12
    if has_repeated_chars(password):
        reasons.append("Contains repeated character runs")
        penalties += 10

    entropy = estimate_entropy_bits(password)
    unique_classes = sum(
        [
            any(ch.islower() for ch in password),
            any(ch.isupper() for ch in password),
            any(ch.isdigit() for ch in password),
            any(not ch.isalnum() for ch in password),
        ]
    )

    violations = policy_violations(password, policy_min_length)
    penalties += len(violations) * 4

    score = min(len(password) * 4, 40)
    score += unique_classes * 8
    score += min(int(entropy // 4), 24)
    score -= penalties
    score = max(0, min(100, score))

    classification = "strong"
    if score < 45 or any("common weak-password" in reason for reason in reasons):
        classification = "weak"
    elif score < 75:
        classification = "medium"

    if "missing-symbol" in violations:
        suggestions.append("Add symbols to increase complexity")
    if "missing-digit" in violations:
        suggestions.append("Include at least one number")
    if len(password) < policy_min_length:
        suggestions.append(f"Increase length to at least {policy_min_length} characters")
    if any("personal/profile" in reason for reason in reasons):
        suggestions.append("Avoid names, birthdays, and obvious personal words")
    if not suggestions and classification == "strong":
        suggestions.append("Looks strong; rotate it regularly and keep it unique")

    return PasswordAssessment(
        password=password,
        score=score,
        entropy_bits=round(entropy, 2),
        classification=classification,
        reasons=reasons,
        policy_violations=violations,
        suggestions=suggestions,
    )


def evaluate_password_worker(item: str, subject_tokens: tuple[str, ...], policy_min_length: int):
    return evaluate_password(
        password=item,
        subject_tokens=subject_tokens,
        policy_min_length=policy_min_length,
    )


def generate_passphrase_suggestions(count: int = 5) -> list[str]:
    suggestions: list[str] = []
    symbols = ["-", "_", ".", "!", "@", "#"]
    for _ in range(count):
        first = secrets.choice(PASS_PHRASE_WORDS).capitalize()
        second = secrets.choice(PASS_PHRASE_WORDS).capitalize()
        joiner = secrets.choice(symbols)
        number = str(secrets.randbelow(900) + 100)
        suggestions.append(f"{first}{joiner}{second}{joiner}{number}")
    return suggestions


def assessments_to_dict(items: list[PasswordAssessment]) -> list[dict]:
    return [asdict(item) for item in items]
