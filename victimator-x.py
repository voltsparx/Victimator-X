#!/usr/bin/env python3
import itertools
import platform
import os
import signal
from pathlib import Path
import argparse

# --- Global Config ---
ORANGE = "\033[38;5;208m"
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BLUE = "\033[94m"
RESET = "\033[0m"
REPO_URL = "https://github.com/voltsparx/Victimator-X"
VERSION = "1.4.0"

# --- Graceful Exit Handler ---
def handle_quit(signum=None, frame=None):
    print(f"\n{RED}[!] User requested exit. Terminating safely...{RESET}")
    exit(0)

signal.signal(signal.SIGINT, handle_quit)

# --- Terminal Utilities ---
def clear_terminal():
    os.system("cls" if platform.system() == "Windows" else "clear")

# --- Banner ---
def show_banner():
    clear_terminal()
    print(f"{ORANGE}  ╔═══════════════════════════════════════════════════════════════════╗  ")
    print(f"{ORANGE}  ║   __     ___      _   _                 _                __  __   ║  ")
    print(f"{ORANGE}  ║   \\ \\   / (_) ___| |_(_)_ __ ___   __ _| |_ ___  _ __    \\ \\/ /   ║  ")
    print(f"{ORANGE}  ║    \\ \\ / /| |/ __| __| | '_ ` _ \\ / _` | __/ _ \\| '__|____\\  /    ║  ")
    print(f"{ORANGE}  ║     \\ V / | | (__| |_| | | | | | | (_| | || (_) | | |_____/  \\    ║  ")
    print(f"{ORANGE}  ║      \\_/  |_|\\___|\\__|_|_| |_| |_|\\__,_|\\__\\___/|_|      /_/\\_\\   ║  ")
    print(f"{ORANGE}  ║                                                                   ║  ")
    print(f"{ORANGE}  ╚═══════════════════════════════════════════════════════════════════╝  ")
    print(f"{BLUE}     ➤ Author: {ORANGE}voltsparx")
    print(f"{BLUE}     ➤ Repo: {ORANGE}{REPO_URL}")
    print(f"{BLUE}     ➤ Version: {ORANGE}{VERSION}")
    print(f"{BLUE}     ➤ License: {ORANGE}MIT")
    print(f"{BLUE}     ➤ Contact: {ORANGE}voltsparx@gmail.com{RESET}\n")

# --- Input Handler ---
def get_input(prompt, is_multi=False):
    while True:
        try:
            value = input(prompt).strip()
            if value.lower() in ('exit', 'quit', 'stop'):
                handle_quit()
            if not value:
                return None
            if is_multi:
                return [v.strip() for v in value.split(",") if v.strip()]
            return value
        except KeyboardInterrupt:
            handle_quit()

# --- Leet & Variations ---
LEET_DICT = {
    'a': ['4', '@'], 'e': ['3'], 'i': ['1', '!'],
    'o': ['0'], 's': ['5', '$'], 't': ['7']
}

def apply_leet(word):
    variations = {word, word.lower(), word.capitalize()}
    for char, repls in LEET_DICT.items():
        for r in repls:
            variations.add(word.lower().replace(char, r))
    return variations

def add_special_chars(word):
    specials = ['!', '@', '#', '$', '%', '&', '*', '?']
    return {f"{word}{c}" for c in specials} | {f"{c}{word}" for c in specials}

# --- Strength Analyzer ---
def password_strength(pw):
    score = 0
    if len(pw) >= 8: score += 1
    if len(pw) >= 12: score += 1
    if any(c.isdigit() for c in pw): score += 1
    if any(c.isupper() for c in pw): score += 1
    if any(c in "!@#$%^&*?" for c in pw): score += 1
    return score

def classify_password(pw):
    score = password_strength(pw)
    if score <= 2: return "weak"
    elif score <= 4: return "medium"
    else: return "strong"

# --- CLI Arguments ---
parser = argparse.ArgumentParser(description="Victimator-X Advanced Wordlist Generator")
parser.add_argument("--hashcat", action="store_true", help="Optimize for Hashcat")
parser.add_argument("--hydra", action="store_true", help="Optimize for Hydra")
parser.add_argument("--min", type=int, default=4, help="Minimum password length")
parser.add_argument("--max", type=int, default=20, help="Maximum password length")
args = parser.parse_args()

# --- Main ---
if __name__ == "__main__":
    print(f"\n{RED}[!] WARNING: For authorized security testing only.")
    print(f"[!] Misuse is illegal. You are responsible for your actions.{RESET}")
    input("\nPress Enter to continue (or CTRL+C to exit)...")

    show_banner()

    data = {
        "first_name": get_input(f"{CYAN}First name: {RESET}"),
        "last_name": get_input(f"{CYAN}Last name: {RESET}"),
        "nickname": get_input(f"{CYAN}Nickname: {RESET}"),
        "birthdate": get_input(f"{CYAN}Birthdate (DDMMYYYY): {RESET}"),
        "favorite_numbers": get_input(f"{CYAN}Favorite numbers: {RESET}", True),
        "hobbies": get_input(f"{CYAN}Hobbies: {RESET}", True),
        "pet_name": get_input(f"{CYAN}Pet name: {RESET}"),
        "partner_name": get_input(f"{CYAN}Partner name: {RESET}"),
        "school": get_input(f"{CYAN}School/College: {RESET}")
    }

    base_words = set()
    for v in data.values():
        if isinstance(v, list):
            for item in v:
                base_words |= apply_leet(item)
        elif v:
            base_words |= apply_leet(v)

    wordlist = set(base_words)

    for w1, w2 in itertools.permutations(base_words, 2):
        combo = w1 + w2
        if args.min <= len(combo) <= args.max:
            wordlist.add(combo)

    enriched = set()
    for w in wordlist:
        enriched |= add_special_chars(w)

    wordlist |= enriched

    # Filters for tools
    if args.hashcat:
        wordlist = {w for w in wordlist if len(w) >= 6}

    if args.hydra:
        wordlist = {w for w in wordlist if len(w) <= 16}

    # Strength Split
    weak, medium, strong = set(), set(), set()
    for pw in wordlist:
        cat = classify_password(pw)
        if cat == "weak": weak.add(pw)
        elif cat == "medium": medium.add(pw)
        else: strong.add(pw)

    output_dir = "wordlists"
    Path(output_dir).mkdir(exist_ok=True)

    def save_file(name, data):
        with open(f"{output_dir}/{name}.txt", "w") as f:
            f.write("\n".join(sorted(data, key=lambda x: (len(x), x))))

    save_file("weak", weak)
    save_file("medium", medium)
    save_file("strong", strong)
    save_file("full", wordlist)

    print(f"{GREEN}[+] Generated: {len(wordlist)} total passwords")
    print(f"[+] weak.txt: {len(weak)}")
    print(f"[+] medium.txt: {len(medium)}")
    print(f"[+] strong.txt: {len(strong)}")
    print(f"[+] Saved in /wordlists/{RESET}")
