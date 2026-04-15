```markdown
# Collatz-Deep-Dive v1.0

A powerful, colorful, and high‑performance tool for exploring the Collatz conjecture ($3n+1$ problem) with parallel processing, cycle detection for negative inputs, extensive logging, and cross‑platform desktop notifications.

![Python Version](https://img.shields.io/badge/python-3.9+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- **Manual Calculation** – Compute the Collatz sequence for any positive integer with real‑time step display and detailed statistics.
- **Powers Test** – Automatically test sequences of the form $base^{exponent}$. For $base = 2$, it verifies expected properties. **Parallel execution** utilizes all available CPU cores for maximum throughput.
- **Negative Numbers** – Explore the extended Collatz function on negative integers. Integrated **cycle detection** identifies re‑entry points and cycle lengths.
- **Optimized Calculation Backends**:
  - `collatz_step` – Fully verified with reverse checks.
  - `collatz_fast` – Lightweight, streamlined logic.
  - `collatz_superfast` – Uses trailing‑zero counts to skip multiple even steps in a single operation.
- **Rich Console Output** – Color‑coded steps and dynamic progress bars.
- **Automatic Logging** – Every session generates timestamped logs in `logs/results/`.
- **Desktop Notifications** – Receive alerts when long‑running tests finish.

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Performance Notes](#performance-notes)
- [Acknowledgments](#acknowledgments)
- [License](#license)

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/importsyss/Collatz-Deep-Dive.git](https://github.com/importsyss/Collatz-Deep-Dive.git)
   cd Collatz-Deep-Dive
   ```

2. **Setup environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate         # Windows
   pip install -r other/requirements.txt
   ```

3. **Run**
   ```bash
   python collatz.py
   ```

## 🚀 Usage

### Main Menu
The interactive CLI allows you to choose between manual mode, powers testing (parallelized), and negative number exploration. You can also reset all logs directly from the menu.

### Manual Mode
Enter any positive integer. For numbers $\le 10^4$, the sequence is printed with color highlights (Blue for even, Yellow for odd).

### Negative Mode
Integrated **cycle detection** pinpoint infinite loops in the negative domain, showing entry points and cycle lengths.

## 📁 Directory Structure

```text
Collatz-Deep-Dive/
├── collatz.py               # Main application
├── other/
│   └── requirements.txt     # Dependencies
├── logs/
│   ├── debug/               # System logs
│   └── results/             # Calculation results
└── README.md
```

## ⚡ Performance Notes
- **Bit Manipulation:** Uses bit-shifting in `superfast` mode for rapid division of even numbers.
- **Multiprocessing:** Distributes heavy testing across `cpu_count() - 1` cores.
- **Large Integers:** Supports numbers with thousands of digits by overriding default string conversion limits.

## 🙏 Acknowledgments
This project was envisioned and developed by **importsyss**, who provided the core ideas, the project's foundation, and the overall architectural direction.

Technical refinement and optimization were supported by:
- **Gemini** & **DeepSeek** – Primary assistance with logic optimization and parallel processing.
- **Claude** – Contributions to specific code segments and documentation formatting.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Happy Collatz exploring!* 🔢✨
```.