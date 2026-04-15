---

COLLATZ DEEP DRIVE v2.0

Collatz Deep Drive is a high-performance, feature-rich command-line application designed to explore the Collatz conjecture (3n + 1 problem) in depth. It combines optimized computation, parallel processing, cycle detection for negative integers, detailed logging, and cross-platform desktop notifications.

The tool is built for both experimentation and large-scale numerical testing, with a strong focus on performance, correctness, and observability.

Compatibility:

* Python 3.9 or higher
* Windows, macOS, Linux
  License: MIT

---

CORE FEATURES

Manual Calculation
Compute the Collatz sequence for any positive integer with optional full step-by-step output.
Includes:

* real-time colored visualization (even/odd steps)
* total steps, even/odd counts
* peak value reached during the sequence
* execution time measurement
* automatic consistency verification of counters

Powers Test (Parallel Engine)
Efficiently evaluates sequences of the form base^exponent.
Key capabilities:

* automatic batching and multiprocessing (cpu_count() - 1 cores)
* per-run performance timing (milliseconds)
* distribution analysis of even vs odd steps
* peak value tracking for each sequence
* anomaly detection with interactive continuation
* optional validation for powers of 2 (expected: steps = exponent, odd = 0)

Negative Numbers Mode
Extends the Collatz function to negative integers.
Includes:

* deterministic cycle detection using visited-state tracking
* identification of:

  * cycle entry point
  * cycle length
* detailed step logging and visualization

---

CALCULATION ENGINES

collatz_step
Validated implementation with reverse checks to guarantee correctness.

collatz_fast
Lightweight version optimized for speed with minimal overhead.

collatz_superfast
Highly optimized engine that compresses multiple even steps into one operation using bit manipulation (trailing zero counting).
This is the fastest available backend and is used in large-scale tests.

---

PERFORMANCE DESIGN

Bit-Level Optimization
Even-number divisions are accelerated using bitwise operations and trailing-zero counting.

Multiprocessing
The powers test distributes workloads across multiple processes, maximizing CPU utilization.

Large Integer Support
Handles extremely large integers (thousands of digits) by removing Python’s default string conversion limits.

Batch Execution
Parallel tests are grouped into batches to reduce overhead and improve throughput.

---

LOGGING SYSTEM

The application automatically generates detailed logs for every operation.

Directory structure:

* logs/debug/     → system-level logs and errors
* logs/results/   → results of calculations and tests

Features:

* timestamped entries (Europe/Rome timezone)
* structured output for reproducibility
* separate log files for each run
* anomaly and error tracking

A built-in option allows full reset of all logs.

---

DESKTOP NOTIFICATIONS

The application sends notifications when long-running tasks complete.

Platform support:

* Windows → plyer (if available)
* macOS → osascript
* Linux → notify-send or zenity fallback

---

USER INTERFACE

Interactive CLI menu with the following options:

1. Manual calculation
2. Powers test (parallel-ready)
3. Negative numbers (cycle detection)
   c. Reset all logs
   q. Exit

Features:

* colored terminal output (via colorama)
* formatted tables for large tests
* progress visualization (bars and statistics)
* safe input handling and interruption support

---

ERROR HANDLING

Robust error management system with custom exceptions:

* InvalidInputError → invalid user input
* CalculationError → arithmetic inconsistencies
* CycleDetectedError → detected cycles in negative mode

All critical errors are logged with stack traces for debugging.

---

PROJECT STRUCTURE

Collatz-Deep-Dive/

* collatz.py              → main application
* other/

  * requirements.txt      → dependencies
* logs/

  * debug/                → internal logs
  * results/              → execution outputs

---

TYPICAL USE CASES

* Studying Collatz sequence behavior
* Testing large ranges of exponential inputs
* Investigating parity distribution (even vs odd steps)
* Exploring negative-domain cycles
* Benchmarking integer sequence performance

---

ACKNOWLEDGMENTS

The project was created and designed by importsyss, including the core architecture and implementation.

AI-assisted development contributions:

* Gemini and DeepSeek → optimization strategies and parallel processing
* Claude → support for specific components and documentation refinement

---

LICENSE

This project is distributed under the MIT License. See the LICENSE file for details.

---
