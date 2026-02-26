import re

from .models import SubjectProfile
from .utils import normalize_text

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def sanitize_profile(profile: SubjectProfile) -> SubjectProfile:
    profile.name = normalize_text(profile.name, max_len=80) or "unknown-subject"
    profile.organization = normalize_text(profile.organization, max_len=80)
    profile.role = normalize_text(profile.role, max_len=80)
    profile.email_hint = normalize_text(profile.email_hint, max_len=120)
    profile.phone_hint = normalize_text(profile.phone_hint, max_len=32)
    profile.aliases = [item for item in profile.aliases if normalize_text(item, 64)]
    profile.keywords = [item for item in profile.keywords if normalize_text(item, 64)]
    profile.favorite_numbers = [item for item in profile.favorite_numbers if normalize_text(item, 24)]
    profile.risk_notes = [item for item in profile.risk_notes if normalize_text(item, 80)]
    return profile


def validate_profile(profile: SubjectProfile) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not profile.name:
        errors.append("subject name is required")

    if profile.email_hint and not EMAIL_RE.match(profile.email_hint):
        errors.append("email hint format is invalid")

    if profile.phone_hint:
        digits = "".join(ch for ch in profile.phone_hint if ch.isdigit())
        if not (7 <= len(digits) <= 15):
            errors.append("phone hint should contain 7-15 digits")

    if profile.birth_year is not None and not (1900 <= profile.birth_year <= 2100):
        errors.append("birth year must be between 1900 and 2100")

    if profile.last_rotation_days is not None:
        if profile.last_rotation_days < 0:
            errors.append("last rotation days cannot be negative")
        elif profile.last_rotation_days > 365:
            warnings.append("password rotation is older than 365 days")

    if len(profile.all_tokens()) < 3:
        warnings.append("very little profile context provided; weak-pattern detection may be limited")

    return errors, warnings
