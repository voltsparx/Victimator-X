import math


def estimate_entropy_bits(password: str) -> float:
    pool_size = 0
    if any(ch.islower() for ch in password):
        pool_size += 26
    if any(ch.isupper() for ch in password):
        pool_size += 26
    if any(ch.isdigit() for ch in password):
        pool_size += 10
    if any(not ch.isalnum() for ch in password):
        pool_size += 33

    if pool_size == 0 or not password:
        return 0.0
    return len(password) * math.log2(pool_size)


def has_sequence(password: str, min_sequence: int = 4) -> bool:
    lowered = password.lower()
    if len(lowered) < min_sequence:
        return False
    for index in range(len(lowered) - min_sequence + 1):
        segment = lowered[index : index + min_sequence]
        asc = all(ord(segment[i + 1]) - ord(segment[i]) == 1 for i in range(len(segment) - 1))
        desc = all(ord(segment[i]) - ord(segment[i + 1]) == 1 for i in range(len(segment) - 1))
        if asc or desc:
            return True
    return False


def has_repeated_chars(password: str, threshold: int = 3) -> bool:
    if not password:
        return False
    run = 1
    for index in range(1, len(password)):
        if password[index] == password[index - 1]:
            run += 1
            if run >= threshold:
                return True
        else:
            run = 1
    return False


def policy_violations(password: str, min_length: int) -> list[str]:
    violations: list[str] = []
    if len(password) < min_length:
        violations.append(f"length<{min_length}")
    if not any(ch.islower() for ch in password):
        violations.append("missing-lowercase")
    if not any(ch.isupper() for ch in password):
        violations.append("missing-uppercase")
    if not any(ch.isdigit() for ch in password):
        violations.append("missing-digit")
    if not any(not ch.isalnum() for ch in password):
        violations.append("missing-symbol")
    return violations
