#!/usr/bin/env python3
"""
Check for sensitive personal information in content files.

Prevents accidental commits of:
- Real names
- Work identifiers (signums, company names)
- Computer/hostname identifiers
- Specific usernames in file paths

Patterns are loaded from .sensitive-patterns file (gitignored).
See .sensitive-patterns.example for template.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def load_patterns(config_file: Path) -> Dict[str, str]:
    """Load sensitive patterns from config file."""
    patterns = {}

    if not config_file.exists():
        print(f"Error: {config_file} not found", file=sys.stderr)
        print(f"Copy .sensitive-patterns.example to .sensitive-patterns and customize", file=sys.stderr)
        sys.exit(1)

    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse pattern_name = regex
            if '=' in line:
                name, pattern = line.split('=', 1)
                patterns[name.strip()] = pattern.strip()

    return patterns

def check_file(file_path: Path, patterns: Dict[str, str]) -> List[Tuple[int, str, str]]:
    """
    Check a file for sensitive information.

    Returns:
        List of (line_number, pattern_name, matched_text) tuples
    """
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                for pattern_name, pattern in patterns.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        violations.append((line_num, pattern_name, match.group()))
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    return violations

def main():
    """Check all markdown files in docs/ for sensitive information."""
    repo_root = Path(__file__).parent.parent
    docs_dir = repo_root / "docs"
    config_file = repo_root / ".sensitive-patterns"

    # Load patterns from config
    patterns = load_patterns(config_file)

    if not patterns:
        print("Warning: No patterns loaded from .sensitive-patterns", file=sys.stderr)
        sys.exit(0)

    if not docs_dir.exists():
        print(f"Error: docs directory not found at {docs_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all markdown files
    md_files = list(docs_dir.rglob("*.md"))

    if not md_files:
        print("No markdown files found in docs/")
        sys.exit(0)

    total_violations = 0
    files_with_violations = 0

    for md_file in md_files:
        violations = check_file(md_file, patterns)

        if violations:
            files_with_violations += 1
            total_violations += len(violations)

            # Make path relative to repo root for cleaner output
            rel_path = md_file.relative_to(repo_root)
            print(f"\n❌ {rel_path}")

            for line_num, pattern_name, matched_text in violations:
                print(f"   Line {line_num}: {pattern_name} - '{matched_text}'")

    # Summary
    print(f"\n{'='*60}")
    print(f"Checked {len(md_files)} files")

    if total_violations > 0:
        print(f"❌ Found {total_violations} violation(s) in {files_with_violations} file(s)")
        print("\nPlease remove or redact sensitive information before committing.")
        sys.exit(1)
    else:
        print("✅ No sensitive information detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
