#!/usr/bin/env bash
# MkDocs SSG Adapter
# Implements pluggable SSG interface: build | serve

set -euo pipefail

cmd="${1:-build}"

case "$cmd" in
  build)
    echo "→ Building MkDocs Material site..."
    mkdocs build --strict --site-dir dist/mkdocs
    echo "✓ MkDocs build complete: dist/mkdocs/"
    ;;
  serve)
    echo "→ Starting MkDocs dev server..."
    mkdocs serve
    ;;
  *)
    echo "Usage: $0 {build|serve}" >&2
    exit 2
    ;;
esac
