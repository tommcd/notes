# AGENTS.md

> Coding agents: Amazon Q Developer, Claude Code, Codex.\
> Mode: specification‑driven, PR‑first.

## 1. Rules of Engagement

- Work **issue‑driven**. Only change files linked to an open issue labeled `spec:ready` or `good-first-task`.
- Prefer small PRs (≤300 LOC diff) with tests.
- Use the `just` tasks; do not invent alternative build steps.
- Never commit generated artifacts from `/data/derived/`, `/references/`, or `/dist/`.

## 2. Local Commands

```bash
# validation
just validate

# generate derived artifacts & pages
just generate

# full build of all SSGs
just build

# preview
just serve
```

## 3. File Ownership

File ownership defines primary responsibility, not exclusive access. Agents should:
- Focus on files in their domain
- Coordinate cross-domain changes via issues
- Request reviews from domain owners on PRs

Ownership map:
- `tools/*.py` → **Python assistant** (validation, generation, build scripts)
- `mkdocs.yml`, theme, blog → **Web assistant** (MkDocs configuration)
- `_quarto.yml` and listings → **Web assistant** (Quarto configuration)
- `ssg/*/adapter.sh` → **SSG owner** (pluggable adapter implementations)
- `data/refs/**` → **Data owner** (reference DB; others read‑only except via importers)
- `code/**` + `SNIPPETS.yaml` → **Code owner** (canonical examples and registry)
- `notes/**/*.md` → **Content owner** (Tom; agents may contribute via PR)
- `SPEC.md`, `AGENTS.md` → **Architect** (Tom; agents may propose changes)

## 4. Coding Standards

- Python: 3.x, type hints, `ruff`, `pytest`, `mypy` optional.
- Bash: POSIX with `set -euo pipefail`.
- Markdown: mdformat/markdownlint; 80–100 col soft wrap.
- Deterministic outputs; don’t embed timestamps.

## 5. Tests Required in PRs

- Unit tests for any new tool or importer.
- Snapshot tests for generated reference/tag pages.
- Snippet integrity tests when touching `SNIPPETS.yaml` or `code/**`.
- CI must pass: validate → generate → build → QA (lychee, Vale, markdownlint, pa11y).

## 6. Commits & PRs

- Conventional commits: `feat:`, `fix:`, `docs:`, `build:`, `test:`, `refactor:`.
- PR template must include: scope, rationale, test evidence (command logs), and checklist boxes for QA gates.

### PR Checklist (agents must tick)

- [ ] All tests passing (`just build` succeeds without errors)
- [ ] Conventional commit format used (`feat:`, `fix:`, `docs:`, etc.)
- [ ] No generated artifacts committed (`/data/derived/`, `/references/`, `/dist/`)
- [ ] Documentation updated where relevant (README, SPEC, inline comments)
- [ ] QA gates passed:
  - [ ] Lychee (link check)
  - [ ] Vale (prose style)
  - [ ] markdownlint (Markdown formatting)
  - [ ] pa11y (accessibility, if UI changes)
- [ ] Issue reference included in PR description (`Closes #123`)
- [ ] Breaking changes noted in PR description and CHANGELOG

## 7. Secrets & Safety

- No external calls requiring secrets.
- Do not write credentials into configs.
- If a task requests external API usage, stop and open an issue for review.

## 8. SSG Adapter Contract (for agents)

Implement a new adapter under `ssg/<name>/adapter.sh` supporting:

```bash
$ ssg/<name>/adapter.sh build   # write to dist/<name>/
$ ssg/<name>/adapter.sh serve   # optional
```

Inputs are the generated artifacts and Markdown content. Do not mutate source trees.

## 9. Definition of Done per Work Package

- Code + tests committed.
- `just build` succeeds.
- Deployed preview artifact attached (CI build logs).
- Updated docs where relevant (README, SPEC snippets).

## 10. Open Questions (to confirm with Owner)

- Preferred CSL style (default: IEEE).
- Blog taxonomy depth and tag display.
- Hash fanout (26 vs 256 shards) for refs.
- Which SSG is canonical for SEO (set canonical links).

## 11. Development Workflow (Spec-Driven)

This project uses **GitHub Spec Kit** for specification-driven development:

### Getting Started with Spec Kit

```bash
# Install Spec Kit globally
npm i -g @github/spec-kit

# Initialize (first time only)
speckit init

# Generate task plan from SPEC.md
speckit.plan
```

### Issue-Driven Development

1. **Find work:** Browse issues labeled `spec:ready` or `good-first-task`
2. **Claim issue:** Comment on issue or assign yourself
3. **Create branch:** `git checkout -b feat/issue-123-short-description`
4. **Implement:** Follow SPEC.md acceptance criteria
5. **Test locally:** Run `just build` before pushing
6. **Open PR:** Reference issue (`Closes #123`), complete PR checklist
7. **Review:** Respond to feedback, update based on spec validation
8. **Merge:** Maintainer merges after approval; CI deploys

### Multi-Agent Coordination

When multiple agents work in parallel:
- **Avoid conflicts:** Different agents work on different directories (see File Ownership)
- **Communication:** Use issue comments to coordinate cross-domain work
- **Dependencies:** Mark dependent issues with `blocked-by: #123` labels
- **Integration:** After parallel work, run full `just build` to verify integration

### Spec Kit Commands Reference

- `speckit.plan` — Generate implementation task graph
- `speckit.review` — Validate implementation against spec
- `speckit.refine` — Update spec based on implementation learnings
- `speckit init` — Scaffold new spec files

### Example Agent Session

```bash
# 1. Agent reads issue #42 labeled "spec:ready"
# Issue: "Implement reference validator (tools/validate_refs.py)"

# 2. Agent checks SPEC.md section 7.1 for acceptance criteria
cat SPEC.md  # Review validation requirements

# 3. Agent implements
git checkout -b feat/42-reference-validator
# ... writes tools/validate_refs.py and tests ...

# 4. Agent tests locally
just validate     # Should pass with sample data
just build        # Should complete successfully

# 5. Agent commits and pushes
git add tools/validate_refs.py tests/unit/test_validate_refs.py
git commit -m "feat: implement reference validator

Closes #42

- JSON Schema validation for reference records
- Unique ID enforcement
- Tag vocabulary validation against tags.yaml
- 100% test coverage"
git push origin feat/42-reference-validator

# 6. Agent opens PR via GitHub CLI or web UI
gh pr create --title "feat: implement reference validator" \
  --body "Closes #42. See commit message for details."
```

