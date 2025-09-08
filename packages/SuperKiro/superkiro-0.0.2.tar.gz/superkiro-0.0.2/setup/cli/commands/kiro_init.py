"""
Kiro Steering Initializer

Adds `.kiro/steering` templates into a target directory.

Usage (via SuperKiro CLI):
  SuperKiro kiro-init [target_dir] [--force]

Notes:
- Treat '~' as the current workspace root (PWD), not OS home.
- By default, existing files are not overwritten unless --force is specified.
"""

import argparse
from pathlib import Path
from typing import Optional, Tuple

from ...utils.ui import display_info, display_success, display_warning, display_error


def register_parser(subparsers, global_parser=None) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "kiro-init",
        help="Initialize .kiro/steering templates in a directory",
        parents=[global_parser] if global_parser else [],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Copy Kiro steering templates into the target directory.\n\n"
            "Examples:\n"
            "  SuperKiro kiro-init                # install into current dir\n"
            "  SuperKiro kiro-init ..             # install into parent dir\n"
            "  SuperKiro kiro-init ~              # treat ~ as workspace root (PWD)\n"
            "  SuperKiro kiro-init . --force          # overwrite existing files\n"
            "  SuperKiro kiro-init . --prune          # remove only SuperKiro template files\n"
            "  SuperKiro kiro-init . --sync           # prune then re-copy latest templates\n"
        ),
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)",
    )
    # Use global --force flag
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Remove only SuperKiro-managed steering templates from the target (.kiro/steering)"
    )
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Prune SuperKiro-managed templates then copy the latest templates"
    )
    return parser


def _resolve_target(target_dir: str) -> Path:
    # Treat '~' as the current workspace root (PWD), not OS home
    if target_dir.strip() == "~":
        return Path.cwd()
    return Path(target_dir).resolve()


def _get_template_root() -> Path:
    """Resolve template source root (package resources if available, otherwise filesystem fallback)."""
    # Try Python 3.9+ importlib.resources.files
    try:
        from importlib.resources import files as ir_files  # type: ignore
        return ir_files("setup.templates.kiro.steering")
    except Exception:
        # Fallback to repository filesystem path
        repo_setup_root = Path(__file__).resolve().parents[2]
        fs_root = repo_setup_root / "templates" / "kiro" / "steering"
        return fs_root


def _iter_md_files(base: Path):
    for entry in base.rglob("*"):
        try:
            if entry.is_file() and entry.name.endswith(".md"):
                yield entry
        except Exception:
            continue


def _copy_templates(dest: Path, force: bool) -> Tuple[int, int]:
    """Copy steering templates from package data to destination.

    Returns (written_count, skipped_count).
    """
    pkg_root = _get_template_root()
    if not pkg_root.exists():
        display_error(f"Template source not found: {pkg_root}")
        return (0, 0)

    dest.mkdir(parents=True, exist_ok=True)

    written = 0
    skipped = 0
    for src in _iter_md_files(pkg_root):
        rel = src.relative_to(pkg_root)
        dst = dest / rel.as_posix()
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and not force:
            display_warning(f"[SKIP] {dst} exists (use --force to overwrite)")
            skipped += 1
            continue
        try:
            content = src.read_text(encoding="utf-8")
            dst.write_text(content, encoding="utf-8")
            display_info(f"[WRITE] {dst}")
            written += 1
        except FileNotFoundError:
            display_error(f"Template not found: {src}")
        except Exception as e:
            display_error(f"Failed to write {dst}: {e}")
    return (written, skipped)


def _prune_templates(dest: Path) -> Tuple[int, int]:
    """Remove only SuperKiro-managed template files from dest.

    Returns (removed_count, preserved_count).
    """
    pkg_root = _get_template_root()
    if not pkg_root.exists():
        display_error(f"Template source not found: {pkg_root}")
        return (0, 0)

    removed = 0
    preserved = 0

    # Build the set of relative template paths
    rel_paths = [src.relative_to(pkg_root) for src in _iter_md_files(pkg_root)]

    # Backward-compat: also prune legacy top-level files even if not present in current templates
    legacy_top = [Path("super_kiro.md"), Path("_router.md"), Path("README.md")]  # historical files
    rel_paths.extend(legacy_top)

    for rel in rel_paths:
        target = dest / rel.as_posix()
        try:
            if target.exists():
                target.unlink()
                display_info(f"[REMOVE] {target}")
                removed += 1
            else:
                preserved += 1
        except Exception as e:
            display_warning(f"Could not remove {target}: {e}")

    # Clean up empty directories under dest that match our template structure
    try:
        # Remove empty 'commands' dir if empty
        commands_dir = dest / "commands"
        if commands_dir.exists() and not any(commands_dir.iterdir()):
            commands_dir.rmdir()
            display_info(f"[REMOVE] {commands_dir} (empty)")
    except Exception:
        pass

    return (removed, preserved)



def run(args: argparse.Namespace) -> int:
    target_root = _resolve_target(getattr(args, "target_dir", "."))
    dest = target_root / ".kiro" / "steering"

    display_info(f"Initializing Kiro steering into: {dest}")
    force = bool(getattr(args, "force", False))

    # Prune-only mode
    if getattr(args, "prune", False) and not getattr(args, "sync", False):
        removed, preserved = _prune_templates(dest)
        display_success(f"Kiro steering prune complete: {removed} removed, {preserved} preserved")
        return 0

    # Sync mode: prune then copy latest
    if getattr(args, "sync", False):
        _prune_templates(dest)
        written, skipped = _copy_templates(dest, force=True)
        display_success(f"Kiro steering sync complete: {written} written")
        return 0

    # Default: copy templates
    written, skipped = _copy_templates(dest, force=force)
    display_success(f"Kiro steering init complete: {written} written, {skipped} skipped")
    return 0
