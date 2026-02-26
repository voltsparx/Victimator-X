from datetime import datetime

from .models import SubjectProfile

LEET_MAP = {
    "a": ["4", "@"],
    "e": ["3"],
    "i": ["1", "!"],
    "o": ["0"],
    "s": ["5", "$"],
    "t": ["7"],
}
SPECIALS = ["!", "@", "#", "$", "%", "&", "*", "?"]


def _expand_token(token: str) -> set[str]:
    base = token.strip()
    if not base:
        return set()

    lowered = base.lower()
    variants = {base, lowered, lowered.capitalize(), lowered.upper()}
    for source, replacements in LEET_MAP.items():
        for replacement in replacements:
            variants.add(lowered.replace(source, replacement))
    return variants


def generate_candidate_blocklist(
    profile: SubjectProfile,
    min_length: int,
    max_length: int,
    max_candidates: int,
) -> list[str]:
    tokens = sorted(token for token in profile.all_tokens() if 0 < len(token) <= max_length * 2)
    expanded: set[str] = set()
    for token in tokens:
        expanded.update(_expand_token(token[: max_length * 2]))

    current_year = str(datetime.utcnow().year)
    years = {current_year, current_year[-2:]}
    if profile.birth_year:
        birth = str(profile.birth_year)
        years.update({birth, birth[-2:]})

    candidates: set[str] = set()

    def add_candidate(value: str):
        if len(candidates) >= max_candidates:
            return
        if min_length <= len(value) <= max_length:
            candidates.add(value)

    expanded_list = sorted(item for item in expanded if len(item) <= max_length + 4)
    for item in expanded_list:
        add_candidate(item)
        for year in years:
            add_candidate(f"{item}{year}")
            add_candidate(f"{year}{item}")
        for special in SPECIALS:
            add_candidate(f"{item}{special}")
            add_candidate(f"{special}{item}")
        if len(candidates) >= max_candidates:
            break

    # Pair combinations are capped to avoid runaway growth.
    pair_limit = min(220, max(60, max_candidates // 180))
    pair_sources = [item for item in expanded_list[:pair_limit] if len(item) < max_length]
    for left in pair_sources:
        for right in pair_sources:
            if left == right:
                continue
            add_candidate(f"{left}{right}")
            if len(candidates) >= max_candidates:
                break
        if len(candidates) >= max_candidates:
            break

    return sorted(candidates, key=lambda word: (len(word), word.lower(), word))
