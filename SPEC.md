# SPEC.md

> Product: Markdown‑first Knowledge & Reference Publishing Platform\
> Owner: Tom\
> Version: 0.1 (draft)

## 1. Purpose

A durable, Git‑backed knowledge base with: notes, blog, citation database, external code snippets, AI guidance, and pluggable static‑site generators (SSGs). Primary source of truth is Markdown and a sharded JSONL reference DB.

## 2. Outcomes / Success Criteria

- Public site builds two views: **/mkdocs/** (MkDocs Material) and **/quarto/** (Quarto).
- Notes render with nav, search, tags. Blog index and RSS present.
- Citations `[@id]` resolve from the DB; reference detail pages show backlinks to notes.
- Code snippets are external files referenced by **snippet IDs** and validated in CI.
- AI artifacts available: `/ai/llm.txt`, `/ai/site-index.json`.
- CI: validate → generate → build → QA → deploy to GitHub Pages.
- Split‑ready: references can move to a submodule with no content changes.
- **Scale target:** Support ≥200,000 references with reasonable build times (< 5 min CI).

## 3. Non‑Goals

- No server‑side app; static hosting only.
- No authentication/authorization.
- No editorial workflow beyond Git PRs.

## 4. High‑Level Architecture

```
repo/
  notes/                         # Markdown notes (nested by domain)
  code/                          # Canonical example sources
    python/ rust/ bash/ ...
    SNIPPETS.yaml                # snippet registry (IDs → file selectors)
  data/
    refs/                        # sharded JSONL (00..ff/ or a..z.jsonl)
      shards/**.jsonl
      tags.yaml
    derived/                     # build outputs (gitignored)
      references.csl.json
      references.bib
  references/                    # GENERATED pages (gitignored; emitted to dist)
  ai/
    llm.txt
    map.md
    site-index.schema.json
    site-index.json              # generated
  ssg/
    mkdocs/adapter.sh            # pluggable SSGs
    quarto/adapter.sh
    zola/adapter.sh (stub)
  tools/                         # Python build/validate utilities
    validate_refs.py
    build_refs.py
    mkdocs_pages.py
    extract_snippets.py
    check_front_matter.py
    export_ai_index.py
  site_root/index.html           # links to /mkdocs/ and /quarto/
  mkdocs.yml
  _quarto.yml
  justfile (and minimal Makefile for CI if desired)
  .github/workflows/{pages.yml,nightly.yml}
```

## 5. Data Contracts

### 5.1 Note front matter

```yaml
---
id: wsl-basics                 # stable, unique
title: WSL basics
date: 2025-10-19               # ISO date
tags: [wsl, windows]
---
```

### 5.2 Reference record (JSONL source of truth)

One object per line; sharded across files.

```json
{"id":"smith2021-sql-inj","type":"web","title":"…","url":"https://…",
 "authors":["Smith, J."],"year":2021,"tags":["security","sql"],
 "accessed":"2025-10-19","archived_url":"https://web.archive.org/…",
 "notes":["wsl-basics"]}
```

- Required: `id,title,url`.
- Nice‑to‑have: `authors,year,tags,accessed,archived_url,notes[]`.

### 5.3 Snippet registry (SNIPPETS.yaml)

```yaml
wsl-list-distros:
  file: bash/wsl_list.sh
  region: list            # between '# region: list' … '# endregion'
py-parse-json:
  file: python/json_tools.py
  function: parse_json    # by symbol
rs-hash-ids:
  file: rust/id_hash/src/lib.rs
  lines: 12-45
```

## 6. SSG Adapter Contract (Pluggable)

- **Inputs:** `notes/**.md`, `references/**.md` (generated), `data/derived/{references.csl.json,references.bib}`, `code/**`, `assets/**`.
- **Outputs:** `dist/<view>/`.
- **Interface:** each adapter exposes `build` and `serve`.

```
ssg/<name>/adapter.sh build   # produce dist/<name>/
ssg/<name>/adapter.sh serve   # local preview (optional)
```

- Initial views: `mkdocs`, `quarto`. Future: `zola`, `hugo`, `eleventy`.

## 7. Generation Pipeline

1. **Validate**
   - JSON Schema over refs; unique IDs; allowed tags.
   - Front matter checks (id/title/date/tags).
   - Snippet registry exists and selectors resolve.
2. **Generate**
   - Concat+transform refs → `references.csl.json` and `.bib`.
   - Build reference pages: master index; per‑tag; per‑reference with backlinks by scanning notes for `[@id]`.
   - Export AI index `/ai/site-index.json`.
3. **Build SSGs**
   - `ssg/mkdocs/adapter.sh build` (MkDocs Material + blog plugin).
   - `ssg/quarto/adapter.sh build` (Quarto website listings and citations).
4. **QA**
   - Link check (lychee) on `dist/**`.
   - Prose/style (Vale + markdownlint + codespell).
   - Accessibility (pa11y) on key pages.
   - Performance thresholds (build time, page size).
5. **Deploy**
   - Upload `dist/` to GitHub Pages.
   - Nightly job reruns deep link check and reference validation.

## 8. Blog & Feeds

- MkDocs Material blog plugin; posts under `notes/blog/` with front matter `title,date,tags`.
- RSS/Atom via plugin (MkDocs) and Quarto listing feed if needed.

## 9. Governance & Policies

- **Tags:** controlled vocabulary in `data/refs/tags.yaml`; CI rejects unknown tags.
- **IDs:** kebab‑case; deterministic; immutable; duplicates rejected.
- **Licenses:** site content CC BY‑SA 4.0; code MIT.
- **Backups:** periodic archive of `notes/` and `data/refs/`.
- **Security:** pinned plugin versions; Dependabot/Renovate; minimal CI tokens.
- **Split readiness:** all tools read refs via `REFS_DIR` (default `data/refs`).

## 10. Acceptance Tests (Initial)

- Unit: schema validation; de‑dup; snippet extractors.
- Integration: small fixture repo → both SSG outputs exist; citations render; backlinks present.
- Golden snapshots for a few generated pages.
- QA gates green in CI.

## 11. Roadmap (v0 → v1)

- v0.1: skeleton, validators, MkDocs build, basic references index.
- v0.2: Quarto view, AI artifacts, snippet integration.
- v0.3: Importers (Chrome/Firefox/Pocket/Zotero), nightlies, feeds.
- v1.0: scale test with ≥50k refs; docs; split to submodule if needed.

## 12. MkDocs Plugin Dependencies

Core plugins for MkDocs Material view:

- **mkdocs-material** — Material Design theme with blog support
- **mkdocs-material-extensions** — Extended Markdown syntax
- **mkdocs-blog-plugin** (or **mkdocs-blogging-plugin**) — Blog listings, RSS/Atom feeds
- **mkdocs-bibtex** — Citation rendering from BibTeX
- **mkdocs-roamlinks-plugin** — Wikilink `[[page]]` support
- **mkdocs-awesome-pages-plugin** — Navigation customization
- **mkdocs-git-revision-date-localized-plugin** (optional) — Last-modified timestamps

Install via:
```bash
pip install mkdocs-material mkdocs-material-extensions \
  mkdocs-blog-plugin mkdocs-bibtex \
  mkdocs-roamlinks-plugin mkdocs-awesome-pages-plugin
```

## 13. Development Workflow with Spec Kit

This project follows **specification-driven development** using [GitHub Spec Kit](https://github.com/github/spec-kit):

1. **Initialize:** `speckit init` to scaffold spec structure.
2. **Plan:** `speckit.plan` generates task graph from SPEC.md.
3. **Implement:** Agents (Amazon Q, Claude Code, Codex) execute tasks from GitHub issues.
4. **Review:** `speckit.review` validates implementation against spec.
5. **Iterate:** `speckit.refine` updates spec based on learnings.

Workflow:
- Each feature starts as a spec in `/specs/*.md`.
- Spec Kit generates GitHub issues labeled `spec:ready`.
- Agents claim issues, implement in PRs, reference issue numbers.
- Maintainer reviews PR against spec acceptance criteria.
- Merge triggers CI pipeline: validate → generate → build → deploy.

