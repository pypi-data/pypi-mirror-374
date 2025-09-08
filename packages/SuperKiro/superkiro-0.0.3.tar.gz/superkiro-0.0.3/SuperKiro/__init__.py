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

# Resolve version robustly across source tree and installed package
def _resolve_version() -> str:
    # 1) Prefer repository VERSION file when running from source
    try:
        repo_version = (Path(__file__).resolve().parents[1] / "VERSION").read_text().strip()
        if repo_version:
            return repo_version
    except Exception:
        pass

    # 2) Installed distribution metadata (importlib.metadata)
    try:
        try:
            from importlib.metadata import version  # Python 3.8+
        except Exception:  # pragma: no cover
            from importlib_metadata import version  # type: ignore

        for dist_name in ("SuperKiro", "superkiro"):
            try:
                v = version(dist_name)
                if v:
                    return v
            except Exception:
                continue
    except Exception:
        pass

    # 3) Final fallback
    return "0.0.0"


__version__ = _resolve_version()
__author__ = "NomenAK, Mithun Gowda B"
__email__ = "anton.knoery@gmail.com"
__license__ = "MIT"
