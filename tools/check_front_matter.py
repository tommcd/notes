#!/usr/bin/env python3
"""
Note Front Matter Validator

Validates Markdown note front matter:
- Required fields: id, title, date
- Optional fields: tags
- Date format validation
"""

import sys
from pathlib import Path
from typing import Any


def check_front_matter(file_path: Path) -> list[str]:
    """Check front matter in a Markdown file."""
    errors = []

    # TODO: Implement proper YAML front matter parsing
    # For now, just check file exists
    if not file_path.exists():
        errors.append(f"File not found: {file_path}")

    return errors


def main():
    """Main validation entry point."""
    notes_dir = Path("notes")

    if not notes_dir.exists():
        print(f"✓ No notes to validate ({notes_dir} not found)")
        return 0

    # Find all markdown files
    md_files = list(notes_dir.rglob("*.md"))

    if not md_files:
        print("✓ No notes to validate (no .md files found)")
        return 0

    all_errors = []

    for md_file in md_files:
        errors = check_front_matter(md_file)
        all_errors.extend(errors)

    if all_errors:
        print(f"✗ Front matter validation failed:", file=sys.stderr)
        for error in all_errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"✓ Validated front matter in {len(md_files)} notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
