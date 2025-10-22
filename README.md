# Tom's Knowledge Base

A personal knowledge management system combining notes, blog, and a reference library with 200k+ bookmarks.

## Overview

This project is a **Markdown-first, Git-backed knowledge base** with:

- **Notes** - Zettelkasten-style interconnected notes
- **Blog** - Chronological posts with RSS feeds
- **References** - Citation database in sharded JSONL format
- **Code Snippets** - Canonical examples with registry
- **AI/RAG Ready** - Machine-readable indices for LLM consumption
- **Pluggable SSGs** - Multiple views (MkDocs Material + Quarto)

## Architecture

See [SPEC.md](SPEC.md) for the complete specification and [AGENTS.md](AGENTS.md) for development workflow.

### Key Components

- **Content**: `notes/` (Markdown), `data/refs/` (JSONL references)
- **Tools**: `tools/*.py` (validation, generation, export)
- **SSG Adapters**: `ssg/{mkdocs,quarto}/adapter.sh`
- **AI Guidance**: `ai/llm.txt`, `ai/site-index.json`
- **Build System**: `justfile` (modern task runner)

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for package management
- [just](https://github.com/casey/just) for task running (optional but recommended)
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) for SSG
- [Quarto](https://quarto.org/) for alternative SSG view

### Installation

```bash
# Install Python dependencies
uv sync

# Install MkDocs and plugins
pip install mkdocs-material mkdocs-material-extensions \
  mkdocs-blog-plugin mkdocs-bibtex \
  mkdocs-roamlinks-plugin mkdocs-awesome-pages-plugin

# Install Quarto (see https://quarto.org/docs/get-started/)
```

### Build the Site

```bash
# Validate all content
python3 tools/validate_refs.py
python3 tools/check_front_matter.py
python3 tools/extract_snippets.py --check-only

# Generate derived artifacts
python3 tools/build_refs.py
python3 tools/mkdocs_pages.py
python3 tools/export_ai_index.py

# Build MkDocs view
./ssg/mkdocs/adapter.sh build

# Or use justfile (if installed)
just validate
just generate
just build
```

### Preview Locally

```bash
# MkDocs
./ssg/mkdocs/adapter.sh serve

# Quarto
./ssg/quarto/adapter.sh serve

# Or both (requires just)
just serve
```

## Development

### Quick Start with Dev Container (Recommended)

1. Install [Docker](https://www.docker.com/products/docker-desktop) and [VS Code](https://code.visualstudio.com/)
1. Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
1. Open this project in VS Code
1. Click "Reopen in Container" when prompted
1. Wait for setup to complete (~2-3 minutes first time)

### Local Development Setup

Set up everything with a single command:

```bash
# One-command setup: installs everything you need
./scripts/setup-environment.sh

# Verify everything is ready
./scripts/check-environment.sh
```

This automatically installs:

- **uv** package manager
- **Python 3.12**
- **External tools** (shellcheck, shfmt, etc.)
- **Python dependencies**
- **Tox** for test orchestration
- **Pre-commit hooks**

### Testing & Quality Checks

```bash
# Run all checks (linting, formatting, tests)
uvx tox

# List all available environments
uvx tox list

# Specific checks
uvx tox -e ruff          # Python linting
uvx tox -e pytest        # Run tests
uvx tox -e quality       # Quality tests
```

### Pre-commit Hooks

```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

## Requirements

- Python 3.12+
- uv for package management

## Project Structure

```
notes/
├── notes/              # Markdown notes and blog posts
├── data/
│   ├── refs/          # Reference database (JSONL)
│   └── derived/       # Generated CSL/BibTeX (gitignored)
├── references/         # Generated reference pages (gitignored)
├── code/              # Canonical code examples
├── ai/                # AI/LLM guidance files
├── ssg/               # SSG adapters (mkdocs, quarto)
├── tools/             # Python build tools
├── src/notes/         # Python package for tooling
├── tests/             # Test suite
├── justfile           # Task runner recipes
├── mkdocs.yml         # MkDocs configuration
├── _quarto.yml        # Quarto configuration
├── SPEC.md            # Project specification
└── AGENTS.md          # Agent development guide
```

## Content Organization

### Notes (`notes/`)

Personal knowledge base entries with front matter:

```yaml
---
id: unique-id
title: Note Title
date: 2025-01-01
tags: [tag1, tag2]
---

# Content

Citations: [@reference-id]
Wikilinks: [[Other Note]]
```

### Blog (`notes/blog/`)

Chronological posts with date-prefixed filenames:
- `2025-01-01-post-title.md`
- RSS/Atom feeds generated automatically

### References (`data/refs/shards/`)

JSONL reference database, sharded by hash:

```json
{"id":"smith2025-example","type":"web","title":"...","url":"https://...","authors":["Smith, J."],"year":2025,"tags":["tag"]}
```

### Code (`code/`)

Canonical examples with snippet registry (`SNIPPETS.yaml`) for inclusion in notes.

## Specification-Driven Development

This project follows **spec-driven development** using [GitHub Spec Kit](https://github.com/github/spec-kit):

1. Features defined in [SPEC.md](SPEC.md)
2. Implementation guided by [AGENTS.md](AGENTS.md)
3. Tasks tracked via GitHub issues labeled `spec:ready`
4. PRs reference issues and include acceptance tests

### Agent Workflow

Multiple AI agents (Amazon Q, Claude Code, Codex) can work in parallel:

- Each agent claims issues in their domain (see [AGENTS.md](AGENTS.md#file-ownership))
- Agents follow conventional commits and PR checklists
- Integration tested via `just build` before merge

See [AGENTS.md section 11](AGENTS.md#development-workflow-spec-driven) for details.

## CI/CD Pipeline

GitHub Actions workflow:
1. **Validate** - Schema, front matter, snippets
2. **Generate** - CSL JSON, BibTeX, reference pages, AI index
3. **Build** - Both MkDocs and Quarto views
4. **QA** - Link check (lychee), prose (Vale), accessibility (pa11y)
5. **Deploy** - GitHub Pages

## Roadmap

- **v0.1** - Skeleton, validators, MkDocs, basic reference index ← **You are here**
- **v0.2** - Quarto view, AI artifacts, snippet integration
- **v0.3** - Importers (Chrome/Firefox/Zotero), nightlies, feeds
- **v1.0** - Scale test with ≥50k refs, split to submodule

## License

- **Content** (notes, blog): CC BY-SA 4.0
- **Code**: MIT License

## Acknowledgments

- Project structure from Python Project Template
- Spec-driven approach inspired by [GitHub Spec Kit](https://github.com/github/spec-kit)
