import sys
sys.set_int_max_str_digits(0)
import os
import time
import multiprocessing
import traceback
import shutil
from datetime import datetime
from zoneinfo import ZoneInfo
from colorama import init, Fore, Style, Back
import platform

# ────────────────────────────────────────────────────────────────────────────────

init(autoreset=True)
tz_rome   = ZoneInfo("Europe/Rome")
FMT       = "%d/%m/%Y %H:%M:%S.%f"
LOGS_DIR      = "logs"
RESULTS_DIR   = os.path.join(LOGS_DIR, "results")
DEBUG_DIR     = os.path.join(LOGS_DIR, "debug")
_SESSION_TIMESTAMP = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
DEBUG_LOG_FILE = os.path.join(DEBUG_DIR, f"collatz_{_SESSION_TIMESTAMP}.log")
_PLATFORM = platform.system()
_CPU_COUNT = max(1, (os.cpu_count() or 1) - 1)

_PINK = "\033[38;5;213m"
_PINK_SOFT = "\033[38;5;218m"
_PINK_DARK = "\033[38;5;198m"
_CYAN = Fore.CYAN
_DIM = Style.DIM
_BOLD = Style.BRIGHT
_RST = Style.RESET_ALL
_BLACK_BG = Back.BLACK

for d in [LOGS_DIR, RESULTS_DIR, DEBUG_DIR]:
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass

# ────────────────────────────────────────────────────────────────────────────────

def _term_width() -> int:
    try:
        return max(40, shutil.get_terminal_size(fallback=(80, 24)).columns)
    except Exception:
        return 80
    
# ────────────────────────────────────────────────────────────────────────────────

def _box_width(min_width: int = 54, max_width: int = 100) -> int:
    width = _term_width() - 2
    return max(min_width, min(width, max_width))

# ────────────────────────────────────────────────────────────────────────────────

def _line(char: str = "─", width: int | None = None) -> str:
    if width is None:
        width = _box_width()
    return char * max(0, width)

# ────────────────────────────────────────────────────────────────────────────────

def _center(text: str, width: int | None = None) -> str:
    if width is None:
        width = _box_width()
    return text.center(width)

# ────────────────────────────────────────────────────────────────────────────────

def _fit(text: str, width: int | None = None) -> str:
    if width is None:
        width = _box_width()
    if len(text) <= width:
        return text
    if width <= 1:
        return text[:width]
    return text[: max(0, width - 1)] + "…"

# ────────────────────────────────────────────────────────────────────────────────

def _table_layout():
    width = _term_width()
    if width >= 140:
        return dict(exp=10, steps=11, even=10, odd=9, pct=9, dist=29, peak=30, ms=10, ok=5)
    if width >= 120:
        return dict(exp=9, steps=10, even=9, odd=8, pct=8, dist=24, peak=24, ms=9, ok=3)
    if width >= 100:
        return dict(exp=8, steps=9, even=8, odd=7, pct=7, dist=20, peak=18, ms=8, ok=3)
    return dict(exp=7, steps=8, even=7, odd=7, pct=6, dist=16, peak=14, ms=7, ok=3)

# ────────────────────────────────────────────────────────────────────────────────

class CalculationError(Exception): pass
class InvalidInputError(ValueError): pass
class CycleDetectedError(Exception):
    def __init__(self, node: int, entry_step: int, length: int):
        self.node = node
        self.entry_step = entry_step
        self.length = length
        super().__init__(f"Cycle detected: re-entry at {node} at step {entry_step}, length={length}")

# ────────────────────────────────────────────────────────────────────────────────

def _write_log(level: str, message: str, exc_info: bool = False):
    now = datetime.now(tz_rome).strftime(FMT)
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] [{level}] {message}\n")
            if exc_info:
                f.write(traceback.format_exc())
    except (OSError, IOError):
        pass

def _make_writer(path: str):
    try:
        f = open(path, "a", encoding="utf-8", buffering=1)
    except (OSError, IOError):
        def write_specific(line: str):
            return None
        return write_specific, None

    def write_specific(line: str):
        try:
            f.write(line + "\n")
        except (OSError, IOError):
            pass

    return write_specific, f

# ────────────────────────────────────────────────────────────────────────────────

def log(level: str, message: str, color=Fore.GREEN, exc_info: bool = False):
    now = datetime.now(tz_rome).strftime(FMT)
    print(
        f"{_BLACK_BG}{Fore.LIGHTBLACK_EX}[{_RST}{_PINK_SOFT}{now}{_RST}{Fore.LIGHTBLACK_EX}]{_RST} "
        f"{_BLACK_BG}{Fore.LIGHTBLACK_EX}[{_RST}{color}{level}{_RST}{Fore.LIGHTBLACK_EX}]{_RST} "
        f"{color}{message}{_RST}"
    )
    _write_log(level, message, exc_info)

# ────────────────────────────────────────────────────────────────────────────────

def clear_screen():
    try:
        print("\033[2J\033[H", end="")
    except Exception:
        os.system("cls" if os.name == "nt" else "clear")

# ────────────────────────────────────────────────────────────────────────────────

def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        try:
            import termios
            if sys.stdin.isatty():
                termios.tcflush(sys.stdin, termios.TCIOFLUSH)
        except Exception:
            pass

# ────────────────────────────────────────────────────────────────────────────────

def wait_for_enter(prompt="\nPress Enter to continue..."):
    flush_input()
    try:
        input(prompt)
    except (EOFError, KeyboardInterrupt):
        pass

# ────────────────────────────────────────────────────────────────────────────────

def send_notification(title: str, message: str):
    try:
        if _PLATFORM == "Windows":
            try:
                from plyer import notification
                notification.notify(title=title, message=message, app_name="Collatz Deep Drive", timeout=8)
                return
            except ImportError:
                pass
        elif _PLATFORM == "Darwin":
            safe_title   = title.replace("'", "\\'")
            safe_message = message.replace("'", "\\'")
            os.system(f"osascript -e 'display notification \"{safe_message}\" with title \"{safe_title}\"'")
        elif _PLATFORM == "Linux":
            safe_title   = title.replace('"', '\\"')
            safe_message = message.replace('"', '\\"')
            ret = os.system(f'notify-send "{safe_title}" "{safe_message}" 2>/dev/null')
            if ret != 0:
                os.system(f'zenity --info --title="{safe_title}" --text="{safe_message}" --timeout=8 2>/dev/null &')
    except Exception:
        pass

# ────────────────────────────────────────────────────────────────────────────────

def collatz_step(n: int) -> tuple[int, bool]:
    if n & 1 == 0:
        r = n >> 1
        if r << 1 != n:
            raise CalculationError(f"Reverse verification failed on {n}: expected {n}, got {r << 1}")
        return r, True
    r = (n << 1) + n + 1
    if r & 1 != 0:
        raise CalculationError(f"3*{n}+1 = {r} — expected even result, got odd")
    return r, False

# ────────────────────────────────────────────────────────────────────────────────

def collatz_step_fast(n: int) -> tuple[int, bool]:
    if n & 1 == 0:
        return n >> 1, True
    return (n << 1) + n + 1, False

# ────────────────────────────────────────────────────────────────────────────────

def verify_counters(steps: int, even: int, odd: int):
    if even < 0 or odd < 0:
        raise CalculationError(f"Negative counter — even={even}, odd={odd}")
    if even + odd != steps:
        raise CalculationError(f"Incorrect counter sum — even({even}) + odd({odd}) = {even + odd}, expected {steps}")

# ────────────────────────────────────────────────────────────────────────────────

def collatz(n: int, verbose: bool = True, delay: float = 0.0, log_writer=None, progress_callback=None):
    if not isinstance(n, int) or n <= 0:
        raise InvalidInputError(f"Invalid input: expected integer > 0, got {n!r}")
    steps = even = odd = 0
    peak = n
    pc = progress_callback
    lw = log_writer
    if verbose:
        log("INFO", f"Starting Collatz with n = {n}", Fore.CYAN)
    while n > 1:
        old = n
        try:
            n, is_even = collatz_step(n)
        except CalculationError as e:
            log("CALCULATION ERROR", str(e), Fore.RED, exc_info=True)
            raise
        if n > peak:
            peak = n
        if is_even:
            even += 1
        else:
            odd += 1
        steps += 1
        try:
            verify_counters(steps, even, odd)
        except CalculationError as e:
            log("COUNTER ERROR", str(e), Fore.RED, exc_info=True)
            raise
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.CYAN}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙ {Fore.GREEN}{n}{Style.RESET_ALL}")
            if delay > 0:
                time.sleep(delay)
        if lw:
            try:
                lw(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception:
                pass
        if pc:
            try:
                pc(steps, even, odd, n, peak)
            except Exception:
                pass
    return steps, even, odd, n, peak

# ────────────────────────────────────────────────────────────────────────────────

def collatz_fast(n: int, verbose: bool = True, log_writer=None, progress_callback=None):
    steps = even = odd = 0
    peak = n
    pc = progress_callback
    lw = log_writer
    while n > 1:
        old = n
        n, is_even = collatz_step_fast(n)
        if n > peak:
            peak = n
        if is_even:
            even += 1
        else:
            odd += 1
        steps += 1
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.CYAN}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙  {Fore.GREEN}{n}{Style.RESET_ALL}")
        if lw:
            try:
                lw(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception:
                pass
        if pc:
            try:
                pc(steps, even, odd, n, peak)
            except Exception:
                pass
    return steps, even, odd, n, peak

# ────────────────────────────────────────────────────────────────────────────────

def collatz_superfast(n: int, progress_callback=None, log_writer=None):
    steps = even = odd = 0
    peak = n
    pc = progress_callback
    while n > 1:
        if n & 1 == 0:
            tz = (n & -n).bit_length() - 1
            n >>= tz
            even += tz
            steps += tz
        else:
            n = n + (n << 1) + 1
            odd += 1
            steps += 1
        if n > peak:
            peak = n
        if pc:
            try:
                pc(steps, even, odd, n, peak)
            except Exception:
                pass
    return steps, even, odd, n, peak

# ────────────────────────────────────────────────────────────────────────────────

def _collatz_superfast_pure(n: int) -> tuple[int, int, int, int, int]:
    steps = even = odd = 0
    peak = n
    while n > 1:
        if n & 1 == 0:
            tz = (n & -n).bit_length() - 1
            n >>= tz
            even += tz
            steps += tz
        else:
            n = n + (n << 1) + 1
            odd += 1
            steps += 1
        if n > peak:
            peak = n
    return steps, even, odd, n, peak

# ────────────────────────────────────────────────────────────────────────────────

def _worker_power(args):
    i, n = args
    t0 = time.perf_counter()
    try:
        steps, even, odd, final, peak = _collatz_superfast_pure(n)
    except KeyboardInterrupt:
        return i, None, None, None, None, None, "INTERRUPTED"
    except Exception as e:
        return i, 0, 0, 0, 0, 0, f"{type(e).__name__}: {e}"
    ms = (time.perf_counter() - t0) * 1000
    return i, steps, even, odd, final, peak, ms

# ────────────────────────────────────────────────────────────────────────────────

def collatz_step_negative(n: int) -> tuple[int, bool]:
    if n & 1 == 0:
        r = n >> 1
        if n >= 0 and n - (n >> 1) != r:
            raise CalculationError(f"Mismatch in negative even step on {n}: expected {r}")
        return r, True
    r = (n << 1) + n + 1
    if r != 3 * n + 1:
        raise CalculationError(f"Mismatch in negative odd step on {n}: expected {3 * n + 1}, got {r}")
    return r, False

# ────────────────────────────────────────────────────────────────────────────────

def collatz_negative(n: int, verbose: bool = True, log_writer=None):
    if n == 0:
        raise InvalidInputError("0 is not a valid input for negative Collatz")
    seen = {}
    steps = 0
    log("INFO", f"Starting NEGATIVE Collatz with n = {n}", Fore.MAGENTA)
    lw = log_writer
    while n not in seen:
        seen[n] = steps
        old = n
        try:
            n, is_even = collatz_step_negative(n)
        except CalculationError as e:
            log("CALCULATION ERROR", str(e), Fore.RED, exc_info=True)
            raise
        steps += 1
        if verbose:
            step_type = f"{Fore.BLUE}E{Style.RESET_ALL}" if is_even else f"{Fore.YELLOW}O{Style.RESET_ALL}"
            print(f"{Fore.MAGENTA}{steps:04d}{Style.RESET_ALL} [{step_type}] {Fore.WHITE}{old}{Style.RESET_ALL} ➙  {Fore.YELLOW}{n}{Style.RESET_ALL}")
        if lw:
            try:
                lw(f"{steps:04d} [E] {old} / 2 = {n}" if is_even else f"{steps:04d} [O] 3*{old}+1 = {n}")
            except Exception:
                pass
    entry_step = seen[n]
    length = steps - entry_step
    raise CycleDetectedError(n, entry_step, length)

# ────────────────────────────────────────────────────────────────────────────────

def _bar(value: int, total: int, width: int = 12) -> str:
    filled = round(value / total * width) if total else 0
    filled = max(0, min(filled, width))
    return "█" * filled + "░" * (width - filled)

# ────────────────────────────────────────────────────────────────────────────────

def _format_large_number(n: int, max_len: int = 20) -> str:
    s = str(n)
    if len(s) <= max_len:
        return s
    exp = len(s) - 1
    return f"{s[0]}.{s[1:4]}e+{exp}"

# ────────────────────────────────────────────────────────────────────────────────

def reset_logs():
    try:
        if os.path.exists(LOGS_DIR):
            shutil.rmtree(LOGS_DIR)
        for d in [LOGS_DIR, RESULTS_DIR, DEBUG_DIR]:
            os.makedirs(d, exist_ok=True)
        log("INFO", "All log files have been deleted and directories recreated.", Fore.CYAN)
    except Exception as e:
        log("ERROR", f"Failed to reset logs: {e}", Fore.RED, exc_info=True)

# ────────────────────────────────────────────────────────────────────────────────

def test_powers():
    base = 2
    while True:
        try:
            raw = input(Fore.CYAN + "Enter the base for the powers test (integer >= 2, default 2): " + Style.RESET_ALL).strip()
            if not raw:
                base = 2
                break
            raw = raw.replace("_", "").replace(" ", "")
            base = int(raw)
            if base < 2:
                print(f"{Fore.RED}Base must be >= 2.{Style.RESET_ALL}")
                continue
            break
        except ValueError:
            print(f"{Fore.RED}Invalid input. Please enter an integer.{Style.RESET_ALL}")
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

    use_parallel = False
    if _CPU_COUNT > 1:
        try:
            resp_par = input(Fore.CYAN + f"Use parallel computation ({_CPU_COUNT} CPU cores)? (y/n, default n): " + Style.RESET_ALL).strip().lower()
            use_parallel = (resp_par == 'y')
        except KeyboardInterrupt:
            log("INFO", "Test cancelled", Fore.YELLOW)
            return

    BATCH = max(2, _CPU_COUNT * 2) if use_parallel else 1

    log("INFO", f"POWERS TEST OF {base} — start (parallel={use_parallel}, cores={_CPU_COUNT})", Fore.MAGENTA)
    layout = _table_layout()
    COL_EXP = layout["exp"]
    COL_STEPS = layout["steps"]
    COL_EVEN = layout["even"]
    COL_ODD = layout["odd"]
    COL_PCT = layout["pct"]
    COL_PEAK = layout["peak"]
    COL_MS = layout["ms"]
    COL_OK = layout["ok"]
    COL_DIST = layout["dist"]
    TOT = COL_EXP + COL_STEPS + COL_EVEN + COL_ODD + COL_PCT + COL_DIST + COL_PEAK + COL_MS + COL_OK
    sep = Fore.LIGHTBLACK_EX + "─" * TOT + Style.RESET_ALL
    header = (f"{Fore.LIGHTBLACK_EX}{'EXP':<{COL_EXP}}{'STEPS':<{COL_STEPS}}{'EVEN':<{COL_EVEN}}{'ODD':<{COL_ODD}}{'%EVEN':<{COL_PCT}}"
              f"{'DIST EVEN(blue)░ ODD(yellow)█':<{COL_DIST}}{'PEAK':<{COL_PEAK}}{'ms':<{COL_MS}}{'OK':<{COL_OK}}{Style.RESET_ALL}")
    print(f"\n{sep}\n{header}\n{sep}")
    tot_steps = tot_even = tot_odd = max_steps = max_peak = counter = 0
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_powers_{base}_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    write_specific, specific_handle = _make_writer(specific_log)
    write_specific(f"Powers test of {base} - started {datetime.now(tz_rome).strftime(FMT)}")
    write_specific("")

    interrupted = False

    def handle_anomaly(idx: int, final: int, steps: int, odd: int) -> bool:
        nonlocal interrupted
        log("ERROR", f"{base}^{idx} — unexpected result: final={final}, steps={steps}, odd={odd}", Fore.RED)
        _write_log("ERROR", f"{base}^{idx} | final={final} steps={steps} odd={odd}")
        write_specific(f"ANOMALY {base}^{idx}: final={final} steps={steps} odd={odd}")
        print(f"\n{Fore.RED}{'─'*60}{Style.RESET_ALL}\n  {Fore.RED}ANOMALY DETECTED{Style.RESET_ALL} — {base}^{idx}\n"
              f"  Final value    : {Fore.RED}{final}{Style.RESET_ALL}  (expected 1)\n"
              f"  Total steps    : {steps}  (expected {idx})\n  Odd steps      : {odd}  (expected 0)\n"
              f"{Fore.RED}{'─'*60}{Style.RESET_ALL}\n")
        if auto_yes:
            print(f"  {Fore.YELLOW}Automatic continuation...{Style.RESET_ALL}")
            choice = "y"
        else:
            while True:
                try:
                    choice = input(f"  {Fore.YELLOW}Continue test? [{Fore.GREEN}y{Fore.YELLOW}/{Fore.RED}n{Fore.YELLOW}]: {Style.RESET_ALL}").strip().lower()
                except KeyboardInterrupt:
                    choice = "n"
                if choice in ("y", "yes"):
                    log("INFO", f"Continuation requested after anomaly on {base}^{idx}", Fore.YELLOW)
                    _write_log("INFO", f"User chose to continue after anomaly on {base}^{idx}")
                    write_specific(f"User chose to continue after anomaly on {base}^{idx}")
                    break
                elif choice in ("n", "no"):
                    log("INFO", f"Test interrupted by user at power {base}^{idx}", Fore.RED)
                    _write_log("INFO", f"User interrupted test at power {base}^{idx}")
                    write_specific(f"Test interrupted by user at power {base}^{idx}")
                    print()
                    break
                else:
                    print(f"  {Fore.RED}Invalid response.{Style.RESET_ALL}")
        if choice in ("n", "no"):
            interrupted = True
            return False
        return True

    def emit_row(idx: int, steps: int, even: int, odd: int, peak: int, ms: float):
        pct = even / steps if steps else 0
        term_w = _term_width()
        compact = term_w < 100
        bar_w = 8 if term_w < 110 else 12
        if compact:
            peak_str = _format_large_number(peak, max_len=max(8, term_w - 60))
            print(f"{Fore.CYAN}{str(base)+'^'+str(idx):<10}{Style.RESET_ALL} "
                  f"{Fore.WHITE}s={steps:<7}{Style.RESET_ALL} "
                  f"{Fore.BLUE}e={even:<6}{Style.RESET_ALL} "
                  f"{Fore.YELLOW}o={odd:<6}{Style.RESET_ALL} "
                  f"{Fore.LIGHTBLACK_EX}{pct:<6.1%}{Style.RESET_ALL} "
                  f"{Fore.LIGHTBLACK_EX}p={peak_str}{Style.RESET_ALL} "
                  f"{Fore.MAGENTA}{ms:<7.3f}{Style.RESET_ALL} "
                  f"{Fore.GREEN}✓{Style.RESET_ALL}")
        else:
            bar_e = _bar(even, steps, bar_w)
            bar_o = _bar(odd, steps, bar_w)
            dist_str = f"{Fore.BLUE}{bar_e}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}│{Style.RESET_ALL}{Fore.YELLOW}{bar_o}{Style.RESET_ALL}"
            peak_str = _format_large_number(peak, max_len=max(8, COL_PEAK - 2))
            print(f"{Fore.CYAN}{str(base)+'^'+str(idx):<{COL_EXP}}{Style.RESET_ALL}"
                  f"{Fore.WHITE}{steps:<{COL_STEPS}}{Style.RESET_ALL}"
                  f"{Fore.BLUE}{even:<{COL_EVEN}}{Style.RESET_ALL}"
                  f"{Fore.YELLOW}{odd:<{COL_ODD}}{Style.RESET_ALL}"
                  f"{Fore.LIGHTBLACK_EX}{pct:<{COL_PCT}.1%}{Style.RESET_ALL}"
                  f"{dist_str}   "
                  f"{Fore.LIGHTBLACK_EX}{peak_str:<{COL_PEAK}}{Style.RESET_ALL}"
                  f"{Fore.MAGENTA}{ms:<{COL_MS}.3f}{Style.RESET_ALL}"
                  f"{Fore.GREEN}✓{Style.RESET_ALL}")
        _write_log("TEST", f"{base}^{idx} | steps={steps} even={even} odd={odd} pct={pct:.1%} peak={peak} ms={ms:.3f}")
        write_specific(f"{base}^{idx}: steps={steps} even={even} odd={odd} pct={pct:.1%} peak={peak} ms={ms:.3f}")

    def process_result(idx: int, steps: int, even: int, odd: int, final: int, peak: int, ms: float) -> bool:
        nonlocal tot_steps, tot_even, tot_odd, max_steps, max_peak, counter
        ok = (final == 1 and steps == idx and odd == 0) if verify_conditions else True
        tot_steps += steps
        tot_even += even
        tot_odd += odd
        if steps > max_steps:
            max_steps = steps
        if peak > max_peak:
            max_peak = peak
        counter += 1
        if not ok and not handle_anomaly(idx, final, steps, odd):
            return False
        emit_row(idx, steps, even, odd, peak, ms)
        return True

    if use_parallel:
        pool = None
        try:
            pool = multiprocessing.Pool(processes=_CPU_COUNT, maxtasksperchild=200)
        except Exception as e:
            log("WARNING", f"Could not create process pool ({e}). Falling back to sequential.", Fore.YELLOW)
            use_parallel = False

    if use_parallel:
        i = 1
        current_n = base
        try:
            while True:
                batch_args = []
                for _ in range(BATCH):
                    batch_args.append((i, current_n))
                    current_n *= base
                    i += 1
                try:
                    results = pool.map(_worker_power, batch_args, chunksize=1)
                except KeyboardInterrupt:
                    log("INFO", "Test interrupted by user", Fore.YELLOW)
                    pool.terminate()
                    pool.join()
                    interrupted = True
                    break
                except Exception as e:
                    log("ERROR", f"Unexpected error in parallel execution: {e}", Fore.RED, exc_info=True)
                    pool.terminate()
                    pool.join()
                    interrupted = True
                    break
                for res in results:
                    if len(res) == 7 and isinstance(res[6], str):
                        idx, steps, even, odd, final, peak, err_msg = res
                        if err_msg == "INTERRUPTED":
                            log("INFO", "Worker interrupted by user", Fore.YELLOW)
                            interrupted = True
                            break
                        if err_msg:
                            log("ERROR", f"{base}^{idx} - worker error: {err_msg}", Fore.RED)
                            continue
                    else:
                        idx, steps, even, odd, final, peak, ms = res
                    if not process_result(idx, steps, even, odd, final, peak, ms):
                        interrupted = True
                        break
                if interrupted:
                    break
        finally:
            if 'pool' in locals() and pool is not None:
                try:
                    if interrupted:
                        pool.terminate()
                    else:
                        pool.close()
                finally:
                    pool.join()
    else:
        current_n = base
        for i in range(1, 1_000_000_000):
            n_orig = current_n
            current_n *= base
            t0 = time.perf_counter()
            try:
                steps, even, odd, final, peak = collatz_superfast(n_orig)
            except KeyboardInterrupt:
                log("INFO", "Test interrupted by user", Fore.YELLOW)
                break
            except Exception as e:
                log("FATAL ERROR", f"{base}^{i}: {e}", Fore.RED, exc_info=True)
                write_specific(f"FATAL ERROR {base}^{i}: {e}")
                log("INFO", f"Test interrupted at power {base}^{i}", Fore.RED)
                break
            ms = (time.perf_counter() - t0) * 1000
            if not process_result(i, steps, even, odd, final, peak, ms):
                break

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
    if specific_handle is not None:
        try:
            specific_handle.close()
        except Exception:
            pass
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")
    send_notification(
        "Collatz Deep Drive",
        f"Powers test of {base} complete — {counter} numbers tested, max steps: {max_steps}"
    )

# ────────────────────────────────────────────────────────────────────────────────

def read_integer(prompt: str) -> int:
    while True:
        try:
            raw = input(prompt).strip().replace("_", "").replace(" ", "")
            if not raw:
                raise InvalidInputError("Empty input")
            return int(raw)
        except (ValueError, InvalidInputError) as e:
            log("ERROR", f"Invalid input: {e}", Fore.RED)
        except KeyboardInterrupt:
            raise

# ────────────────────────────────────────────────────────────────────────────────

def manual_mode():
    try:
        x = read_integer(Fore.CYAN + "Enter an integer > 0: " + Style.RESET_ALL)
    except KeyboardInterrupt:
        return
    if x <= 0:
        log("ERROR", f"Number must be > 0, got {x}", Fore.RED)
        return
    verbose = False
    if x > 10**4:
        try:
            verbose = input(Fore.CYAN + "Show all steps in console? (y/n, default n): " + Style.RESET_ALL).strip().lower() == 'y'
        except KeyboardInterrupt:
            return
    else:
        verbose = True
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_manual_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    write_specific, specific_handle = _make_writer(specific_log)
    write_specific(f"Manual calculation for n = {x} - started {datetime.now(tz_rome).strftime(FMT)}")
    log_writer = write_specific if verbose else None
    t0 = time.perf_counter()
    try:
        steps, even, odd, final, peak = collatz_fast(x, verbose=verbose, log_writer=log_writer)
    except CalculationError as e:
        log("FATAL ERROR", f"Calculation interrupted due to arithmetic error: {e}", Fore.RED, exc_info=True)
        write_specific(f"FATAL ERROR: {e}")
        return
    except InvalidInputError as e:
        log("INPUT ERROR", str(e), Fore.RED)
        write_specific(f"INPUT ERROR: {e}")
        return
    except KeyboardInterrupt:
        log("INFO", "Calculation interrupted by user", Fore.YELLOW)
        write_specific("Calculation interrupted by user")
        return
    except Exception as e:
        log("UNEXPECTED ERROR", f"{type(e).__name__}: {e}", Fore.RED, exc_info=True)
        write_specific(f"UNEXPECTED ERROR: {e}")
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
    if specific_handle is not None:
        try:
            specific_handle.close()
        except Exception:
            pass
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")
    send_notification(
        "Collatz Deep Drive",
        f"Manual calculation done — n={x}  steps={steps}  peak={_format_large_number(peak, 20)}  time={elapsed:.3f}s"
    )

# ────────────────────────────────────────────────────────────────────────────────

def negative_mode():
    try:
        x = read_integer(Fore.CYAN + "Enter an integer (negative allowed, positive will be negated): " + Style.RESET_ALL)
    except KeyboardInterrupt:
        return
    if x == 0:
        log("ERROR", "0 is not valid for negative Collatz", Fore.RED)
        return
    if x > 0:
        x = -x
        log("INFO", f"Positive input detected. Using {x} instead.", Fore.CYAN)
    timestamp = datetime.now(tz_rome).strftime("%Y%m%d_%H%M%S")
    specific_log = os.path.join(RESULTS_DIR, f"collatz_negative_{x}_{timestamp}.txt")
    specific_log_path = os.path.abspath(specific_log)
    write_specific, specific_handle = _make_writer(specific_log)
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
        send_notification(
            "Collatz Deep Drive",
            f"Negative Collatz — cycle detected at node {e.node}, length {e.length} steps"
        )
    except CalculationError as e:
        log("FATAL ERROR", f"Calculation interrupted due to arithmetic error: {e}", Fore.RED, exc_info=True)
        write_specific(f"FATAL ERROR: {e}")
    except InvalidInputError as e:
        log("INPUT ERROR", str(e), Fore.RED)
        write_specific(f"INPUT ERROR: {e}")
    except KeyboardInterrupt:
        log("INFO", "Calculation interrupted by user", Fore.YELLOW)
        write_specific("Calculation interrupted by user")
    except Exception as e:
        log("UNEXPECTED ERROR", f"{type(e).__name__}: {e}", Fore.RED, exc_info=True)
        write_specific(f"UNEXPECTED ERROR: {e}")
    write_specific(f"Calculation ended: {datetime.now(tz_rome).strftime(FMT)}")
    if specific_handle is not None:
        try:
            specific_handle.close()
        except Exception:
            pass
    log("INFO", f"Detailed log saved to: {specific_log_path}", Fore.CYAN)
    print(f"{Fore.CYAN}→ Log file path: {specific_log_path}{Style.RESET_ALL}")

# ────────────────────────────────────────────────────────────────────────────────

def show_credits():
    clear_screen()
    width = _box_width(54, 96)
    print()
    print(f"{_BOLD}{_PINK_DARK}{'=' * width}{_RST}")
    print(f"{_BOLD}{_PINK_SOFT}{_center('CREDITS', width)}{_RST}")
    print(f"{_BOLD}{_PINK_DARK}{'=' * width}{_RST}")
    print()
    print(f"{_CYAN}importsys{_RST} – part of the code, idea, design, etc.")
    print(f"{_CYAN}DeepSeek & ChatGPT{_RST} – help in code and README.md writing,")
    print(f"                    specifically grammar correction.")
    print()
    print(f"{_BOLD}{_PINK_DARK}{'=' * width}{_RST}")
    print()
    wait_for_enter()

# ────────────────────────────────────────────────────────────────────────────────

def draw_menu():
    clear_screen()
    width = _box_width(58, 96)
    print()
    print(f"{_BLACK_BG}{_BOLD}{_PINK_DARK}{'═' * width}{_RST}")
    print(f"{_BLACK_BG}{_BOLD}{_PINK_SOFT}{_center('COLLATZ DEEP DRIVE v2.0', width)}{_RST}")
    print(f"{_BLACK_BG}{_DIM}{_center(f'{_PLATFORM} · {_CPU_COUNT} cores · window {_term_width()} cols', width)}{_RST}")
    print(f"{_BLACK_BG}{_BOLD}{_PINK_DARK}{'═' * width}{_RST}")
    print()
    print(f"  {_PINK_SOFT}1{_RST}. Manual calculation")
    print(f"     {_DIM}Single input, counter verification, and full trace.{_RST}")
    print(f"  {_PINK_SOFT}2{_RST}. Powers test")
    print(f"     {_DIM}Sequential or parallel batch test on powers of a base.{_RST}")
    print(f"  {_PINK_SOFT}3{_RST}. Negative numbers")
    print(f"     {_DIM}Cycle detection on the negative Collatz variant.{_RST}")
    print(f"  {_PINK_SOFT}c{_RST}. Reset all logs")
    print(f"     {_DIM}Deletes every log file and recreates the folders.{_RST}")
    print(f"  {_PINK_SOFT}credits{_RST}. Show credits")
    print()
    print(f"  {_DIM}q{_RST}. Exit")
    print()
    print(f"{_BLACK_BG}{_BOLD}{_PINK_DARK}{'═' * width}{_RST}")
    print()

# ────────────────────────────────────────────────────────────────────────────────

def main():
    while True:
        draw_menu()
        try:
            c = input(f"{_BOLD}{_PINK_SOFT}▶ Choice: {_RST}").strip().lower()
        except KeyboardInterrupt:
            log("INFO", "User interrupt — exiting", Fore.CYAN)
            break
        if c == "q":
            log("INFO", "Exiting program", Fore.CYAN)
            print(f"{_PINK_SOFT}\nThank you for using Collatz Deep Drive. Goodbye!\n{_RST}")
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
        elif c == "c":
            clear_screen()
            confirm = input(f"{Fore.YELLOW}Are you sure you want to delete all log files? (y/n): {Style.RESET_ALL}").strip().lower()
            if confirm == 'y':
                reset_logs()
            else:
                log("INFO", "Log reset cancelled.", Fore.CYAN)
            wait_for_enter()
        elif c == "credits":
            show_credits()
        else:
            log("ERROR", f"Invalid choice: '{c}'", Fore.RED)
            time.sleep(1)
            
# ────────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()

# ────────────────────────────────────────────────────────────────────────────────
