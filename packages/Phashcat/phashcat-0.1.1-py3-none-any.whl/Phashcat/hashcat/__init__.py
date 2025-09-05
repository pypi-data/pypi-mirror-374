"""
hashcat – Pythonic wrapper tools around Hashcat CLI.

Exports:
- hashcat(*positionals, binary=None)  -> HashcatBuilder
- HashcatBuilder                      -> immutable, monoid-style builder
- flags                               -> module with all CLI flag constants, tables, VALUE_KIND, etc.

Binary resolution order (bundled-first, no external dependency):
1) explicit `binary` arg
2) env var HASHCAT_BINARY **if it resolves to a real executable**
3) bundled binary shipped with this package (same dir as this __init__):
     - 'hashcat.exe' (Windows) OR 'hashcat' (Linux/macOS)
4) system PATH via shutil.which
5) fallback: 'hashcat.exe' on Windows, else 'hashcat'
"""

from __future__ import annotations

from pathlib import Path
import os
import shutil

# Expose the flags module as a namespace (constants, tables, VALUE_KIND…)
from . import hashcat_flags as flags

# Import the builder class (we’ll wrap the factory to auto-resolve binary)
from .hashcat_builder import HashcatBuilder as _HashcatBuilder

__version__ = "0.1.0"


def _resolve_binary(explicit: str | None = None) -> str:
    """Resolve the hashcat binary path with a bundled-first strategy."""
    if explicit:
        return explicit

    # 1) Respect HASHCAT_BINARY only if it points to a real executable
    env = os.getenv("HASHCAT_BINARY")
    if env:
        # absolute/relative file path
        env_path = Path(env)
        if env_path.exists() and env_path.is_file():
            return str(env_path)
        # or a resolvable name on PATH
        found_env = shutil.which(env)
        if found_env:
            return found_env
        # otherwise ignore and continue (don't break the bundled-first guarantee)

    # 2) Bundled binary next to this module (cross-platform pack-in)
    here = Path(__file__).resolve().parent  # .../Phashcat/hashcat
    bundled_win = here / "hashcat.exe"
    bundled_nix = here / "hashcat"
    if bundled_win.exists() and bundled_win.is_file():
        return str(bundled_win)
    if bundled_nix.exists() and bundled_nix.is_file():
        return str(bundled_nix)

    # 3) Try system PATH (if user prefers external install)
    found = shutil.which("hashcat") or shutil.which("hashcat.exe")
    if found:
        return found

    # 4) Fallback (last resort)
    return "hashcat.exe" if os.name == "nt" else "hashcat"


def hashcat(*positionals: str, binary: str | None = None) -> _HashcatBuilder:
    """
    Convenience factory matching your DSL:

        cmd = (
            hashcat("hash_file_name.txt")
            .hash_type(0)
            .attack_mode(3)
            .outfile("cracked.txt")
            .status(True)
            .value()
        )

    Args:
        *positionals: hash|hashfile|hccapxfile and then dictionary/mask/dir...
        binary: path to hashcat binary (optional; auto-resolved if omitted)

    Returns:
        HashcatBuilder (immutable)
    """
    return _HashcatBuilder.empty(binary=_resolve_binary(binary)).arg(*positionals)


# Clean public surface
HashcatBuilder = _HashcatBuilder

# Optionally re-export a few handy maps directly (still available under flags.*)
SHORT_TO_LONG = flags.SHORT_TO_LONG
VALUE_KIND = flags.VALUE_KIND
ATTACK_MODES = flags.ATTACK_MODES
OUTFILE_FORMATS = flags.OUTFILE_FORMATS
RULE_DEBUG_MODES = flags.RULE_DEBUG_MODES
BRAIN_CLIENT_FEATURES = flags.BRAIN_CLIENT_FEATURES
BUILTIN_CHARSETS = flags.BUILTIN_CHARSETS
OPENCL_DEVICE_TYPES = flags.OPENCL_DEVICE_TYPES
WORKLOAD_PROFILES = flags.WORKLOAD_PROFILES

__all__ = [
    "hashcat",
    "HashcatBuilder",
    "flags",
    "SHORT_TO_LONG",
    "VALUE_KIND",
    "ATTACK_MODES",
    "OUTFILE_FORMATS",
    "RULE_DEBUG_MODES",
    "BRAIN_CLIENT_FEATURES",
    "BUILTIN_CHARSETS",
    "OPENCL_DEVICE_TYPES",
    "WORKLOAD_PROFILES",
    "__version__",
]
