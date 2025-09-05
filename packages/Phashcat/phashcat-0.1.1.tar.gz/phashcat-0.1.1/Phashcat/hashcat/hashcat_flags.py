# hashcat_flags.py — constants and tables for Hashcat (v7.1.2)


"""
Hashcat Flags & Tables (v7.1.2)
===============================

This module provides **Python constants** for all long-form Hashcat options
exposed in `hashcat --help` (the output you supplied), an alias map from
short → long flags, a value-kind schema for light validation, and helpful
tables (attack modes, outfile formats, etc.). It also exposes a small helper
to build a command list safely.

Why a separate flags module?
----------------------------
Separating constants from the builder keeps responsibilities clear:
- This module is a *data catalog* (stable, easy to test).
- The builder composes these constants into commands (fluent API).

Version note
------------
The flags below are generated from Hashcat **v7.1.2** help text. If you
upgrade Hashcat, re-generate or extend the constants accordingly.

Quick Start
-----------
    from hashcat.hashcat_flags import (
        HASH_TYPE, ATTACK_MODE, OUTFILE, STATUS, VALUE_KIND, build_cmd
    )

    cmd = build_cmd(
        opts={
            HASH_TYPE: 0,            # MD5
            ATTACK_MODE: 3,          # brute-force
            OUTFILE: "cracked.txt",
            STATUS: True,            # boolean switch
        },
        positionals=["example0.hash", "?d?d?d?d?d?d"]
    )
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any


# =============================================================================
# Long-form flags (constants)
# =============================================================================

HC = "hashcat.exe"  # default executable; the package resolves a better path at runtime

HASH_TYPE = "--hash-type"                      # -m
ATTACK_MODE = "--attack-mode"                  # -a
VERSION = "--version"                          # -V
HELP = "--help"                                # -h / -hh
QUIET = "--quiet"
HEX_CHARSET = "--hex-charset"
HEX_SALT = "--hex-salt"
HEX_WORDLIST = "--hex-wordlist"
FORCE = "--force"
DEPRECATED_CHECK_DISABLE = "--deprecated-check-disable"
STATUS = "--status"
STATUS_JSON = "--status-json"
STATUS_TIMER = "--status-timer"
STDIN_TIMEOUT_ABORT = "--stdin-timeout-abort"
MACHINE_READABLE = "--machine-readable"
KEEP_GUESSING = "--keep-guessing"
SELF_TEST_DISABLE = "--self-test-disable"
LOOPBACK = "--loopback"
MARKOV_HCSTAT2 = "--markov-hcstat2"
MARKOV_DISABLE = "--markov-disable"
MARKOV_CLASSIC = "--markov-classic"
MARKOV_INVERSE = "--markov-inverse"
MARKOV_THRESHOLD = "--markov-threshold"        # -t
METAL_COMPILER_RUNTIME = "--metal-compiler-runtime"
RUNTIME = "--runtime"
SESSION = "--session"
RESTORE = "--restore"
RESTORE_DISABLE = "--restore-disable"
RESTORE_FILE_PATH = "--restore-file-path"
OUTFILE = "--outfile"                           # -o
OUTFILE_FORMAT = "--outfile-format"
OUTFILE_JSON = "--outfile-json"
OUTFILE_AUTOHEX_DISABLE = "--outfile-autohex-disable"
OUTFILE_CHECK_TIMER = "--outfile-check-timer"
WORDLIST_AUTOHEX_DISABLE = "--wordlist-autohex-disable"
SEPARATOR = "--separator"                       # -p
STDOUT = "--stdout"
SHOW = "--show"
LEFT = "--left"
USERNAME = "--username"
DYNAMIC_X = "--dynamic-x"
REMOVE = "--remove"
REMOVE_TIMER = "--remove-timer"
POTFILE_DISABLE = "--potfile-disable"
POTFILE_PATH = "--potfile-path"
ENCODING_FROM = "--encoding-from"
ENCODING_TO = "--encoding-to"
DEBUG_MODE = "--debug-mode"
DEBUG_FILE = "--debug-file"
INDUCTION_DIR = "--induction-dir"
OUTFILE_CHECK_DIR = "--outfile-check-dir"
LOGFILE_DISABLE = "--logfile-disable"
HCCAPX_MESSAGE_PAIR = "--hccapx-message-pair"
NONCE_ERROR_CORRECTIONS = "--nonce-error-corrections"
KEYBOARD_LAYOUT_MAPPING = "--keyboard-layout-mapping"
TRUECRYPT_KEYFILES = "--truecrypt-keyfiles"
VERACRYPT_KEYFILES = "--veracrypt-keyfiles"
VERACRYPT_PIM_START = "--veracrypt-pim-start"
VERACRYPT_PIM_STOP = "--veracrypt-pim-stop"
BENCHMARK = "--benchmark"                       # -b
BENCHMARK_ALL = "--benchmark-all"
BENCHMARK_MIN = "--benchmark-min"
BENCHMARK_MAX = "--benchmark-max"
SPEED_ONLY = "--speed-only"
PROGRESS_ONLY = "--progress-only"
SEGMENT_SIZE = "--segment-size"                # -c
BITMAP_MIN = "--bitmap-min"
BITMAP_MAX = "--bitmap-max"
BRIDGE_PARAMETER1 = "--bridge-parameter1"
BRIDGE_PARAMETER2 = "--bridge-parameter2"
BRIDGE_PARAMETER3 = "--bridge-parameter3"
BRIDGE_PARAMETER4 = "--bridge-parameter4"
CPU_AFFINITY = "--cpu-affinity"
HOOK_THREADS = "--hook-threads"
HASH_INFO = "--hash-info"                       # -H / -HH
EXAMPLE_HASHES = "--example-hashes"
BACKEND_IGNORE_CUDA = "--backend-ignore-cuda"
BACKEND_IGNORE_HIP = "--backend-ignore-hip"
BACKEND_IGNORE_METAL = "--backend-ignore-metal"
BACKEND_IGNORE_OPENCL = "--backend-ignore-opencl"
BACKEND_INFO = "--backend-info"                 # -I / -II
BACKEND_DEVICES = "--backend-devices"           # -d
BACKEND_DEVICES_VIRTMULTI = "--backend-devices-virtmulti" # -Y
BACKEND_DEVICES_VIRTHOST = "--backend-devices-virthost"   # -R
BACKEND_DEVICES_KEEPFREE = "--backend-devices-keepfree"
OPENCL_DEVICE_TYPES = "--opencl-device-types"   # -D
OPTIMIZED_KERNEL_ENABLE = "--optimized-kernel-enable"     # -O
MULTIPLY_ACCEL_DISABLE = "--multiply-accel-disable"       # -M
WORKLOAD_PROFILE = "--workload-profile"         # -w
KERNEL_ACCEL = "--kernel-accel"                 # -n
KERNEL_LOOPS = "--kernel-loops"                 # -u
KERNEL_THREADS = "--kernel-threads"             # -T
BACKEND_VECTOR_WIDTH = "--backend-vector-width"
SPIN_DAMP = "--spin-damp"
HWMON_DISABLE = "--hwmon-disable"
HWMON_TEMP_ABORT = "--hwmon-temp-abort"
SCRYPT_TMTO = "--scrypt-tmto"
SKIP = "--skip"                                 # -s
LIMIT = "--limit"                               # -l
KEYSPACE = "--keyspace"
TOTAL_CANDIDATES = "--total-candidates"
RULE_LEFT = "--rule-left"                       # -j
RULE_RIGHT = "--rule-right"                     # -k
RULES_FILE = "--rules-file"                     # -r
GENERATE_RULES = "--generate-rules"             # -g
GENERATE_RULES_FUNC_MIN = "--generate-rules-func-min"
GENERATE_RULES_FUNC_MAX = "--generate-rules-func-max"
GENERATE_RULES_FUNC_SEL = "--generate-rules-func-sel"
GENERATE_RULES_SEED = "--generate-rules-seed"
CUSTOM_CHARSET1 = "--custom-charset1"           # -1
CUSTOM_CHARSET2 = "--custom-charset2"           # -2
CUSTOM_CHARSET3 = "--custom-charset3"           # -3
CUSTOM_CHARSET4 = "--custom-charset4"           # -4
CUSTOM_CHARSET5 = "--custom-charset5"           # -5
CUSTOM_CHARSET6 = "--custom-charset6"           # -6
CUSTOM_CHARSET7 = "--custom-charset7"           # -7
CUSTOM_CHARSET8 = "--custom-charset8"           # -8
IDENTIFY = "--identify"
INCREMENT = "--increment"                       # -i
INCREMENT_INVERSE = "--increment-inverse"
INCREMENT_MIN = "--increment-min"
INCREMENT_MAX = "--increment-max"
SLOW_CANDIDATES = "--slow-candidates"           # -S
BYPASS_DELAY = "--bypass-delay"
BYPASS_THRESHOLD = "--bypass-threshold"
BRAIN_SERVER = "--brain-server"
BRAIN_SERVER_TIMER = "--brain-server-timer"
BRAIN_CLIENT = "--brain-client"                 # -z
BRAIN_CLIENT_FEATURES = "--brain-client-features"
BRAIN_HOST = "--brain-host"
BRAIN_PORT = "--brain-port"
BRAIN_PASSWORD = "--brain-password"
BRAIN_SESSION = "--brain-session"
BRAIN_SESSION_WHITELIST = "--brain-session-whitelist"
COLOR_CRACKED = "--color-cracked"


# =============================================================================
# Short → Long aliases
# =============================================================================

SHORT_TO_LONG: Dict[str, str] = {
    "-m": HASH_TYPE,
    "-a": ATTACK_MODE,
    "-V": VERSION,
    "-h": HELP,  # (-hh for extended help; both map here)
    "-t": MARKOV_THRESHOLD,
    "-o": OUTFILE,
    "-p": SEPARATOR,
    "-b": BENCHMARK,
    "-c": SEGMENT_SIZE,
    "-H": HASH_INFO,  # (-HH also valid)
    "-I": BACKEND_INFO,  # (-II also valid)
    "-d": BACKEND_DEVICES,
    "-Y": BACKEND_DEVICES_VIRTMULTI,
    "-R": BACKEND_DEVICES_VIRTHOST,
    "-D": OPENCL_DEVICE_TYPES,
    "-O": OPTIMIZED_KERNEL_ENABLE,
    "-M": MULTIPLY_ACCEL_DISABLE,
    "-w": WORKLOAD_PROFILE,
    "-n": KERNEL_ACCEL,
    "-u": KERNEL_LOOPS,
    "-T": KERNEL_THREADS,
    "-s": SKIP,
    "-l": LIMIT,
    "-j": RULE_LEFT,
    "-k": RULE_RIGHT,
    "-r": RULES_FILE,
    "-g": GENERATE_RULES,
    "-1": CUSTOM_CHARSET1,
    "-2": CUSTOM_CHARSET2,
    "-3": CUSTOM_CHARSET3,
    "-4": CUSTOM_CHARSET4,
    "-5": CUSTOM_CHARSET5,
    "-6": CUSTOM_CHARSET6,
    "-7": CUSTOM_CHARSET7,
    "-8": CUSTOM_CHARSET8,
    "-i": INCREMENT,
    "-S": SLOW_CANDIDATES,
    "-z": BRAIN_CLIENT,
}


# =============================================================================
# Value kinds per option (light validation schema)
#   Kinds: "Num", "Str", "File", "Dir", "Char", "Port", "Code", "Hex", "Rule", "CS", None (boolean switch)
# =============================================================================

VALUE_KIND: Dict[str, Optional[str]] = {
    HASH_TYPE: "Num",
    ATTACK_MODE: "Num",
    VERSION: None,
    HELP: None,
    QUIET: None,
    HEX_CHARSET: None,
    HEX_SALT: None,
    HEX_WORDLIST: None,
    FORCE: None,
    DEPRECATED_CHECK_DISABLE: None,
    STATUS: None,
    STATUS_JSON: None,
    STATUS_TIMER: "Num",
    STDIN_TIMEOUT_ABORT: "Num",
    MACHINE_READABLE: None,
    KEEP_GUESSING: None,
    SELF_TEST_DISABLE: None,
    LOOPBACK: None,
    MARKOV_HCSTAT2: "File",
    MARKOV_DISABLE: None,
    MARKOV_CLASSIC: None,
    MARKOV_INVERSE: None,
    MARKOV_THRESHOLD: "Num",
    METAL_COMPILER_RUNTIME: "Num",
    RUNTIME: "Num",
    SESSION: "Str",
    RESTORE: None,
    RESTORE_DISABLE: None,
    RESTORE_FILE_PATH: "File",
    OUTFILE: "File",
    OUTFILE_FORMAT: "Str",  # comma-separated ids
    OUTFILE_JSON: None,
    OUTFILE_AUTOHEX_DISABLE: None,
    OUTFILE_CHECK_TIMER: "Num",
    WORDLIST_AUTOHEX_DISABLE: None,
    SEPARATOR: "Char",
    STDOUT: None,
    SHOW: None,
    LEFT: None,
    USERNAME: None,
    DYNAMIC_X: None,
    REMOVE: None,
    REMOVE_TIMER: "Num",
    POTFILE_DISABLE: None,
    POTFILE_PATH: "File",
    ENCODING_FROM: "Code",
    ENCODING_TO: "Code",
    DEBUG_MODE: "Num",
    DEBUG_FILE: "File",
    INDUCTION_DIR: "Dir",
    OUTFILE_CHECK_DIR: "Dir",
    LOGFILE_DISABLE: None,
    HCCAPX_MESSAGE_PAIR: "Num",
    NONCE_ERROR_CORRECTIONS: "Num",
    KEYBOARD_LAYOUT_MAPPING: "File",
    TRUECRYPT_KEYFILES: "File",
    VERACRYPT_KEYFILES: "File",
    VERACRYPT_PIM_START: "Num",
    VERACRYPT_PIM_STOP: "Num",
    BENCHMARK: None,
    BENCHMARK_ALL: None,
    BENCHMARK_MIN: "Num",
    BENCHMARK_MAX: "Num",
    SPEED_ONLY: None,
    PROGRESS_ONLY: None,
    SEGMENT_SIZE: "Num",
    BITMAP_MIN: "Num",
    BITMAP_MAX: "Num",
    BRIDGE_PARAMETER1: "Str",
    BRIDGE_PARAMETER2: "Str",
    BRIDGE_PARAMETER3: "Str",
    BRIDGE_PARAMETER4: "Str",
    CPU_AFFINITY: "Str",
    HOOK_THREADS: "Num",
    HASH_INFO: None,
    EXAMPLE_HASHES: None,
    BACKEND_IGNORE_CUDA: None,
    BACKEND_IGNORE_HIP: None,
    BACKEND_IGNORE_METAL: None,
    BACKEND_IGNORE_OPENCL: None,
    BACKEND_INFO: None,
    BACKEND_DEVICES: "Str",
    BACKEND_DEVICES_VIRTMULTI: "Num",
    BACKEND_DEVICES_VIRTHOST: "Num",
    BACKEND_DEVICES_KEEPFREE: "Num",
    OPENCL_DEVICE_TYPES: "Str",
    OPTIMIZED_KERNEL_ENABLE: None,
    MULTIPLY_ACCEL_DISABLE: None,
    WORKLOAD_PROFILE: "Num",
    KERNEL_ACCEL: "Num",
    KERNEL_LOOPS: "Num",
    KERNEL_THREADS: "Num",
    BACKEND_VECTOR_WIDTH: "Num",
    SPIN_DAMP: "Num",
    HWMON_DISABLE: None,
    HWMON_TEMP_ABORT: "Num",
    SCRYPT_TMTO: "Num",
    SKIP: "Num",
    LIMIT: "Num",
    KEYSPACE: None,
    TOTAL_CANDIDATES: None,
    RULE_LEFT: "Rule",
    RULE_RIGHT: "Rule",
    RULES_FILE: "File",
    GENERATE_RULES: "Num",
    GENERATE_RULES_FUNC_MIN: "Num",
    GENERATE_RULES_FUNC_MAX: "Num",
    GENERATE_RULES_FUNC_SEL: "Str",
    GENERATE_RULES_SEED: "Num",
    CUSTOM_CHARSET1: "CS",
    CUSTOM_CHARSET2: "CS",
    CUSTOM_CHARSET3: "CS",
    CUSTOM_CHARSET4: "CS",
    CUSTOM_CHARSET5: "CS",
    CUSTOM_CHARSET6: "CS",
    CUSTOM_CHARSET7: "CS",
    CUSTOM_CHARSET8: "CS",
    IDENTIFY: None,  # (takes file positional, not value)
    INCREMENT: None,
    INCREMENT_INVERSE: None,
    INCREMENT_MIN: "Num",
    INCREMENT_MAX: "Num",
    SLOW_CANDIDATES: None,
    BYPASS_DELAY: "Num",
    BYPASS_THRESHOLD: "Num",
    BRAIN_SERVER: None,
    BRAIN_SERVER_TIMER: "Num",
    BRAIN_CLIENT: None,
    BRAIN_CLIENT_FEATURES: "Num",
    BRAIN_HOST: "Str",
    BRAIN_PORT: "Port",
    BRAIN_PASSWORD: "Str",
    BRAIN_SESSION: "Hex",
    BRAIN_SESSION_WHITELIST: "Hex",
    COLOR_CRACKED: None,
}


# =============================================================================
# Tables (from help output)
# =============================================================================

ATTACK_MODES = {
    0: "Straight",
    1: "Combination",
    3: "Brute-force",
    6: "Hybrid Wordlist + Mask",
    7: "Hybrid Mask + Wordlist",
    9: "Association",
}

OUTFILE_FORMATS = {
    1: "hash[:salt]",
    2: "plain",
    3: "hex_plain",
    4: "crack_pos",
    5: "timestamp absolute",
    6: "timestamp relative",
}

RULE_DEBUG_MODES = {
    1: "Finding-Rule",
    2: "Original-Word",
    3: "Original-Word:Finding-Rule",
    4: "Original-Word:Finding-Rule:Processed-Word",
    5: "Original-Word:Finding-Rule:Processed-Word:Wordlist",
}

BRAIN_CLIENT_FEATURES = {
    1: "Send hashed passwords",
    2: "Send attack positions",
    3: "Send hashed passwords and attack positions",
}

BUILTIN_CHARSETS = {
    "l": "[a-z]",
    "u": "[A-Z]",
    "d": "[0-9]",
    "h": "[0-9a-f]",
    "H": "[0-9A-F]",
    "s": r""" !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~""",
    "a": "?l?u?d?s",
    "b": "0x00-0xff",
}

OPENCL_DEVICE_TYPES = {
    1: "CPU",
    2: "GPU",
    3: "FPGA, DSP, Co-Processor",
}

WORKLOAD_PROFILES = {
    1: {"Performance": "Low",      "Runtime": "2 ms",   "Power": "Low",     "DesktopImpact": "Minimal"},
    2: {"Performance": "Default",  "Runtime": "12 ms",  "Power": "Economic","DesktopImpact": "Noticeable"},
    3: {"Performance": "High",     "Runtime": "96 ms",  "Power": "High",    "DesktopImpact": "Unresponsive"},
    4: {"Performance": "Nightmare","Runtime": "480 ms", "Power": "Insane",  "DesktopImpact": "Headless"},
}


# =============================================================================
# Helper: build_cmd
# =============================================================================

def build_cmd(
    *,
    binary: str = HC,
    opts: Optional[Dict[str, Any]] = None,
    positionals: Optional[List[str]] = None,
) -> List[str]:
    """
    Build a Hashcat command list safely.

    Parameters
    ----------
    binary : str
        The path/name of the hashcat executable. Defaults to `HC` ("hashcat.exe").
        The package-level factory function resolves a smarter default.

    opts : dict[str, Any] | None
        Mapping of {flag -> value_or_bool}. For boolean switches use True/False.
        For valued flags supply a string or number; it will be stringified.

    positionals : list[str] | None
        Positional arguments appended after options, e.g.:
        [hash|hashfile|hccapxfile, dictionary|mask|directory...]

    Returns
    -------
    list[str]
        A command argument vector ready for `subprocess.run`.

    Notes
    -----
    - This function performs **no path existence checks**.
    - Light validation is available through VALUE_KIND in the builder;
      here we assume you pass already-validated values.
    """
    cmd = [binary]
    opts = opts or {}
    for flag, val in opts.items():
        kind = VALUE_KIND.get(flag)
        if kind is None:
            if val:
                cmd.append(flag)
        else:
            if val is not None:
                cmd.extend([flag, str(val)])
    if positionals:
        cmd.extend(positionals)
    return cmd


__all__ = [
    # Executable default
    "HC",

    # Flags
    "HASH_TYPE", "ATTACK_MODE", "VERSION", "HELP", "QUIET", "HEX_CHARSET", "HEX_SALT",
    "HEX_WORDLIST", "FORCE", "DEPRECATED_CHECK_DISABLE", "STATUS", "STATUS_JSON",
    "STATUS_TIMER", "STDIN_TIMEOUT_ABORT", "MACHINE_READABLE", "KEEP_GUESSING",
    "SELF_TEST_DISABLE", "LOOPBACK", "MARKOV_HCSTAT2", "MARKOV_DISABLE", "MARKOV_CLASSIC",
    "MARKOV_INVERSE", "MARKOV_THRESHOLD", "METAL_COMPILER_RUNTIME", "RUNTIME", "SESSION",
    "RESTORE", "RESTORE_DISABLE", "RESTORE_FILE_PATH", "OUTFILE", "OUTFILE_FORMAT",
    "OUTFILE_JSON", "OUTFILE_AUTOHEX_DISABLE", "OUTFILE_CHECK_TIMER",
    "WORDLIST_AUTOHEX_DISABLE", "SEPARATOR", "STDOUT", "SHOW", "LEFT", "USERNAME",
    "DYNAMIC_X", "REMOVE", "REMOVE_TIMER", "POTFILE_DISABLE", "POTFILE_PATH",
    "ENCODING_FROM", "ENCODING_TO", "DEBUG_MODE", "DEBUG_FILE", "INDUCTION_DIR",
    "OUTFILE_CHECK_DIR", "LOGFILE_DISABLE", "HCCAPX_MESSAGE_PAIR",
    "NONCE_ERROR_CORRECTIONS", "KEYBOARD_LAYOUT_MAPPING", "TRUECRYPT_KEYFILES",
    "VERACRYPT_KEYFILES", "VERACRYPT_PIM_START", "VERACRYPT_PIM_STOP", "BENCHMARK",
    "BENCHMARK_ALL", "BENCHMARK_MIN", "BENCHMARK_MAX", "SPEED_ONLY", "PROGRESS_ONLY",
    "SEGMENT_SIZE", "BITMAP_MIN", "BITMAP_MAX", "BRIDGE_PARAMETER1", "BRIDGE_PARAMETER2",
    "BRIDGE_PARAMETER3", "BRIDGE_PARAMETER4", "CPU_AFFINITY", "HOOK_THREADS",
    "HASH_INFO", "EXAMPLE_HASHES", "BACKEND_IGNORE_CUDA", "BACKEND_IGNORE_HIP",
    "BACKEND_IGNORE_METAL", "BACKEND_IGNORE_OPENCL", "BACKEND_INFO", "BACKEND_DEVICES",
    "BACKEND_DEVICES_VIRTMULTI", "BACKEND_DEVICES_VIRTHOST", "BACKEND_DEVICES_KEEPFREE",
    "OPENCL_DEVICE_TYPES", "OPTIMIZED_KERNEL_ENABLE", "MULTIPLY_ACCEL_DISABLE",
    "WORKLOAD_PROFILE", "KERNEL_ACCEL", "KERNEL_LOOPS", "KERNEL_THREADS",
    "BACKEND_VECTOR_WIDTH", "SPIN_DAMP", "HWMON_DISABLE", "HWMON_TEMP_ABORT",
    "SCRYPT_TMTO", "SKIP", "LIMIT", "KEYSPACE", "TOTAL_CANDIDATES", "RULE_LEFT",
    "RULE_RIGHT", "RULES_FILE", "GENERATE_RULES", "GENERATE_RULES_FUNC_MIN",
    "GENERATE_RULES_FUNC_MAX", "GENERATE_RULES_FUNC_SEL", "GENERATE_RULES_SEED",
    "CUSTOM_CHARSET1", "CUSTOM_CHARSET2", "CUSTOM_CHARSET3", "CUSTOM_CHARSET4",
    "CUSTOM_CHARSET5", "CUSTOM_CHARSET6", "CUSTOM_CHARSET7", "CUSTOM_CHARSET8",
    "IDENTIFY", "INCREMENT", "INCREMENT_INVERSE", "INCREMENT_MIN", "INCREMENT_MAX",
    "SLOW_CANDIDATES", "BYPASS_DELAY", "BYPASS_THRESHOLD", "BRAIN_SERVER",
    "BRAIN_SERVER_TIMER", "BRAIN_CLIENT", "BRAIN_CLIENT_FEATURES", "BRAIN_HOST",
    "BRAIN_PORT", "BRAIN_PASSWORD", "BRAIN_SESSION", "BRAIN_SESSION_WHITELIST",
    "COLOR_CRACKED",

    # Maps & helpers
    "SHORT_TO_LONG", "VALUE_KIND",
    "ATTACK_MODES", "OUTFILE_FORMATS", "RULE_DEBUG_MODES",
    "BRAIN_CLIENT_FEATURES", "BUILTIN_CHARSETS",
    "OPENCL_DEVICE_TYPES", "WORKLOAD_PROFILES",
    "build_cmd",
]
