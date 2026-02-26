from .models import PasswordAssessment, RunSummary, SubjectProfile


def _ratio(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return numerator / denominator


def build_nano_ai_guidance(
    profile: SubjectProfile,
    summary: RunSummary,
    audited_assessments: list[PasswordAssessment],
) -> list[str]:
    tips: list[str] = []

    weak_ratio = _ratio(summary.weak_count, summary.generated_candidates)
    if weak_ratio >= 0.45:
        tips.append("High weak-pattern exposure detected. Prioritize policy hardening and awareness training.")
    elif weak_ratio >= 0.25:
        tips.append("Moderate weak-pattern exposure detected. Tighten password standards and monitor reuse.")
    else:
        tips.append("Weak-pattern exposure is relatively low. Keep regular hygiene checks in place.")

    if profile.mfa_enabled is False:
        tips.append("MFA is disabled. Enable MFA for all critical accounts immediately.")
    elif profile.mfa_enabled is None:
        tips.append("MFA status unknown. Verify MFA coverage and document gaps.")

    if profile.password_manager_used is False:
        tips.append("Password manager is not in use. Adopt one to reduce reuse and weak-password risk.")
    elif profile.password_manager_used is None:
        tips.append("Password manager usage unknown. Confirm whether users store credentials safely.")

    if profile.last_rotation_days is not None and profile.last_rotation_days > 180:
        tips.append("Password rotation appears stale (>180 days). Rotate high-risk credentials.")

    audited_weak = [item for item in audited_assessments if item.classification == "weak"]
    if audited_weak:
        tips.append(
            f"Audited password list contains {len(audited_weak)} weak passwords. "
            "Force reset and blocklist these patterns."
        )

    if not profile.organization:
        tips.append("Organization context missing. Add it for clearer reporting and ownership.")
    if not profile.risk_notes:
        tips.append("No risk notes supplied. Capture recent incidents or known user behavior patterns.")

    return tips[:8]


def answer_nano_ai_question(question: str) -> str:
    q = question.strip().lower()
    if not q:
        return "Ask about policy, MFA, weak patterns, or remediation."
    if "mfa" in q:
        return "Enable MFA everywhere possible, starting with privileged and externally accessible accounts."
    if "weak" in q or "score" in q:
        return "Focus on passwords flagged weak due to common-list matches, personal tokens, and policy violations."
    if "policy" in q:
        return "Baseline policy: >=12 chars, mixed case, numbers, symbols, and ban known weak/common passwords."
    if "rotation" in q:
        return "Use risk-based rotation: immediate for compromised creds, periodic for privileged accounts."
    if "manager" in q:
        return "Password managers reduce reuse and improve uniqueness across services."
    return "Prioritize MFA, stronger policy thresholds, and continuous password hygiene audits."
