# Site Map

Human-readable overview of content organization.

## Directory Structure

```
/
├── notes/              # Markdown notes
│   ├── *.md           # Individual notes
│   └── blog/          # Blog posts
│       └── YYYY-MM-DD-slug.md
├── references/         # Reference library (generated)
│   ├── index.md       # Master index
│   ├── tags/          # References by tag
│   └── *.md           # Individual reference pages
├── code/              # Canonical code examples
│   ├── python/
│   ├── rust/
│   ├── bash/
│   └── SNIPPETS.yaml  # Snippet registry
├── data/
│   ├── refs/          # Reference database (JSONL)
│   └── derived/       # Generated artifacts
└── ai/
    ├── llm.txt        # This guidance file
    ├── map.md         # This map
    └── site-index.json # Machine-readable index
```

## Content Types

### Notes (`/notes/`)

Personal knowledge base entries:
- Atomic concepts (Zettelkasten principle)
- Interconnected via wikilinks `[[Page]]`
- Cite references via `[@id]`
- Tags for categorization

### Blog (`/notes/blog/`)

Chronological articles:
- Date-prefixed filenames
- RSS/Atom feeds available
- Listed at `/blog/index.html`

### References (`/references/`)

Citation library:
- Web articles, papers, books
- Backlinks to citing notes
- Organized by tags
- Wayback Machine snapshots where available

### Code (`/code/`)

Canonical examples:
- Python, Rust, Bash, etc.
- Snippet system for inclusion in notes
- Tested and validated

## Navigation Patterns

### By Topic

1. Start at `/notes/index.html`
2. Browse by tag or search
3. Follow wikilinks between related notes

### By Date (Blog)

1. Visit `/blog/index.html`
2. Browse chronologically
3. Filter by category

### By Reference

1. Visit `/references/index.html`
2. Browse by tag (e.g., `/references/tags/python.html`)
3. View reference details with backlinks

## Search Strategy

- **Full-text:** Use site search (top-right)
- **Tags:** Browse tag pages
- **Wikilinks:** Follow connections between notes
- **Citations:** Click `[@ref]` to view reference

## Build Process

Content is static-generated:
1. Validate (schema, links)
2. Generate (reference pages, indices)
3. Build (MkDocs + Quarto)
4. Deploy (GitHub Pages)

Updated on every commit to main branch.
