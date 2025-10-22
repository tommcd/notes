#!/usr/bin/env python3
"""
Reference Database Builder

Transforms JSONL references to output formats:
- CSL JSON (data/derived/references.csl.json) for Quarto
- BibTeX (data/derived/references.bib) for MkDocs
"""

import json
import sys
from pathlib import Path


def build_csl_json(refs: list[dict], output_file: Path):
    """Build CSL JSON format."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    csl_refs = []
    for ref in refs:
        # Minimal CSL JSON conversion
        csl_ref = {
            "id": ref["id"],
            "type": ref.get("type", "webpage"),
            "title": ref["title"],
            "URL": ref["url"],
        }
        if "authors" in ref:
            csl_ref["author"] = [{"literal": author} for author in ref["authors"]]
        if "year" in ref:
            csl_ref["issued"] = {"date-parts": [[ref["year"]]]}

        csl_refs.append(csl_ref)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(csl_refs, f, indent=2)


def build_bibtex(refs: list[dict], output_file: Path):
    """Build BibTeX format."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        for ref in refs:
            ref_type = ref.get("type", "misc")
            ref_id = ref["id"]
            title = ref["title"]
            url = ref["url"]

            f.write(f"@{ref_type}{{{ref_id},\n")
            f.write(f"  title = {{{title}}},\n")
            f.write(f"  url = {{{url}}},\n")

            if "authors" in ref:
                authors = " and ".join(ref["authors"])
                f.write(f"  author = {{{authors}}},\n")
            if "year" in ref:
                f.write(f"  year = {{{ref['year']}}},\n")

            f.write("}\n\n")


def main():
    """Main builder entry point."""
    refs_dir = Path("data/refs/shards")
    csl_output = Path("data/derived/references.csl.json")
    bib_output = Path("data/derived/references.bib")

    if not refs_dir.exists():
        print(f"✓ No references to build ({refs_dir} not found)")
        csl_output.parent.mkdir(parents=True, exist_ok=True)
        csl_output.write_text("[]")
        bib_output.write_text("")
        return 0

    # Load all references
    refs = []
    for jsonl_file in refs_dir.rglob("*.jsonl"):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    refs.append(json.loads(line))

    if not refs:
        print("✓ No references to build (no records found)")
        csl_output.parent.mkdir(parents=True, exist_ok=True)
        csl_output.write_text("[]")
        bib_output.write_text("")
        return 0

    # Build outputs
    build_csl_json(refs, csl_output)
    build_bibtex(refs, bib_output)

    print(f"✓ Built {len(refs)} references")
    print(f"  → {csl_output}")
    print(f"  → {bib_output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
