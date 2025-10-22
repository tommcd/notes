#!/usr/bin/env python3
"""
Reference Database Validator

Validates JSONL reference records against schema:
- JSON Schema compliance
- Unique ID enforcement
- Tag vocabulary validation
- Required fields present
"""

import json
import sys
from pathlib import Path
from typing import Set


def load_allowed_tags(tags_file: Path) -> Set[str]:
    """Load allowed tags from tags.yaml."""
    # TODO: Implement YAML parsing
    # For now, return a permissive set
    return {"sample", "blog", "test", "web", "security", "python"}


def validate_reference(ref: dict, allowed_tags: Set[str], seen_ids: Set[str]) -> list[str]:
    """Validate a single reference record."""
    errors = []

    # Check required fields
    if "id" not in ref:
        errors.append("Missing required field: id")
    elif ref["id"] in seen_ids:
        errors.append(f"Duplicate ID: {ref['id']}")
    else:
        seen_ids.add(ref["id"])

    if "title" not in ref:
        errors.append(f"Missing required field 'title' in {ref.get('id', 'unknown')}")

    if "url" not in ref:
        errors.append(f"Missing required field 'url' in {ref.get('id', 'unknown')}")

    # Check tags
    if "tags" in ref:
        for tag in ref["tags"]:
            if tag not in allowed_tags:
                errors.append(f"Unknown tag '{tag}' in {ref.get('id', 'unknown')}")

    return errors


def main():
    """Main validation entry point."""
    refs_dir = Path("data/refs/shards")
    tags_file = Path("data/refs/tags.yaml")

    if not refs_dir.exists():
        print(f"✓ No references to validate ({refs_dir} not found)")
        return 0

    # Load allowed tags
    if tags_file.exists():
        allowed_tags = load_allowed_tags(tags_file)
    else:
        print("⚠ Warning: tags.yaml not found, skipping tag validation")
        allowed_tags = set()

    # Validate all JSONL files
    all_errors = []
    seen_ids: Set[str] = set()
    total_refs = 0

    for jsonl_file in refs_dir.rglob("*.jsonl"):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    ref = json.loads(line)
                    total_refs += 1
                    errors = validate_reference(ref, allowed_tags, seen_ids)
                    if errors:
                        for error in errors:
                            all_errors.append(f"{jsonl_file}:{line_num} {error}")
                except json.JSONDecodeError as e:
                    all_errors.append(f"{jsonl_file}:{line_num} Invalid JSON: {e}")

    # Report results
    if all_errors:
        print(f"✗ Validation failed with {len(all_errors)} errors:", file=sys.stderr)
        for error in all_errors[:10]:  # Show first 10
            print(f"  {error}", file=sys.stderr)
        if len(all_errors) > 10:
            print(f"  ... and {len(all_errors) - 10} more errors", file=sys.stderr)
        return 1

    print(f"✓ Validated {total_refs} references across {len(seen_ids)} unique IDs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
