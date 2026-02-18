# Victimator-X 🔐  
### Password Profiling & Wordlist Generator

<p align="center">
  <b>Ethical Security Tool for Targeted Password Auditing</b><br>
  Built for penetration testers, red teams, and security researchers.
</p>

---

## ⚠️ Legal & Ethical Notice

> ❗ **For authorized security testing only**  
> ❗ Unauthorized use is illegal  
> ❗ The author is not responsible for misuse  

By using this tool, you agree to test **only systems you own or have explicit permission to assess**.

---

## 📖 Overview

**Victimator-X** is an advanced password profiling tool that generates highly targeted wordlists using personal, professional, and digital footprint data.

It simulates realistic human password patterns to improve the effectiveness of:

- 🔍 Password strength audits  
- 🛡️ Security assessments  
- 🎯 Red team engagements  
- 🧪 CTF challenges & research  

---

## ✨ Features

### 🔤 Smart Word Generation
- Leet speak transformations  
- Name & keyword permutations  
- Special character injection  
- Human-like password patterns  

### 🧠 Intelligent Classification
- Automatic strength scoring  
- Categorized outputs:
  - `weak`
  - `medium`
  - `strong`

### ⚙️ Tool Optimization Modes
- `--hashcat` → optimized for Hashcat  
- `--hydra` → optimized for Hydra  

### 🧩 Flexible Input Support
- Personal details
- Hobbies & interests
- Favorite numbers
- School/company names
- Multi-value fields

### 🛡️ Safety & UX
- Graceful exit handling (CTRL+C)
- Cross-platform terminal support
- No external dependencies
- Legal warning prompt

---

## 📦 Installation

### Requirements
- Python **3.x**
- Built-in modules only (no pip required):
  - `itertools`
  - `platform`
  - `os`
  - `signal`
  - `pathlib`
  - `argparse`

### Clone the Repository
~~~bash
git clone https://github.com/voltsparx/Victimator-X.git
cd Victimator-X
~~~

---

## 🚀 Usage

Run the tool:

~~~bash
python3 victimator-x.py
~~~

### Optional Modes

~~~bash
--hashcat    Optimize output for Hashcat
--hydra      Optimize output for Hydra
--min N      Minimum password length
--max N      Maximum password length
~~~

### Example

~~~bash
python3 victimator-x.py --hashcat --min 8 --max 16
~~~

---

## 🧾 Input Fields

All inputs are optional — more data = more accurate wordlists.

| Category | Examples |
|----------|----------|
| Personal | John, Doe, 15071990 |
| Numbers | 7, 13, 99 |
| Hobbies | gaming, hiking, music |
| Digital | reddit.com, xXJohnXx |
| Education | Central High School |

---

## 📂 Output Structure

Victimator-X generates categorized wordlists:

~~~
/wordlists/
├── weak.txt
├── medium.txt
├── strong.txt
└── full.txt
~~~

### Output Highlights
- ✔ 1,000 – 50,000+ targeted combinations  
- ✔ Sorted by length & readability  
- ✔ Ready for Hashcat, Hydra, John the Ripper  

---

## 🧪 Example Generated Passwords

~~~
John123
J0hn!
Doe@1990
gaming#7
CentralHigh2024
~~~

---

## 🧠 How It Works

### Workflow

~~~
Input Data
   ↓
Leet Transformations
   ↓
Permutations & Combinations
   ↓
Special Character Injection
   ↓
Length Filtering
   ↓
Strength Classification
   ↓
Categorized Wordlists
~~~

---

## 🛠 CLI Options

| Option | Description |
|--------|------------|
| `--hashcat` | Ensures compatibility with Hashcat rules |
| `--hydra` | Limits length for Hydra compatibility |
| `--min` | Minimum password length |
| `--max` | Maximum password length |

---

## ✅ Ethical Use Cases

✔ Password strength auditing  
✔ Authorized penetration testing  
✔ Red team exercises  
✔ Security education  
✔ Capture The Flag competitions  

---

## ❌ Prohibited Uses

✖ Unauthorized system access  
✖ Brute-forcing unknown targets  
✖ Violating cybercrime laws  

---

## 📊 Version

**Current Version:** `1.2.0`

---

## 🤝 Contributing

Contributions are welcome!

If you'd like to improve Victimator-X:

1. Fork the repo  
2. Create a feature branch  
3. Submit a pull request  

---

## 🐞 Reporting Issues

Report bugs or request features here:  
👉 https://github.com/voltsparx/Victimator-X/issues

---

## 📜 License

MIT License — Use responsibly.

---

## 👤 Author

**voltsparx**  
📧 voltsparx@gmail.com  
🌐 https://github.com/voltsparx  

---

## ⭐ Support the Project

If you find Victimator-X useful, consider giving it a ⭐ on GitHub — it helps others discover the tool!
