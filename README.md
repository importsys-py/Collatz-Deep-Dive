```markdown
# Collatz Deep Drive v2.0

A powerful, colorful, and high‑performance tool for exploring the Collatz conjecture (3n+1 problem) with parallel processing, cycle detection for negative inputs, extensive logging, and cross‑platform desktop notifications.

![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Manual Calculation** – Compute the Collatz sequence for any positive integer with real‑time step display and detailed statistics.
- **Powers Test** – Automatically test sequences of the form `base^exponent`. For base = 2 it verifies the expected properties (steps = exponent, odd steps = 0). **Parallel execution** uses all available CPU cores for massive speed.
- **Negative Numbers** – Explore the extended Collatz function on negative integers. **Cycle detection** identifies re‑entry points and cycle lengths.
- **Super‑fast Optimised Modes** – Three calculation backends:
  - `collatz_step` – Fully verified with reverse checks.
  - `collatz_fast` – Lightweight, no extra verification.
  - `collatz_superfast` – Uses trailing‑zero count to skip multiple even steps at once.
- **Rich Console Output** – Colour‑coded steps (blue = even, yellow = odd) and progress bars.
- **Automatic Logging** – Every run creates timestamped logs in `logs/results/`. A separate debug log (`logs/debug/collatz.log`) records all events.
- **Desktop Notifications** – Get notified when long‑running tests finish (Windows, macOS, Linux).
- **Cross‑Platform** – Works on Windows, macOS, and Linux.

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Main Menu](#main-menu)
  - [Manual Mode](#manual-mode)
  - [Powers Test](#powers-test)
  - [Negative Mode](#negative-mode)
  - [Reset Logs](#reset-logs)
- [Directory Structure](#directory-structure)
- [Dependencies](#dependencies)
- [Performance Notes](#performance-notes)
- [Contributing](#contributing)
- [License](#license)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/collatz-deep-drive.git
   cd collatz-deep-drive
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install colorama plyer
   ```
   > `plyer` is optional – it enables native Windows notifications. On macOS/Linux, notifications work out‑of‑the‑box via `osascript` / `notify-send`.

4. **Run the program**
   ```bash
   python collatz.py
   ```

## 🚀 Usage

### Main Menu

```
==================================================
         COLLATZ DEEP DRIVE v2.0
         Windows · 7 cores
==================================================

  1. Manual calculation
  2. Powers test  ✦ parallel-ready
  3. Negative numbers  (cycle detection)
  c. Reset all logs (delete files)

  q. Exit

==================================================
```

### Manual Mode

Choose option `1` and enter a positive integer.  
- For numbers ≤ 10⁴, every step is printed in colour.
- For larger numbers, you can choose to show all steps or only the final summary.
- A log file is saved in `logs/results/`.

### Powers Test

Choose option `2` and provide:
- **Base** (default 2)
- Whether to verify the power‑of‑2 conditions (only for base = 2)
- Automatic continuation on anomalies
- Use parallel processing (recommended)

The test computes `base^1`, `base^2`, … until you interrupt it or an anomaly occurs (if verification is on).  
A live table shows exponent, steps, even/odd counts, distribution bar, peak value, and elapsed milliseconds.

### Negative Mode

Choose option `3` and enter an integer. Positive numbers are automatically negated.  
The extended Collatz function is applied. If a cycle is detected, the program displays:
- The node where the cycle re‑enters
- The step number of first entry
- The cycle length

### Reset Logs

Press `c` to delete the entire `logs/` directory and recreate it fresh.

## 📁 Directory Structure

```
collatz-deep-drive/
├── collatz.py               # Main program
├── logs/
│   ├── debug/
│   │   └── collatz.log      # Global debug log (all runs)
│   └── results/
│       ├── collatz_manual_YYYYMMDD_HHMMSS.txt
│       ├── collatz_powers_2_YYYYMMDD_HHMMSS.txt
│       └── collatz_negative_... .txt
└── README.md
```

## 📦 Dependencies

| Package    | Purpose                           | Required |
|------------|-----------------------------------|----------|
| `colorama` | Cross‑platform coloured terminal output | Yes |
| `plyer`    | Native Windows notifications      | Optional |
| `zoneinfo` | Timezone handling (Python ≥3.9 built‑in) | Built‑in |
| `multiprocessing`, `threading`, `queue` | Parallel processing | Built‑in |

> Python 3.9 or higher is required because of `zoneinfo`.

## ⚡ Performance Notes

- The **super‑fast** mode (`collatz_superfast`) is used in the powers test. It exploits the fact that an even number `n` can be divided by `2^k` where `k` is the number of trailing zeros in its binary representation. This dramatically reduces the number of loop iterations.
- Parallel testing uses `multiprocessing.Pool` with `cpu_count() - 1` workers to avoid system overload.
- For extremely large integers (thousands of digits), `sys.set_int_max_str_digits(0)` removes the string conversion limit.

## 🤝 Contributing

Contributions are welcome!  
If you find a bug, have a feature request, or want to improve the code:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please keep the code style consistent and add appropriate comments.

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

*Happy Collatz exploring!* 🔢✨
```