```markdown
# Collatz Conjecture Explorer

A powerful Python tool to explore the famous Collatz conjecture (also known as the \(3n+1\) problem).  
Test huge numbers, run automated power tests, detect cycles in negative domains, and save detailed logs.

---

## 📌 What is the Collatz Conjecture?

The Collatz conjecture states that for any positive integer \(n\):

- If \(n\) is **even**, divide it by 2: \(n \to n/2\)
- If \(n\) is **odd**, multiply by 3 and add 1: \(n \to 3n + 1\)

Repeating this process will eventually reach the cycle **4 → 2 → 1 → 4** for every positive integer ever tested.  
Despite its simplicity, the conjecture remains unproven.

This program lets you test the conjecture on numbers of arbitrary size, including:
- Manual single‑number calculations
- Automated powers‑of‑\(b\) tests (e.g., \(2^{68}\))
- Negative integer cycles (a different, fascinating behaviour)

---

## 🚀 Features

- ✅ **Manual Mode** – Enter any positive integer and watch the sequence step‑by‑step (or get a fast summary for large numbers).
- ✅ **Powers Test** – Test \(b^1, b^2, b^3, \dots\) automatically.  
  For \(b=2\) it verifies that steps = exponent and odd steps = 0 (as predicted by the conjecture).  
  Handles **extremely large exponents** thanks to Python's unlimited integer precision.
- ✅ **Negative Mode** – Explore the Collatz function on negative integers, which produces cycles (e.g., \(-5 \to -14 \to -7 \to -20 \to -10 \to -5\)).
- ✅ **Detailed Logging** – Every run saves a timestamped log file in the `logs/results/` folder.
- ✅ **Progress Window** – Optional GUI progress bar for long calculations (uses `tkinter`).
- ✅ **Super‑fast Algorithm** – Optimised `collatz_superfast` uses trailing‑zero counting to skip multiple even steps at once.

---

## 🛠️ Requirements

- **Python 3.9+** (for `zoneinfo` support; otherwise install `backports.zoneinfo`)
- Libraries:
  - `colorama` – coloured terminal output  
  - `tkinter` – usually included with Python (optional, for the progress window)

Install the required package with:

```bash
pip install colorama
```

> ⚠️ On some Linux distributions you may need to install `tkinter` separately:  
> `sudo apt-get install python3-tk` (Ubuntu/Debian)

---

## ▶️ How to Run

1. Clone or download the script.
2. Open a terminal in the script’s directory.
3. Run:

```bash
python collatz_explorer.py
```

4. Use the interactive menu to choose a mode.

---

## 📁 Logs & Results

All results are stored inside the `logs/` directory:

- `logs/results/` – Detailed logs for each manual run, powers test, and negative test.
- `logs/debug/collatz.log` – Global debug log with timestamps and errors.

---

## 🧪 Example: A Gigantic Number

The program was tested with a **1728‑digit number** (the sequence `123214321414124256467688989` repeated 64 times).  
Despite its size, it eventually converged to the **4 → 2 → 1** cycle, confirming the conjecture once again.

You can try numbers of virtually any size – the only limit is your computer’s memory and patience!

---

## 👨‍💻 Credits

This project is a **collaboration between human and AI**:

- **Original concept, core logic, and manual improvements** by me (importsyss).
- **Code optimisation, bug fixes, and feature enhancements** developed with the assistance of **DeepSeek AI**.

The script combines human creativity with AI‑powered efficiency to deliver a robust and user‑friendly exploration tool.

---

## 📄 License

This project is open‑source and available under the [MIT License](LICENSE).  
Feel free to use, modify, and share it.

---

*Happy Collatz exploring!* 🔢✨
```