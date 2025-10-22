#!/usr/bin/env bash
# Quarto SSG Adapter
# Implements pluggable SSG interface: build | serve

set -euo pipefail

cmd="${1:-build}"

case "$cmd" in
  build)
    echo "→ Building Quarto site..."
    quarto render --output-dir dist/quarto
    echo "✓ Quarto build complete: dist/quarto/"
    ;;
  serve)
    echo "→ Starting Quarto preview server..."
    quarto preview
    ;;
  *)
    echo "Usage: $0 {build|serve}" >&2
    exit 2
    ;;
esac
