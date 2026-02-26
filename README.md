# Victimator-X v1.6.0

Defensive password auditing toolkit for identifying weak password patterns and improving policy quality.

## Legal and Ethical Notice

Use this tool only on accounts and systems you own or are explicitly authorized to assess.
Unauthorized access attempts are illegal.

---

## What Changed

- Refactored from a single script into a modular `core/` architecture.
- Added `core/engine/` with `async`, `threading`, and `parallel` execution modes.
- Added `core/ui/` to centralize all terminal UI logic.
- Added `core/metadata.py` as a single metadata source used via f-strings.
- Added structured output in `output/` with logs, wordlists, and reports.
- Added beginner-friendly prompts and explicit ethical confirmation.
- Added richer verified subject prompts (organization, role, email/phone hints, MFA, manager use, rotation age, risk notes).
- Added `--self-check` connectivity checks for engines and output writeability.
- Added a small nano-ai helper (`--ask-ai`) and run-time remediation guidance.
- Expanded weak-password analysis with:
  - policy violations
  - entropy scoring
  - common weak-password detection
  - personal-info similarity detection
  - passphrase suggestions

---

## Project Structure

```text
Victimator-X/
├── victimator-x.py
├── core/
│   ├── cli.py
│   ├── audit.py
│   ├── generator.py
│   ├── policy.py
│   ├── reporting.py
│   ├── logging_setup.py
│   ├── models.py
│   ├── metadata.py
│   ├── nano_ai.py
│   ├── validation.py
│   ├── healthcheck.py
│   ├── utils.py
│   ├── ui/
│   │   ├── styles.py
│   │   └── terminal.py
│   └── engine/
│       ├── async_engine.py
│       ├── threading_engine.py
│       ├── parallel_engine.py
│       └── coordinator.py
├── output/
│   ├── logs/
│   ├── wordlists/
│   └── reports/
└── README.md
```

---

## Installation

```bash
git clone https://github.com/voltsparx/Victimator-X.git
cd Victimator-X
```

---

Requires Python 3.10+.

## Usage

### Interactive (Beginner Friendly)

```bash
python victimator-x.py
```

The tool will ask for subject details, confirm ethical usage, and generate defensive audit artifacts.

---

### Non-Interactive

```bash
python victimator-x.py \
  --subject-name "Alice Carter" \
  --aliases "alice,acarter,a.carter" \
  --keywords "gaming,runner,phoenix" \
  --favorite-numbers "7,13,99" \
  --birth-year 1999 \
  --organization "Blue Team" \
  --role "employee" \
  --email-hint "alice.carter@example.com" \
  --phone-hint "+1-555-0199" \
  --mfa-enabled no \
  --password-manager no \
  --last-rotation-days 240 \
  --risk-notes "reuse,shared-device" \
  --engine auto \
  --workers 8 \
  --max-candidates 30000 \
  --ask-ai "how to reduce weak passwords?" \
  --yes
```

### Audit Existing Passwords From File

```bash
python victimator-x.py \
  --subject-name "Alice Carter" \
  --password-file passwords.txt \
  --engine threading \
  --yes
```

`passwords.txt` should contain one password per line.

---

## Engine Modes

- `auto`: chooses engine based on workload
- `async`: async task orchestration
- `threading`: thread pool execution
- `parallel`: process pool execution

---

## Output Layout

```text
output/
├── logs/
│   └── victimator-x.log
├── wordlists/
│   └── <subject-name-slug>/
│       ├── weak.txt
│       ├── medium.txt
│       ├── strong.txt
│       └── full.txt
└── reports/
    └── <subject-name-slug>/
        ├── summary.json
        ├── report.txt
        └── password-audit.json   # only when --password-file is used
```

---

## Key CLI Options

| Option | Description |
|---|---|
| `--subject-name` | Name used for subject-scoped output folders |
| `--aliases` | Comma-separated known aliases/usernames |
| `--keywords` | Comma-separated personal keywords |
| `--favorite-numbers` | Comma-separated reused numbers |
| `--birth-year` | Optional year used in weak-pattern checks |
| `--password-file` | File with passwords to audit |
| `--organization` / `--role` | Extra profile context for audit attribution |
| `--email-hint` / `--phone-hint` | Optional hints used for weak-pattern detection |
| `--mfa-enabled` / `--password-manager` | Security hygiene context (`yes`, `no`, `unknown`) |
| `--last-rotation-days` | Password age context |
| `--risk-notes` | Comma-separated contextual risk markers |
| `--engine` | `auto`, `async`, `threading`, or `parallel` |
| `--workers` | Worker count |
| `--min-length` / `--max-length` | Generated candidate length bounds |
| `--max-candidates` | Candidate generation cap |
| `--policy-min-length` | Password policy minimum length |
| `--output-root` | Root output directory (default `output`) |
| `--self-check` | Run engine/output connectivity checks and exit |
| `--ask-ai` | Ask nano-ai for quick defensive guidance |
| `--no-nano-ai` | Disable nano-ai guidance in generated report |
| `--yes` | Skip interactive ethical confirmation |

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Open a pull request

---

Read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Security

See [SECURITY.md](SECURITY.md).

## License

MIT
