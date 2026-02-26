import os
import platform
import sys

from ..metadata import (
    APP_NAME,
    ENGINE_CAPABILITY_LINE,
    REPO_URL,
    TAGLINE,
    VERSION,
)
from .styles import BLUE, CYAN, GREEN, RED, RESET, YELLOW


def clear_terminal():
    if not sys.stdout.isatty():
        return
    os.system("cls" if platform.system() == "Windows" else "clear")


def _banner_line(text: str, width: int = 67) -> str:
    content = text[: width - 4]
    return f"| {content:<{width - 4}} |"


def show_banner():
    clear_terminal()
    border = "+" + "-" * 65 + "+"
    lines = [
        border,
        _banner_line(f"{APP_NAME} | {TAGLINE}"),
        _banner_line(ENGINE_CAPABILITY_LINE),
        border,
        _banner_line(f"Version: {VERSION}"),
        _banner_line(f"Repo: {REPO_URL}"),
        border,
    ]
    print(f"{BLUE}")
    for line in lines:
        print(f"{line}")
    print(f"{RESET}")


def print_error(message: str):
    print(f"{RED}[!] {message}{RESET}")


def print_success(message: str):
    print(f"{GREEN}[+] {message}{RESET}")


def print_warning(message: str):
    print(f"{YELLOW}[*] {message}{RESET}")


def print_info(message: str):
    print(f"{BLUE}[i] {message}{RESET}")


def prompt_text(label: str, optional: bool = False) -> str:
    suffix = " (optional)" if optional else ""
    return input(f"{CYAN}{label}{suffix}: {RESET}").strip()
