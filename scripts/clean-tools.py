#!/usr/bin/env python3
"""
Clean/uninstall external development tools.

This script is a thin wrapper around the sstdf-python-standards package.
Tool logic lives in the package (versioned dependency), not in this script.

Only uninstalls plugin-managed tools (tracked in registry or in ~/.local/bin/).
Skips tools installed by other means.

Usage:
    ./scripts/clean-tools.py           # Uninstall all plugin-managed tools
    ./scripts/clean-tools.py --dry-run  # Preview what would be removed
"""

import sys
from pathlib import Path

# Import from sstdf-python-standards package
try:
    from sstdf_python_standards.tools import ToolManager
except ImportError:
    print(
        "Error: sstdf-python-standards package not installed.\n"
        "Install it with: uv sync --group dev",
        file=sys.stderr,
    )
    sys.exit(1)

import argparse

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TOOLS_DIR = SCRIPT_DIR / "tools"


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Uninstall plugin-managed external tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s              # Uninstall all plugin-managed tools
  %(prog)s --dry-run    # Preview what would be removed

Only removes tools that are:
- Tracked in the registry (~/.config/sstdf-python-tools/managed_tools.json)
- Installed in ~/.local/bin/

Tools installed by other means are skipped.
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show commands without executing them",
    )

    args = parser.parse_args()

    # Initialize manager
    manager = ToolManager(tools_dir=TOOLS_DIR, project_root=PROJECT_ROOT)

    removed = manager.uninstall_all(dry_run=args.dry_run)

    return 0 if removed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
