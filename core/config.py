import os
from pathlib import Path

DEFAULT_MIN_LENGTH = 4
DEFAULT_MAX_LENGTH = 20
DEFAULT_POLICY_MIN_LENGTH = 12
DEFAULT_MAX_CANDIDATES = 50000
DEFAULT_ENGINE = "auto"
DEFAULT_WORKERS = max(2, os.cpu_count() or 2)
DEFAULT_OUTPUT_ROOT = Path("output")

COMMON_WEAK_PASSWORDS = {
    "123456",
    "12345678",
    "123456789",
    "1234567890",
    "password",
    "qwerty",
    "abc123",
    "111111",
    "123123",
    "iloveyou",
    "admin",
    "welcome",
    "monkey",
    "dragon",
    "football",
    "letmein",
    "master",
    "sunshine",
    "ashley",
    "bailey",
    "shadow",
    "password1",
    "passw0rd",
    "qwerty123",
    "trustno1",
    "freedom",
    "whatever",
    "654321",
    "superman",
    "hello123",
}
