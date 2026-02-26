import re
from pathlib import Path


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text or "unknown-subject"


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    values = [part.strip() for part in value.split(",") if part.strip()]
    deduped: list[str] = []
    seen: set[str] = set()
    for item in values:
        key = item.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def parse_tristate(value: str | None) -> bool | None:
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"yes", "true", "1", "y"}:
        return True
    if lowered in {"no", "false", "0", "n"}:
        return False
    return None


def normalize_text(value: str | None, max_len: int = 64) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    if not cleaned:
        return None
    return cleaned[:max_len]


def sort_passwords(values: set[str] | list[str]) -> list[str]:
    return sorted(values, key=lambda word: (len(word), word.lower(), word))


def load_passwords_from_file(file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"Password file not found: {file_path}")
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return [line.strip() for line in lines if line.strip()]
