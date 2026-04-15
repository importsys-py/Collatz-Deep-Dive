import sys
sys.set_int_max_str_digits(0)
import os
import time
import threading
import queue
from datetime import datetime
from zoneinfo import ZoneInfo
from colorama import init, Fore, Style
import tkinter as tk
from tkinter import ttk

init(autoreset=True)

tz_rome   = ZoneInfo("Europe/Rome")
FMT       = "%d/%m/%Y %H:%M:%S"

LOGS_DIR      = "logs"
RESULTS_DIR   = os.path.join(LOGS_DIR, "results")
DEBUG_DIR     = os.path.join(LOGS_DIR, "debug")
DEBUG_LOG_FILE = os.path.join(DEBUG_DIR, "collatz.log")

for d in [LOGS_DIR, RESULTS_DIR, DEBUG_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass

class CalculationError(Exception): pass
class InvalidInputError(ValueError): pass
class CycleDetectedError(Exception):
    def __init__(self, node: int, entry_step: int, length: int):
        self.node = node
        self.entry_step = entry_step
        self.length = length
        super().__init__(f"Cycle detected: re-entry at {node} at step {entry_step}, length={length}")

def _write_log(level: str, message: str):
    now = datetime.now(tz_rome).strftime(FMT)
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] [{level}] {message}\n")
    except (OSError, IOError):
        pass

def log(level: str, message: str, color=Fore.GREEN):
    now = datetime.now(tz_rome).strftime(FMT)
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{now}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} "
          f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{color}{level}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} "
          f"{color}{message}{Style.RESET_ALL}")
    _write_log(level, message)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit(): msvcrt.getch()
    except ImportError:
        import termios, sys, select
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def wait_for_enter(prompt="\nPress Enter to continue..."):
    flush_input()
    try: input(prompt)
    except (EOFError, KeyboardInterrupt): pass

def collatz_step(n: int) -> tuple[int, bool]:
    if n & 1 == 0:
        r = n >> 1
        if r << 1 != n: raise CalculationError(f"Reverse verification failed on {n}: expected {n}, got {r << 1}")
        return r, True
    else:
        r = (n << 1) + n + 1
        if r & 1 != 0: raise CalculationError(f"3*{n}+1 = {r} — expected even result, got odd")
        return r, False

def collatz_step_fast(n: int) -> tuple[int, bool]:
    return (n >> 1, True) if n & 1 == 0 else ((n << 1) + n + 1, False)

def verify_counters(steps: int, even: int, odd: int):
    if even < 0 or odd < 0: raise CalculationError(f"Negative counter — even={even}, odd={odd}")
    if even + odd != steps: raise CalculationError(f"Incorrect counter sum — even({even}) + odd({odd}) = {even + odd}, expected {steps}")

def collatz(n: int, verbose: bool = True, delay: float = 0.0, log_writer=None, progress_callback=None):
    if not isinstance(n, int) or n <= 0: raise InvalidInputError(f"Invalid input: expected integer > 0, got {n!r}")
    steps = even = odd = 0
    peak = n
    if verbose: log("INFO", f"Starting Collatz with n = {n}", Fore.CYAN)
    while n > 1:
        old = n
        try: n, is_even = collatz_step(n)
        except CalculationError as e:
            log("CALCULATION ERROR", str(e), Fore.RED)
            _write_log("CALCULATION ERROR", str(e))
            raise
        if n > peak: peak = n
        if is_even: even += 1
        else: odd += 1
        steps += 1
        try: verify_counters(steps, even, odd)
        except CalculationError as e:
            log("COUNTER ERROR", str(e), Fore.RED)
            _write_log("COUNTER ERROR", str(e))
            raise
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.CYAN}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙ {Fore.GREEN}{n}{Style.RESET_ALL}")
            if delay > 0: time.sleep(delay)
        if log_writer:
            try: log_writer(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception: pass
        if progress_callback:
            try: progress_callback(steps, even, odd, n, peak)
            except Exception: pass
    return steps, even, odd, n, peak

def collatz_fast(n: int, verbose: bool = True, log_writer=None, progress_callback=None):
    steps = even = odd = 0
    peak = n
    while n > 1:
        old = n
        n, is_even = collatz_step_fast(n)
        if n > peak: peak = n
        if is_even: even += 1
        else: odd += 1
        steps += 1
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.CYAN}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙  {Fore.GREEN}{n}{Style.RESET_ALL}")
        if log_writer:
            try: log_writer(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception: pass
        if progress_callback:
            try: progress_callback(steps, even, odd, n, peak)
            except Exception: pass
    return steps, even, odd, n, peak

def collatz_superfast(n: int, progress_callback=None, log_writer=None):
    steps = even = odd = 0
    peak = n
    while n > 1:
        if n & 1 == 0:
            tz = (n & -n).bit_length() - 1
            n >>= tz
            even += tz
            steps += tz
        else:
            n = (n << 1) + n + 1
            odd += 1
            steps += 1
        if n > peak: peak = n
        if progress_callback:
            try: progress_callback(steps, even, odd, n, peak)
            except Exception: pass
    return steps, even, odd, n, peak

def collatz_step_negative(n: int) -> tuple[int, bool]:
    if n & 1 == 0:
        r = n >> 1
        if n >= 0 and n - (n >> 1) != r: raise CalculationError(f"Mismatch in negative even step on {n}: expected {r}")
        return r, True
    else:
        r = (n << 1) + n + 1
        if r != 3 * n + 1: raise CalculationError(f"Mismatch in negative odd step on {n}: expected {3 * n + 1}, got {r}")
        return r, False

def collatz_negative(n: int, verbose: bool = True, log_writer=None):
    if n == 0: raise InvalidInputError("0 is not a valid input for negative Collatz")
    seen = {}
    steps = 0
    log("INFO", f"Starting NEGATIVE Collatz with n = {n}", Fore.MAGENTA)
    while n not in seen:
        seen[n] = steps
        old = n
        try: n, is_even = collatz_step_negative(n)
        except CalculationError as e:
            log("CALCULATION ERROR", str(e), Fore.RED)
            _write_log("CALCULATION ERROR", str(e))
            raise
        steps += 1
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.MAGENTA}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙  {Fore.YELLOW}{n}{Style.RESET_ALL}")
        if log_writer:
            try: log_writer(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception: pass
    entry_step = seen[n]
    length = steps - entry_step
    raise CycleDetectedError(n, entry_step, length)

def _bar(value: int, total: int, width: int = 12) -> str:
    filled = round(value / total * width) if total else 0
    filled = max(0, min(filled, width))
    return "█" * filled + "░" * (width - filled)

def _format_large_number(n: int, max_len: int = 20) -> str:
    s = str(n)
    if len(s) <= max_len: return s
    exp = len(s) - 1
    return f"{s[0]}.{s[1:4]}e+{exp}"

class ProgressWindow:
    def __init__(self, title, total_steps_known=False, total_steps=0):
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("500x200")
        self.root.resizable(False, False)
        self.root.attributes('-topmost', True)
        self.total_steps_known = total_steps_known
        self.total_steps = total_steps
        self.current_steps = 0
        self.start_time = time.perf_counter()
        self.running = True
        self.queue = queue.Queue()
        self.calculation_finished = False
        self.calculation_result = None
        self.calculation_error = None
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.status_label = ttk.Label(main_frame, text="Calculating...", font=('TkDefaultFont', 10, 'bold'))
        self.status_label.pack(pady=(0,10))
        self.steps_label = ttk.Label(main_frame, text="Steps: 0")
        self.steps_label.pack()
        self.time_label = ttk.Label(main_frame, text="Elapsed time: 0.0 s")
        self.time_label.pack()
        self.eta_label = ttk.Label(main_frame, text="")
        if total_steps_known:
            self.eta_label.pack()
            self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
            self.progress.pack(pady=10)
            self.progress['maximum'] = total_steps
        else:
            self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=400, mode='indeterminate')
            self.progress.pack(pady=10)
            self.progress.start(10)
        self.speed_label = ttk.Label(main_frame, text="Speed: 0 steps/s")
        self.speed_label.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_progress(self, steps, even, odd, n, peak):
        try:
            self.queue.put_nowait(('update', steps, time.perf_counter()))
        except queue.Full:
            pass

    def on_closing(self):
        self.running = False
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg[0] == 'update':
                    _, steps, now = msg
                    self.current_steps = steps
                    elapsed = now - self.start_time
                    self.steps_label.config(text=f"Steps: {steps}")
                    self.time_label.config(text=f"Elapsed time: {elapsed:.2f} s")
                    speed = steps / elapsed if elapsed > 0 else 0
                    self.speed_label.config(text=f"Speed: {speed:.2f} steps/s")
                    if self.total_steps_known:
                        self.progress['value'] = steps
                        if steps > 0:
                            eta = (self.total_steps - steps) / speed if speed > 0 else 0
                            self.eta_label.config(text=f"Estimated time remaining: {eta:.2f} s")
                elif msg[0] == 'done':
                    self.calculation_finished = True
                    self.calculation_result = msg[1]
                    self.running = False
                    self.root.destroy()
                    return
                elif msg[0] == 'error':
                    self.calculation_error = msg[1]
                    self.running = False
                    self.root.destroy()
                    return
        except queue.Empty: pass
        except tk.TclError:
            self.running = False
            return
        if self.running:
            try:
                self.root.after(100, self.process_queue)
            except tk.TclError:
                pass

    def run_calculation(self, target_func, *args, **kwargs):
        def worker():
            try:
                kwargs['progress_callback'] = self.update_progress
                result = target_func(*args, **kwargs)
                self.queue.put(('done', result))
            except Exception as e:
                self.queue.put(('error', e))
        self.thread = threading.Thread(target=worker, daemon=True)
        self.thread.start()
        self.root.after(100, self.process_queue)
        try:
            self.root.mainloop()
        except tk.TclError:
            pass
        if not self.calculation_finished and self.calculation_error is None: return None
        if self.calculation_error is not None: raise self.calculation_error
        return self.calculation_result

def test_powers():
    base = 2
    while True:
        try:
            raw = input(Fore.CYAN + "Enter the base for the powers test (integer >= 2, default 2): " + Style.RESET_ALL).strip()
            if not raw: base = 2; break
            raw = raw.replace("_", "").replace(" ", "")
            base = int(raw)
            if base < 2: print(f"{Fore.RED}Base must be >= 2.{Style.RESET_ALL}"); continue
            break
        except ValueError: print(f"{Fore.RED}Invalid input. Please enter an integer.{Style.RESET_ALL}")
        except KeyboardInterrupt:
            log("INFO", "Test cancelled by user", Fore.YELLOW)
            return
    verify_conditions = False
    if base == 2:
        try:
            resp_cond = input(Fore.CYAN + "Verify power-of-2 conditions (steps = exponent, odd=0)? (y/n, default y): " + Style.RESET_ALL).strip().lower()
            verify_conditions = resp_cond != 'n'
        except KeyboardInterrupt:
            log("INFO", "Test cancelled", Fore.YELLOW)
            return
    else:
        print(f"{Fore.YELLOW}Note: for base {base} the power-of-2 conditions are not expected. The test will not stop.{Style.RESET_ALL}")
    auto_yes = False
    if verify_conditions:
        try:
            resp_auto = input(Fore.CYAN + "Automatically answer 'y' to all continuation prompts? (y/n, default n): " + Style.RESET_ALL).strip().lower()
            auto_yes = (resp_auto == 'y')
        except KeyboardInterrupt:
            log("INFO", "Test cancelled", Fore.YELLOW)
            return
    log("INFO", f"POWERS TEST OF {base} — start", Fore.MAGENTA)
    COL_EXP, COL_STEPS, COL_EVEN, COL_ODD, COL_PCT, COL_PEAK, COL_MS, COL_OK, COL_DIST = 8, 10, 10, 10, 8, 28, 10, 5, 29
    TOT = COL_EXP + COL_STEPS + COL_EVEN + COL_ODD + COL_PCT + COL_DIST + COL_PEAK + COL_MS + COL_OK
    sep = Fore.LIGHTBLACK_EX + "─" * TOT + Style.RESET_ALL
    header = (f"{Fore.LIGHTBLACK_EX}{'EXP':<{COL_EXP}}{'STEPS':<{COL_STEPS}}{'EVEN':<{COL_EVEN}}{'ODD':<{COL_ODD}}{'%EVEN':<{COL_PCT}}"
              f"{'DIST EVEN(blue)░ ODD(yellow)█':<{COL_DIST}}{'PEAK':<{COL_PEAK}}{'ms':<{COL_MS}}{'OK':<{COL_OK}}{Style.RESET_ALL}")
    print(f"\n{sep}\n{header}\n{sep}")
    tot_steps = tot_even = tot_odd = max_steps = max_peak = counter = 0
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_powers_{base}_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    def write_specific(line: str):
        try:
            with open(specific_log, "a", encoding="utf-8") as f: f.write(line + "\n")
        except (OSError, IOError):
            log("WARNING", f"Could not write to {specific_log}", Fore.YELLOW)
    write_specific(f"Powers test of {base} - started {datetime.now(tz_rome).strftime(FMT)}")
    write_specific("")
    for i in range(1, 1_000_000_000):
        n_orig = base ** i
        t0 = time.perf_counter()
        try:
            # Utilizzo di collatz_superfast per maggiore efficienza
            steps, even, odd, final, peak = collatz_superfast(n_orig)
        except KeyboardInterrupt:
            log("INFO", "Test interrupted by user", Fore.YELLOW)
            break
        except Exception as e:
            log("FATAL ERROR", f"{base}^{i}: {e}", Fore.RED)
            _write_log("FATAL ERROR", f"{base}^{i}: {e}")
            write_specific(f"FATAL ERROR {base}^{i}: {e}")
            log("INFO", f"Test interrupted at power {base}^{i}", Fore.RED)
            break
        ms = (time.perf_counter() - t0) * 1000
        ok = (final == 1 and steps == i and odd == 0) if verify_conditions else True
        tot_steps += steps; tot_even += even; tot_odd += odd
        if steps > max_steps: max_steps = steps
        if peak > max_peak: max_peak = peak
        counter += 1
        if not ok:
            log("ERROR", f"{base}^{i} — unexpected result: final={final}, steps={steps}, odd={odd}", Fore.RED)
            _write_log("ERROR", f"{base}^{i} | final={final} steps={steps} odd={odd}")
            write_specific(f"ANOMALY {base}^{i}: final={final} steps={steps} odd={odd}")
            print(f"\n{Fore.RED}{'─'*60}{Style.RESET_ALL}\n  {Fore.RED}ANOMALY DETECTED{Style.RESET_ALL} — {base}^{i}\n"
                  f"  Final value    : {Fore.RED}{final}{Style.RESET_ALL}  (expected 1)\n"
                  f"  Total steps    : {steps}  (expected {i})\n  Odd steps      : {odd}  (expected 0)\n"
                  f"{Fore.RED}{'─'*60}{Style.RESET_ALL}\n")
            if auto_yes:
                choice = "y"
                print(f"  {Fore.YELLOW}Automatic continuation...{Style.RESET_ALL}")
            else:
                while True:
                    try: choice = input(f"  {Fore.YELLOW}Continue test? [{Fore.GREEN}y{Fore.YELLOW}/{Fore.RED}n{Fore.YELLOW}]: {Style.RESET_ALL}").strip().lower()
                    except KeyboardInterrupt: choice = "n"
                    if choice in ("y","yes"):
                        log("INFO", f"Continuation requested after anomaly on {base}^{i}", Fore.YELLOW)
                        _write_log("INFO", f"User chose to continue after anomaly on {base}^{i}")
                        write_specific(f"User chose to continue after anomaly on {base}^{i}")
                        break
                    elif choice in ("n","no"):
                        log("INFO", f"Test interrupted by user at power {base}^{i}", Fore.RED)
                        _write_log("INFO", f"User interrupted test at power {base}^{i}")
                        write_specific(f"Test interrupted by user at power {base}^{i}")
                        print()
                        break
                    else: print(f"  {Fore.RED}Invalid response.{Style.RESET_ALL}")
            if choice in ("n","no"): break
        pct = even / steps if steps else 0
        bar_e = _bar(even, steps, 12)
        bar_o = _bar(odd, steps, 12)
        dist_str = f"{Fore.BLUE}{bar_e}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL}{Fore.YELLOW}{bar_o}{Style.RESET_ALL}"
        peak_str = _format_large_number(peak, max_len=COL_PEAK-2)
        print(f"{Fore.CYAN}{str(base)+'^'+str(i):<{COL_EXP}}{Style.RESET_ALL}"
              f"{Fore.WHITE}{steps:<{COL_STEPS}}{Style.RESET_ALL}"
              f"{Fore.BLUE}{even:<{COL_EVEN}}{Style.RESET_ALL}"
              f"{Fore.YELLOW}{odd:<{COL_ODD}}{Style.RESET_ALL}"
              f"{Fore.LIGHTBLACK_EX}{pct:<{COL_PCT}.1%}{Style.RESET_ALL}"
              f"{dist_str}   "
              f"{Fore.LIGHTBLACK_EX}{peak_str:<{COL_PEAK}}{Style.RESET_ALL}"
              f"{Fore.MAGENTA}{ms:<{COL_MS}.3f}{Style.RESET_ALL}"
              f"{Fore.GREEN}✓{Style.RESET_ALL}")
        _write_log("TEST", f"{base}^{i} | steps={steps} even={even} odd={odd} pct={pct:.1%} peak={peak} ms={ms:.3f}")
        write_specific(f"{base}^{i}: steps={steps} even={even} odd={odd} pct={pct:.1%} peak={peak} ms={ms:.3f}")
    print(sep)
    log("INFO", f"Numbers tested : {counter}", Fore.CYAN)
    log("INFO", f"Total steps    : {tot_steps}", Fore.WHITE)
    log("INFO", f"Total even     : {tot_even}", Fore.BLUE)
    log("INFO", f"Total odd      : {tot_odd}", Fore.YELLOW)
    log("INFO", f"Max steps      : {max_steps}", Fore.MAGENTA)
    log("INFO", f"Absolute peak  : {_format_large_number(max_peak, 30)}", Fore.GREEN)
    write_specific("\n=== SUMMARY ===")
    write_specific(f"Numbers tested : {counter}")
    write_specific(f"Total steps    : {tot_steps}")
    write_specific(f"Total even     : {tot_even}")
    write_specific(f"Total odd      : {tot_odd}")
    write_specific(f"Max steps      : {max_steps}")
    write_specific(f"Absolute peak  : {max_peak}")
    write_specific(f"Test ended     : {datetime.now(tz_rome).strftime(FMT)}")
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")

def read_integer(prompt: str) -> int:
    while True:
        try:
            raw = input(prompt).strip().replace("_", "").replace(" ", "")
            if not raw: raise InvalidInputError("Empty input")
            return int(raw)
        except (ValueError, InvalidInputError):
            log("ERROR", "Invalid input: please enter an integer", Fore.RED)
        except KeyboardInterrupt:
            raise

def manual_mode():
    try: x = read_integer(Fore.CYAN + "Enter an integer > 0: " + Style.RESET_ALL)
    except KeyboardInterrupt: return
    if x <= 0: log("ERROR", f"Number must be > 0, got {x}", Fore.RED); return
    verbose = False
    if x > 10**4:
        try: verbose = input(Fore.CYAN + "Show all steps in console? (y/n, default n): " + Style.RESET_ALL).strip().lower() == 'y'
        except KeyboardInterrupt: return
    else:
        verbose = True
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_manual_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    def write_specific(line: str):
        try:
            with open(specific_log, "a", encoding="utf-8") as f: f.write(line + "\n")
        except (OSError, IOError):
            log("WARNING", f"Could not write to {specific_log}", Fore.YELLOW)
    write_specific(f"Manual calculation for n = {x} - started {datetime.now(tz_rome).strftime(FMT)}")
    log_writer = write_specific if verbose else None
    t0 = time.perf_counter()
    try:
        steps, even, odd, final, peak = collatz_fast(x, verbose=verbose, log_writer=log_writer)
    except CalculationError as e:
        log("FATAL ERROR", f"Calculation interrupted due to arithmetic error: {e}", Fore.RED); write_specific(f"FATAL ERROR: {e}"); return
    except InvalidInputError as e:
        log("INPUT ERROR", str(e), Fore.RED); write_specific(f"INPUT ERROR: {e}"); return
    except KeyboardInterrupt:
        log("INFO", "Calculation interrupted by user", Fore.YELLOW)
        write_specific("Calculation interrupted by user")
        return
    elapsed = time.perf_counter() - t0
    print("\n──────── RESULTS ────────\n")
    log("INFO", f"Total steps : {steps}", Fore.CYAN)
    log("INFO", f"Even steps  : {even}", Fore.BLUE)
    log("INFO", f"Odd steps   : {odd}", Fore.YELLOW)
    log("INFO", f"Final value : {final}", Fore.GREEN)
    log("INFO", f"Maximum peak: {peak}", Fore.MAGENTA)
    log("INFO", f"Elapsed time: {elapsed:.6f}s", Fore.GREEN)
    write_specific("\n=== RESULTS ===")
    write_specific(f"Total steps : {steps}")
    write_specific(f"Even steps  : {even}")
    write_specific(f"Odd steps   : {odd}")
    write_specific(f"Final value : {final}")
    write_specific(f"Maximum peak: {peak}")
    write_specific(f"Elapsed time: {elapsed:.6f} s")
    try:
        verify_counters(steps, even, odd)
        log("OK", "All counters verified successfully ✓", Fore.GREEN)
        write_specific("Counter verification: OK")
    except CalculationError as e:
        log("ERROR", f"Final verification failed: {e}", Fore.RED)
        write_specific(f"Counter verification failed: {e}")
    write_specific(f"Calculation ended: {datetime.now(tz_rome).strftime(FMT)}")
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")

def negative_mode():
    try:
        x = read_integer(Fore.CYAN + "Enter an integer (negative allowed, positive will be negated): " + Style.RESET_ALL)
    except KeyboardInterrupt:
        return
    if x == 0:
        log("ERROR", "0 is not valid for negative Collatz", Fore.RED)
        return
    # Se l'utente inserisce un numero positivo, lo trasformiamo automaticamente in negativo
    if x > 0:
        x = -x
        log("INFO", f"Positive input detected. Using {x} instead.", Fore.CYAN)
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_negative_{x}_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    def write_specific(line: str):
        try:
            with open(specific_log, "a", encoding="utf-8") as f: f.write(line + "\n")
        except (OSError, IOError):
            log("WARNING", f"Could not write to {specific_log}", Fore.YELLOW)
    write_specific(f"Negative calculation for n = {x} - started {datetime.now(tz_rome).strftime(FMT)}")
    write_specific("=== STEPS ===")
    try:
        collatz_negative(x, verbose=True, log_writer=write_specific)
    except CycleDetectedError as e:
        log("INFO", "CYCLE DETECTED", Fore.YELLOW)
        log("INFO", f"Re-entry node     : {e.node}", Fore.GREEN)
        log("INFO", f"Entry step        : {e.entry_step}", Fore.CYAN)
        log("INFO", f"Cycle length      : {e.length} steps", Fore.MAGENTA)
        _write_log("CYCLE", str(e))
        write_specific("\n=== CYCLE DETECTED ===")
        write_specific(f"Re-entry node     : {e.node}")
        write_specific(f"Entry step        : {e.entry_step}")
        write_specific(f"Cycle length      : {e.length}")
    except CalculationError as e:
        log("FATAL ERROR", f"Calculation interrupted due to arithmetic error: {e}", Fore.RED)
        _write_log("FATAL ERROR", str(e))
        write_specific(f"FATAL ERROR: {e}")
    except InvalidInputError as e:
        log("INPUT ERROR", str(e), Fore.RED)
        write_specific(f"INPUT ERROR: {e}")
    except KeyboardInterrupt:
        log("INFO", "Calculation interrupted by user", Fore.YELLOW)
        write_specific("Calculation interrupted by user")
    write_specific(f"Calculation ended: {datetime.now(tz_rome).strftime(FMT)}")
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")

def main():
    while True:
        clear_screen()
        print(Style.BRIGHT + Fore.MAGENTA + "╔" + "═" * 44 + "╗")
        print(Fore.MAGENTA + "║" + Fore.CYAN + Style.BRIGHT + "        COLLATZ CONJECTURE EXPLORER        " + Fore.MAGENTA + " ║")
        print(Fore.MAGENTA + "╠" + "═" * 44 + "╣")
        print(Fore.MAGENTA + "║" + Fore.YELLOW + "  1. Manual calculation                    " + Fore.MAGENTA + " ║")
        print(Fore.MAGENTA + "║" + Fore.YELLOW + "  2. Powers test                           " + Fore.MAGENTA + " ║")
        print(Fore.MAGENTA + "║" + Fore.YELLOW + "  3. Negative numbers (cycle detection)    " + Fore.MAGENTA + " ║")
        print(Fore.MAGENTA + "║" + Fore.YELLOW + "  q. Exit                                  " + Fore.MAGENTA + " ║")
        print(Fore.MAGENTA + "╚" + "═" * 44 + "╝" + Style.RESET_ALL)
        try:
            c = input(Fore.GREEN + Style.BRIGHT + "\n▶ Choice: " + Style.RESET_ALL).strip().lower()
        except KeyboardInterrupt:
            log("INFO", "User interrupt — exiting", Fore.CYAN)
            break
        if c == "q":
            log("INFO", "Exiting program", Fore.CYAN)
            print(Fore.MAGENTA + "\nThank you for using Collatz Explorer. Goodbye!\n" + Style.RESET_ALL)
            break
        elif c == "1":
            manual_mode()
            wait_for_enter()
        elif c == "2":
            clear_screen()
            test_powers()
            wait_for_enter()
        elif c == "3":
            clear_screen()
            negative_mode()
            wait_for_enter()
        else:
            log("ERROR", f"Invalid choice: '{c}'", Fore.RED)
            time.sleep(1)

if __name__ == "__main__":
    main()