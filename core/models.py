from dataclasses import dataclass, field


@dataclass
class SubjectProfile:
    name: str
    aliases: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    favorite_numbers: list[str] = field(default_factory=list)
    birth_year: int | None = None
    organization: str | None = None
    role: str | None = None
    email_hint: str | None = None
    phone_hint: str | None = None
    mfa_enabled: bool | None = None
    password_manager_used: bool | None = None
    last_rotation_days: int | None = None
    risk_notes: list[str] = field(default_factory=list)

    def all_tokens(self) -> set[str]:
        tokens: set[str] = set()
        seeds = [
            self.name,
            *self.aliases,
            *self.keywords,
            *self.favorite_numbers,
            self.organization or "",
            self.role or "",
            *self.risk_notes,
        ]
        for value in seeds:
            if not value:
                continue
            token = value.strip()
            if token:
                tokens.add(token)
        if self.birth_year:
            tokens.add(str(self.birth_year))
            tokens.add(str(self.birth_year)[-2:])
        if self.email_hint:
            hint = self.email_hint.strip().lower()
            if "@" in hint:
                local, domain = hint.split("@", 1)
                if local:
                    tokens.add(local)
                if domain:
                    parts = [part for part in domain.split(".") if part]
                    tokens.update(parts)
            else:
                tokens.add(hint)
        if self.phone_hint:
            digits = "".join(ch for ch in self.phone_hint if ch.isdigit())
            if len(digits) >= 4:
                tokens.add(digits[-4:])
        return tokens


@dataclass
class PasswordAssessment:
    password: str
    score: int
    entropy_bits: float
    classification: str
    reasons: list[str] = field(default_factory=list)
    policy_violations: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class RunSummary:
    subject_name: str
    subject_slug: str
    generated_candidates: int
    weak_count: int
    medium_count: int
    strong_count: int
    engine_mode: str
    workers: int
    policy_min_length: int
    audited_password_count: int = 0
    audited_weak_count: int = 0
