---

# Collatz Deep Drive v2.0

A powerful, high-performance CLI tool for exploring the Collatz conjecture (3n + 1 problem), featuring parallel computation, cycle detection for negative integers, advanced logging, and cross-platform notifications.

---

## Features

### Manual Calculation

Compute the Collatz sequence for any positive integer with:

* real-time step-by-step visualization
* colored output (even / odd steps)
* total steps, even/odd counters
* peak value tracking
* execution time measurement
* automatic counter validation

---

### Powers Test (Parallel Engine)

Test numbers of the form:

base^exponent

Includes:

* multiprocessing across CPU cores
* batch execution for performance
* per-number timing (ms)
* even/odd distribution analysis
* peak tracking
* anomaly detection
* optional validation for powers of 2

---

### Negative Numbers (Cycle Detection)

Explore Collatz behavior over negative integers:

* automatic cycle detection
* entry point identification
* cycle length calculation
* full step logging

---

### Optimized Engines

* collatz_step
  Verified implementation with reverse checks

* collatz_fast
  Lightweight and efficient

* collatz_superfast
  Uses bit manipulation (trailing-zero compression) to skip multiple steps at once

---

### Logging System

All runs are automatically logged:

logs/debug/
logs/results/

Features:

* timestamped logs (Europe/Rome timezone)
* separate files per run
* anomaly tracking
* full reproducibility

---

### Desktop Notifications

Cross-platform notifications when tasks complete:

* Windows → plyer
* macOS → osascript
* Linux → notify-send / zenity

---

## Installation

Clone the repository:

git clone [https://github.com/importsys-py/Collatz-Deep-Dive.git](https://github.com/importsys-py/Collatz-Deep-Dive.git)
cd Collatz-Deep-Dive

Create virtual environment:

python -m venv venv

Activate:

Linux/macOS:
source venv/bin/activate

Windows:
venv\Scripts\activate

Install dependencies:

pip install -r other/requirements.txt

Run:

python collatz.py

---

## Usage

Interactive CLI menu:

1. Manual calculation
2. Powers test (parallel-ready)
3. Negative numbers (cycle detection)
   c. Reset logs
   q. Exit

---

## Performance

* Bit-level optimizations for even steps
* Multiprocessing using cpu_count() - 1
* Handles extremely large integers
* Batch execution for reduced overhead

---

## Error Handling

Custom exceptions:

* InvalidInputError
* CalculationError
* CycleDetectedError

All errors are logged with stack traces.

---

## Project Structure

Collatz-Deep-Dive/

collatz.py            → main application
other/
requirements.txt    → dependencies

logs/
debug/              → system logs
results/            → outputs

---

## Use Cases

* studying Collatz sequences
* testing large exponential inputs
* analyzing parity distribution
* detecting cycles in negative domain
* performance benchmarking

---

## Acknowledgments

Created by importsyss

AI-assisted development:

* Gemini and DeepSeek → optimization and parallel logic
* Claude → code and documentation refinement

---

## License

MIT License

---