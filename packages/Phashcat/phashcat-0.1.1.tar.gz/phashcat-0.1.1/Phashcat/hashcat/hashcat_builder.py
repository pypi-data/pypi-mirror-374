# hashcat_builder.py — Monoid-style fluent builder for Hashcat commands
# Place under: Phashcat/hashcat/hashcat_builder.py

"""
HashcatBuilder — a Monoid-style Fluent Command Builder
=====================================================

This module exposes an immutable, chainable builder to assemble Hashcat
commands using readable methods instead of raw strings. It relies on the
constants and value schema from `hashcat_flags.py`.

Design goals
------------
- **Immutability**: each method returns a *new* builder (functional style).
- **Monoid**: `empty()` is the identity; use `.mappend()` to combine builders.
- **Validation**: light type-checks using `VALUE_KIND` (numeric/boolean/…).
- **Ergonomics**: human-friendly shortcuts: `.hash_type(0)`, `.attack_mode(3)`, etc.
- **Safety**: `.value()` returns a list (ready for `subprocess.run`).

Example
-------
    from hashcat.hashcat_builder import hashcat

    cmd = (
        hashcat("example0.hash", "?d?d?d?d?d?d")
        .hash_type(0)
        .attack_mode(3)
        .outfile("cracked.txt")
        .status(True)
        .value()
    )
    # subprocess.run(cmd, check=True)

Public API
----------
- class `HashcatBuilder`
  - `.empty()`                      → identity builder
  - `.mappend(other)`               → combine two builders (right-biased)
  - `.set(flag, value=True)`        → low-level setter for any long-form flag
  - `.unset(flag)`                  → remove a flag
  - `.arg(*args)`                   → append positional arguments
  - Rich fluent methods for common flags (see below)
  - `.value()` / `.cmdline()` / `.run(...)`

- function `hashcat(*positionals, binary=None)` → convenience factory.
"""

from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Dict, List, Any, Optional
import subprocess
import shlex

# Import flags & schema from the sibling module
from .hashcat_flags import (
    HC,
    VALUE_KIND,
    # Common flags (re-export or add more as you like)
    HASH_TYPE, ATTACK_MODE, OUTFILE, STATUS, STATUS_TIMER, WORKLOAD_PROFILE,
    MARKOV_THRESHOLD, SESSION, RUNTIME, SKIP, LIMIT,
    RULES_FILE, RULE_LEFT, RULE_RIGHT, GENERATE_RULES,
    INCREMENT, INCREMENT_MIN, INCREMENT_MAX, SLOW_CANDIDATES,
    CUSTOM_CHARSET1, CUSTOM_CHARSET2, CUSTOM_CHARSET3, CUSTOM_CHARSET4,
    CUSTOM_CHARSET5, CUSTOM_CHARSET6, CUSTOM_CHARSET7, CUSTOM_CHARSET8,
    ENCODING_FROM, ENCODING_TO, POTFILE_PATH, POTFILE_DISABLE,
    BACKEND_DEVICES, OPENCL_DEVICE_TYPES, BACKEND_INFO,
    BENCHMARK, BENCHMARK_ALL, BENCHMARK_MIN, BENCHMARK_MAX,
    CPU_AFFINITY, HOOK_THREADS, KERNEL_ACCEL, KERNEL_LOOPS, KERNEL_THREADS,
    BACKEND_VECTOR_WIDTH, OPTIMIZED_KERNEL_ENABLE, MULTIPLY_ACCEL_DISABLE,
    BRAIN_CLIENT, BRAIN_SERVER, BRAIN_HOST, BRAIN_PORT, BRAIN_PASSWORD,
    COLOR_CRACKED, QUIET, FORCE, SHOW, LEFT, STDOUT,
)

Kind = Optional[str]  # VALUE_KIND values: "Num", "Str", None (boolean), etc.


def _validate(flag: str, val: Any) -> None:
    """
    Validate a value against `VALUE_KIND`.

    Parameters
    ----------
    flag : str
        Long-form flag (e.g., '--status', '--hash-type').

    val : Any
        The value to validate; booleans for switches, numeric for 'Num', etc.

    Raises
    ------
    TypeError
        If the value does not match the expected kind (best-effort check).
    """
    kind: Kind = VALUE_KIND.get(flag)
    if kind is None:
        # boolean switch
        if val not in (True, False, None):
            raise TypeError(f"{flag} is a boolean switch; got {type(val).__name__}")
        return

    # for valued flags, None is not a valid value
    if val is None:
        raise TypeError(f"{flag} expects {kind}; got None")

    if kind == "Num":
        # Accept int/float but not bool (bool is subclass of int)
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise TypeError(f"{flag} expects a number; got {type(val).__name__}")
    else:
        # 'Str', 'File', 'Dir', 'Char', 'Code', 'Hex', 'Rule', 'CS', 'Port'
        # Accept any str-able value; semantic correctness left to caller.
        pass


def _normalize(flag: str, val: Any) -> Optional[str | int | float | bool]:
    """
    Normalize a value for CLI emission.

    Returns
    -------
    None | bool | (str|int|float)
      - For boolean flags: True means include the flag, False/None omit it.
      - For valued flags: the stringified value.
    """
    kind = VALUE_KIND.get(flag)
    if kind is None:
        return True if val else None
    return val


@dataclass(frozen=True)
class HashcatBuilder:
    """
    Immutable, chainable builder for Hashcat commands.

    The builder stores a mapping of options (long-form flags) and a list of
    positional arguments. Each mutating method returns a **new** instance.

    Parameters
    ----------
    binary : str
        Hashcat binary to call (default: from `hashcat_flags.HC`).
        The package-level `hashcat()` factory resolves a better default.

    _opts : dict[str, Any]
        Internal options mapping. Use `.set()` or fluent methods to modify.

    _positionals : list[str]
        Positional arguments: typically [hash|hashfile|hccapxfile, dict|mask|dir...].

    Monoid Semantics
    ----------------
    - `HashcatBuilder.empty()` is the identity element.
    - `.mappend(other)` combines two builders (right-biased option override).
    - Associativity holds: (a⊕b)⊕c == a⊕(b⊕c)

    Example
    -------
        base = HashcatBuilder.empty().hash_type(0)
        brute = HashcatBuilder.empty().attack_mode(3)
        combined = base.mappend(brute).outfile("out.txt")
    """
    binary: str = HC
    _opts: Dict[str, Any] = None
    _positionals: List[str] = None

    def __post_init__(self):
        object.__setattr__(self, "_opts", dict(self._opts or {}))
        object.__setattr__(self, "_positionals", list(self._positionals or []))

    def _is_empty(self) -> bool:
        return not self._opts and not self._positionals

    # ---------------------------------------------------------------------
    # Monoid operations
    # ---------------------------------------------------------------------
    @classmethod
    def empty(cls, *, binary: str = HC) -> "HashcatBuilder":
        """
        Identity builder with no options and no positionals.

        Parameters
        ----------
        binary : str
            Hashcat binary path/name.

        Returns
        -------
        HashcatBuilder
        """
        return cls(binary=binary, _opts={}, _positionals=[])

    def mappend(self, other: "HashcatBuilder") -> "HashcatBuilder":
        """
        Combine two builders (right-biased).

        Options from `other` override same-named options in `self`.
        Positionals are concatenated in order.

        Parameters
        ----------
        other : HashcatBuilder

        Returns
        -------
        HashcatBuilder
        """
        merged_opts = {**self._opts, **other._opts}
        merged_pos = self._positionals + list(other._positionals)

        if self._is_empty() and not other._is_empty():
            new_binary = other.binary
        elif other._is_empty():
            new_binary = self.binary
        else:
            new_binary = self.binary  # deterministic choice

        return HashcatBuilder(binary=new_binary, _opts=merged_opts, _positionals=merged_pos)

    # ---------------------------------------------------------------------
    # Low-level API (generic controls)
    # ---------------------------------------------------------------------
    def set(self, flag: str, value: Any = True) -> "HashcatBuilder":
        """
        Set a long-form flag.

        Parameters
        ----------
        flag : str
            Long-form option (e.g., '--status', '--outfile').

        value : Any, default True
            - For boolean flags: True/False.
            - For valued flags: a value coerced to string on emission.

        Returns
        -------
        HashcatBuilder
        """
        _validate(flag, value)
        new_opts = dict(self._opts)
        new_opts[flag] = value
        return replace(self, _opts=new_opts)

    def unset(self, flag: str) -> "HashcatBuilder":
        """
        Remove a flag if present.

        Parameters
        ----------
        flag : str

        Returns
        -------
        HashcatBuilder
        """
        new_opts = dict(self._opts)
        new_opts.pop(flag, None)
        return replace(self, _opts=new_opts)

    def arg(self, *args: str) -> "HashcatBuilder":
        """
        Append positional arguments.

        Parameters
        ----------
        *args : str
            e.g., ["example0.hash", "example.dict"] or ["example0.hash", "?d?d..."]

        Returns
        -------
        HashcatBuilder
        """
        return replace(self, _positionals=self._positionals + list(args))

    # ---------------------------------------------------------------------
    # Fluent API (ergonomic shorthands for common flags)
    # Each method returns a NEW builder (immutability).
    # ---------------------------------------------------------------------
    def hash_type(self, num: int) -> "HashcatBuilder":
        """Select hash mode. Example: `.hash_type(0)` for MD5."""
        return self.set(HASH_TYPE, num)

    def attack_mode(self, num: int) -> "HashcatBuilder":
        """Select attack mode. Example: `.attack_mode(3)` for brute-force."""
        return self.set(ATTACK_MODE, num)

    def outfile(self, path: str) -> "HashcatBuilder":
        """Write cracked results to a file."""
        return self.set(OUTFILE, path)

    def status(self, on: bool = True) -> "HashcatBuilder":
        """Enable/disable status updates (boolean switch)."""
        return self.set(STATUS, on)

    def status_timer(self, seconds: int) -> "HashcatBuilder":
        """Seconds between status updates."""
        return self.set(STATUS_TIMER, seconds)

    def workload_profile(self, w: int) -> "HashcatBuilder":
        """Set workload profile (1..4)."""
        return self.set(WORKLOAD_PROFILE, w)

    def markov_threshold(self, x: int) -> "HashcatBuilder":
        """Stop accepting new markov-chains at threshold X."""
        return self.set(MARKOV_THRESHOLD, x)

    def session(self, name: str) -> "HashcatBuilder":
        """Define a specific session name."""
        return self.set(SESSION, name)

    def runtime(self, seconds: int) -> "HashcatBuilder":
        """Abort session after X seconds of runtime."""
        return self.set(RUNTIME, seconds)

    def skip(self, n: int) -> "HashcatBuilder":
        """Skip X words from the start."""
        return self.set(SKIP, n)

    def limit(self, n: int) -> "HashcatBuilder":
        """Limit X words from the start + skipped words."""
        return self.set(LIMIT, n)

    def rules_file(self, path: str) -> "HashcatBuilder":
        """Apply multiple rules from file."""
        return self.set(RULES_FILE, path)

    def rule_left(self, rule: str) -> "HashcatBuilder":
        """Apply a single left rule (e.g., `-j 'c'`)."""
        return self.set(RULE_LEFT, rule)

    def rule_right(self, rule: str) -> "HashcatBuilder":
        """Apply a single right rule (e.g., `-k '^-')`."""
        return self.set(RULE_RIGHT, rule)

    def generate_rules(self, n: int) -> "HashcatBuilder":
        """Generate X random rules."""
        return self.set(GENERATE_RULES, n)

    def increment(self, on: bool = True) -> "HashcatBuilder":
        """Enable/disable mask increment mode."""
        return self.set(INCREMENT, on)

    def increment_min(self, n: int) -> "HashcatBuilder":
        """Start mask incrementing at X."""
        return self.set(INCREMENT_MIN, n)

    def increment_max(self, n: int) -> "HashcatBuilder":
        """Stop mask incrementing at X."""
        return self.set(INCREMENT_MAX, n)

    def slow_candidates(self, on: bool = True) -> "HashcatBuilder":
        """Enable slower (but advanced) candidate generators."""
        return self.set(SLOW_CANDIDATES, on)

    # Custom charsets (?1.. ?8)
    def cs1(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET1, cs)
    def cs2(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET2, cs)
    def cs3(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET3, cs)
    def cs4(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET4, cs)
    def cs5(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET5, cs)
    def cs6(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET6, cs)
    def cs7(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET7, cs)
    def cs8(self, cs: str) -> "HashcatBuilder": return self.set(CUSTOM_CHARSET8, cs)

    # Encoding / potfile
    def encoding_from(self, code: str) -> "HashcatBuilder": return self.set(ENCODING_FROM, code)
    def encoding_to(self, code: str) -> "HashcatBuilder":   return self.set(ENCODING_TO, code)
    def potfile_path(self, path: str) -> "HashcatBuilder":  return self.set(POTFILE_PATH, path)
    def potfile_disable(self, on: bool = True) -> "HashcatBuilder": return self.set(POTFILE_DISABLE, on)

    # Backend / performance
    def backend_devices(self, csv: str) -> "HashcatBuilder":    return self.set(BACKEND_DEVICES, csv)
    def opencl_device_types(self, csv: str) -> "HashcatBuilder":return self.set(OPENCL_DEVICE_TYPES, csv)
    def backend_info(self, on: bool = True) -> "HashcatBuilder":return self.set(BACKEND_INFO, on)
    def kernel_accel(self, n: int) -> "HashcatBuilder":         return self.set(KERNEL_ACCEL, n)
    def kernel_loops(self, n: int) -> "HashcatBuilder":         return self.set(KERNEL_LOOPS, n)
    def kernel_threads(self, n: int) -> "HashcatBuilder":       return self.set(KERNEL_THREADS, n)
    def vector_width(self, n: int) -> "HashcatBuilder":         return self.set(BACKEND_VECTOR_WIDTH, n)
    def optimized_kernel(self, on: bool = True) -> "HashcatBuilder": return self.set(OPTIMIZED_KERNEL_ENABLE, on)
    def multiply_accel_disable(self, on: bool = True) -> "HashcatBuilder": return self.set(MULTIPLY_ACCEL_DISABLE, on)
    def cpu_affinity(self, csv: str) -> "HashcatBuilder":       return self.set(CPU_AFFINITY, csv)
    def hook_threads(self, n: int) -> "HashcatBuilder":         return self.set(HOOK_THREADS, n)

    # Brain / QoL
    def brain_client(self, on: bool = True) -> "HashcatBuilder": return self.set(BRAIN_CLIENT, on)
    def brain_server(self, on: bool = True) -> "HashcatBuilder": return self.set(BRAIN_SERVER, on)
    def brain_host(self, host: str) -> "HashcatBuilder":         return self.set(BRAIN_HOST, host)
    def brain_port(self, port: int) -> "HashcatBuilder":         return self.set(BRAIN_PORT, port)
    def brain_password(self, pwd: str) -> "HashcatBuilder":      return self.set(BRAIN_PASSWORD, pwd)
    def color_cracked(self, on: bool = True) -> "HashcatBuilder":return self.set(COLOR_CRACKED, on)

    # Presentation / output helpers
    def quiet(self, on: bool = True) -> "HashcatBuilder":  return self.set(QUIET, on)
    def force(self, on: bool = True) -> "HashcatBuilder":  return self.set(FORCE, on)
    def show(self, on: bool = True) -> "HashcatBuilder":   return self.set(SHOW, on)
    def left(self, on: bool = True) -> "HashcatBuilder":   return self.set(LEFT, on)
    def stdout(self, on: bool = True) -> "HashcatBuilder": return self.set(STDOUT, on)

    # ---------------------------------------------------------------------
    # Materialization
    # ---------------------------------------------------------------------
    def value(self) -> List[str]:
        """
        Render the command as a list of arguments.

        Returns
        -------
        list[str]
            Suitable for `subprocess.run(self.value(), ...)`.

        Emission rules
        --------------
        - Boolean flags emit only the flag when True; omitted otherwise.
        - Valued flags emit [flag, value].
        - Options are sorted by flag for determinism (easy to diff tests).
        - Positionals are appended at the end, in insertion order.
        """
        cmd = [self.binary]
        for flag in sorted(self._opts.keys()):
            val = _normalize(flag, self._opts[flag])
            kind = VALUE_KIND.get(flag)
            if kind is None:
                if val is True:
                    cmd.append(flag)
            else:
                if val is not None:
                    cmd.extend([flag, str(val)])
        cmd.extend(self._positionals)
        return cmd

    def cmdline(self) -> str:
        """
        Render the command as a printable string with proper quoting.

        Returns
        -------
        str
        """
        return " ".join(shlex.quote(str(x)) for x in self.value())

    def run(
        self,
        *,
        check: bool = True,
        capture_output: bool = False,
        text: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute the command with `subprocess.run`.

        Parameters
        ----------
        check : bool, default True
            If True, raise CalledProcessError on non-zero exit.

        capture_output : bool, default False
            If True, capture stdout/stderr (Python 3.7+).

        text : bool, default True
            If True, decode output to text (UTF-8 by default).

        Returns
        -------
        subprocess.CompletedProcess
        """
        return subprocess.run(self.value(), check=check, capture_output=capture_output, text=text)


# Convenience factory matching the desired DSL
def hashcat(*positionals: str, binary: str = HC) -> HashcatBuilder:
    """
    Create a new builder with optional initial positionals.

    Parameters
    ----------
    *positionals : str
        Positional arguments (hash|hashfile|hccapxfile, dict/mask/dir...).

    binary : str, default HC
        Hashcat executable. The package-level __init__ resolves a smarter default;
        here we keep it simple to avoid circular imports.

    Returns
    -------
    HashcatBuilder
    """
    return HashcatBuilder.empty(binary=binary).arg(*positionals)


__all__ = ["HashcatBuilder", "hashcat"]
