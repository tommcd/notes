# Session Command History
## Date: 2025-10-22

This file documents the key commands run during the initial setup session.

## Git Setup
```bash
# Configure personal git identity for ~/git/tommcd/
cat << 'EOT' > ~/.gitconfig-personal
[user]
	name = Thomas McDermott
	email = tcmcdermott@gmail.com
EOT

# Add conditional include to ~/.gitconfig
echo "" >> ~/.gitconfig
echo "# Personal repositories configuration" >> ~/.gitconfig
echo "[includeIf \"gitdir:~/git/tommcd/\"]" >> ~/.gitconfig
echo "    path = ~/.gitconfig-personal" >> ~/.gitconfig
```

## Repository Initialization
```bash
cd ~/git/tommcd/notes
git init
git branch -M main
git add .
git commit -m "feat: initial knowledge base structure"
```

## GitHub Setup
```bash
# Create repository
gh repo create notes --public --description "My notes, blog, and references" --source . --remote origin

# Push to GitHub
git push -u origin main
```

## Clone Other Repositories
```bash
cd ~/git/tommcd
git clone https://github.com/tommcd/tommcd.github.io.git
git clone https://github.com/tommcd/tommcd.git
```

## Directory Restructure
```bash
cd ~/git/tommcd/notes
mkdir -p docs dev

# Move content to docs/
git mv notes docs/notes
git mv index.md docs/index.md
git mv references docs/references

# Move project docs to dev/
git mv IMPLEMENTATION_SUMMARY.md dev/
```

## Configuration Updates
```bash
# Updated mkdocs.yml:
# - docs_dir: docs
# - edit_uri: edit/main/docs/
# - blog_dir: notes/blog

# Updated _quarto.yml (pending)
# - Point to docs/ directory
```

## GitHub Pages Setup
```bash
# Created .github/workflows/pages.yml
# Enabled GitHub Pages via API
gh api -X POST repos/tommcd/notes/pages -f build_type=workflow -f source[branch]=main
```

## Key Files Created
- `SPEC.md` - Project specification (at root)
- `AGENTS.md` - Agent development guide (at root)
- `dev/IMPLEMENTATION_SUMMARY.md` - Implementation details
- `.github/workflows/pages.yml` - CI/CD pipeline
- `justfile` - Build task runner
- `mkdocs.yml` - MkDocs configuration
- `_quarto.yml` - Quarto configuration
- Sample content in `docs/notes/` and `docs/notes/blog/`

## Tools Created
- `tools/validate_refs.py` - Reference validator
- `tools/check_front_matter.py` - Front matter validator
- `tools/extract_snippets.py` - Snippet validator
- `tools/build_refs.py` - Reference builder (CSL/BibTeX)
- `tools/mkdocs_pages.py` - Page generator
- `tools/export_ai_index.py` - AI index exporter

## Validation & Build
```bash
# Validate
python3 tools/validate_refs.py
python3 tools/check_front_matter.py
python3 tools/extract_snippets.py --check-only

# Generate
python3 tools/build_refs.py
python3 tools/mkdocs_pages.py
python3 tools/export_ai_index.py

# Build (when just is installed)
just validate
just generate
just build
```

## URLs
- Main site: https://tommcd.github.io
- Notes site: https://tommcd.github.io/notes/ (pending deployment)
- GitHub repo: https://github.com/tommcd/notes
- Profile: https://github.com/tommcd
