#!/usr/bin/env python3
"""
SuperKiro Framework Management Hub
Unified entry point for all SuperKiro operations

Usage:
    SuperKiro install [options]
    SuperKiro update [options]
    SuperKiro uninstall [options]
    SuperKiro backup [options]
    SuperKiro --help
"""

from pathlib import Path

# Read version from VERSION file
try:
    __version__ = (Path(__file__).parent.parent / "VERSION").read_text().strip()
except Exception:
    __version__ = "4.0.8"  # Fallback
__author__ = "NomenAK, Mithun Gowda B"
__email__ = "anton.knoery@gmail.com"
__license__ = "MIT"
