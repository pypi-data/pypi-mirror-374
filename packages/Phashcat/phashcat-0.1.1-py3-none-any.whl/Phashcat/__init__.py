"""
Phashcat – Python wrapper for Hashcat CLI

This package exposes:
- hashcat(...)      -> factory function returning a HashcatBuilder
- HashcatBuilder    -> fluent, monoid-style builder
- flags             -> module with all CLI constants, tables, VALUE_KIND, etc.
"""

from .hashcat import hashcat, HashcatBuilder, flags

__version__ = "0.1.0"

__all__ = [
    "hashcat",
    "HashcatBuilder",
    "flags",
    "__version__",
]


