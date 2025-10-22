# Knowledge Base Build System
# Modern task runner using just (https://github.com/casey/just)

set shell := ["bash", "-euo", "pipefail", "-c"]

# SSG views to build (space-separated)
SSG_VIEWS := "mkdocs quarto"

# Default recipe - show help
default:
    @just --list

# Validate all data sources
validate:
    @echo "==> Validating reference database..."
    uv run python tools/validate_refs.py
    @echo "==> Checking note front matter..."
    uv run python tools/check_front_matter.py
    @echo "==> Verifying code snippets..."
    uv run python tools/extract_snippets.py --check-only
    @echo "✓ Validation complete"

# Generate derived artifacts and pages
generate:
    @echo "==> Building reference artifacts..."
    uv run python tools/build_refs.py
    @echo "==> Generating reference pages..."
    uv run python tools/mkdocs_pages.py
    @echo "==> Exporting AI index..."
    uv run python tools/export_ai_index.py
    @echo "✓ Generation complete"

# Build all SSG views
build: validate generate
    @echo "==> Building SSG views: {{SSG_VIEWS}}"
    @for view in {{SSG_VIEWS}}; do \
        echo "  → Building $view..."; \
        ssg/$view/adapter.sh build || exit 1; \
    done
    @echo "✓ Build complete"

# Serve preview of all SSGs (background)
serve:
    @echo "==> Starting preview servers..."
    @for view in {{SSG_VIEWS}}; do \
        echo "  → Starting $view server..."; \
        ssg/$view/adapter.sh serve & \
    done
    @echo "✓ Servers started in background"
    @echo "  Press Ctrl+C to stop"

# Clean all generated artifacts
clean:
    @echo "==> Cleaning generated content..."
    rm -rf data/derived/* references/* dist/* site/* .cache
    rm -f ai/site-index.json
    @echo "✓ Clean complete"

# Run full quality checks (linting, link check, prose)
qa:
    @echo "==> Running quality checks..."
    @echo "  → Python linting..."
    uvx tox -e ruff
    @echo "  → Markdown linting..."
    uvx tox -e quality
    @echo "  → Link checking..."
    lychee --config .lychee.toml 'dist/**/*.html' || echo "⚠ Some links broken"
    @echo "✓ QA complete"

# Run unit tests
test:
    @echo "==> Running tests..."
    uvx tox -e pytest
    @echo "✓ Tests complete"

# Full CI pipeline: validate → generate → build → QA → test
ci: build qa test
    @echo "✓ CI pipeline complete"

# Install Python dependencies
install:
    @echo "==> Installing Python dependencies..."
    uv sync
    @echo "✓ Install complete"

# Set up pre-commit hooks
hooks:
    @echo "==> Installing pre-commit hooks..."
    uv run pre-commit install
    @echo "✓ Hooks installed"

# Initialize development environment
setup: install hooks
    @echo "==> Checking external tools..."
    ./scripts/check-environment.sh || echo "⚠ Some tools missing"
    @echo "✓ Setup complete"

# Show project status
status:
    @echo "==> Project Status"
    @echo ""
    @echo "Notes:      $(find notes -name '*.md' -not -path '*/blog/*' | wc -l) files"
    @echo "Blog posts: $(find notes/blog -name '*.md' 2>/dev/null | wc -l) files"
    @echo "References: $(find data/refs/shards -name '*.jsonl' 2>/dev/null | wc -l) shards"
    @echo "Code:       $(find code -name 'SNIPPETS.yaml' -o -name '*.py' -o -name '*.rs' -o -name '*.sh' | wc -l) files"
    @echo ""
    @echo "Generated:"
    @test -d data/derived && echo "  ✓ Reference artifacts" || echo "  ✗ Reference artifacts"
    @test -d references && echo "  ✓ Reference pages" || echo "  ✗ Reference pages"
    @test -f ai/site-index.json && echo "  ✓ AI index" || echo "  ✗ AI index"
    @test -d dist && echo "  ✓ SSG builds" || echo "  ✗ SSG builds"

# Bootstrap sample content for testing
bootstrap:
    @echo "==> Creating sample content..."
    @mkdir -p data/refs/shards/00
    @mkdir -p notes/blog
    @echo "  → Creating sample reference..."
    @echo '{"id":"sample-2025-test","type":"web","title":"Sample Reference","url":"https://example.com","authors":["Doe, J."],"year":2025,"tags":["sample"],"accessed":"2025-01-01"}' > data/refs/shards/00/sample.jsonl
    @echo "  → Creating sample note..."
    @echo -e '---\nid: sample-note\ntitle: Sample Note\ndate: 2025-01-01\ntags: [sample]\n---\n\n# Sample Note\n\nThis is a sample note citing [@sample-2025-test].' > notes/sample-note.md
    @echo "  → Creating sample blog post..."
    @echo -e '---\ntitle: Hello World\ndate: 2025-01-01\ntags: [blog]\n---\n\n# Hello World\n\nWelcome to the blog!' > notes/blog/2025-01-01-hello-world.md
    @echo "  → Creating tags vocabulary..."
    @echo -e 'allowed_tags:\n  - sample\n  - blog\n  - test' > data/refs/tags.yaml
    @echo "  → Creating empty snippet registry..."
    @echo 'snippets: {}' > code/SNIPPETS.yaml
    @echo "✓ Bootstrap complete"
