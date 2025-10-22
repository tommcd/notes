# Development Scripts

This directory contains scripts for setting up, checking, and managing the development environment.

## Quick Start

```bash
# Full environment setup (one command)
./scripts/setup-environment.sh

# Verify everything is working
./scripts/check-environment.sh

# Run tests
uvx tox
```

## Tox Integration

**All scripts in this directory are exposed via tox** for a unified interface. See [README.md](../README.md#testing--quality-checks) for the comprehensive tox command reference.

**Quick reference**:

```bash
# Environment management
uvx tox -e setup-environment     # ./scripts/setup-environment.sh
uvx tox -e check-environment     # ./scripts/check-environment.sh
uvx tox -e clean-environment     # ./scripts/clean-environment.sh

# Tool management
uvx tox -e setup-tools           # python3 scripts/setup-external-tools.py
uvx tox -e check-tools           # python3 scripts/check-tools.py
uvx tox -e clean-tools           # python3 scripts/clean-tools.py

# Utilities
uvx tox -e show-tox-commands     # python3 scripts/show-tox-commands.py
uvx tox -e sync-precommit-versions # python3 scripts/sync-precommit-versions.py
```

**When adding a new tool, remember to add a tox environment** in `tox.ini` if appropriate. Example:

```ini
[testenv:your-new-tool]
description = Description of what it does
package = skip
dependency_groups =
allowlist_externals = python3
commands = python3 scripts/your-new-tool.py
```

## Scripts Overview

### Environment Management

#### setup-environment.sh

**Purpose**: Complete development environment setup

**What it does**:

1. Installs uv (Python package manager)
1. Installs Python 3.12 (if needed)
1. Installs external tools (shellcheck, shfmt, hadolint, etc.)
1. Installs Python dependencies
1. Installs tox globally
1. Installs pre-commit hooks

**Usage**:

```bash
./scripts/setup-environment.sh              # Local development
./scripts/setup-environment.sh --devcontainer # Devcontainer mode
./scripts/setup-environment.sh --dry-run    # Preview only
```

#### check-environment.sh

**Purpose**: Validate development environment is ready

**What it checks**:

- Python version
- uv package manager
- External tools (with version matching)
- Git and pre-commit hooks
- Python dependencies (pre-commit, tox)

**Usage**:

```bash
./scripts/check-environment.sh
```

**Exit codes**:

- `0` - Environment ready
- `1` - One or more issues detected

#### clean-environment.sh

**Purpose**: Remove generated files to simulate fresh clone

**What it removes**:

- Virtual environments (.venv)
- Tox environments (.tox)
- Python caches (__pycache__, .pytest_cache)
- Build artifacts (dist/, build/, \*.egg-info)
- Pre-commit git hooks
- Coverage files
- Test output directories

**Usage**:

```bash
./scripts/clean-environment.sh              # Project only (safe)
./scripts/clean-environment.sh --deep       # + global pre-commit cache
./scripts/clean-environment.sh --tools      # + uninstall external tools
./scripts/clean-environment.sh --deep --tools # Full cleanup
```

**Warning**: `--tools` flag requires sudo and uninstalls system-wide tools!

### External Tools Management

This project uses a **Markdown-driven plugin system** for managing external tools like shellcheck, shfmt, hadolint, etc.

#### setup-external-tools.py

**Purpose**: Install external tools from Markdown plugins

**Usage**:

```bash
python3 scripts/setup-external-tools.py              # Install all tools
python3 scripts/setup-external-tools.py --tool hadolint # Specific tool
python3 scripts/setup-external-tools.py --dry-run    # Preview only
```

**How it works**:

1. Reads tool versions from [pyproject.toml](../pyproject.toml) `[tool.external-tools]`
1. Discovers Markdown plugins in [scripts/tools/](tools/)
1. Checks current versions
1. Installs/upgrades tools as needed

#### check-tools.py

**Purpose**: Validate external tool versions

**Usage**:

```bash
python3 scripts/check-tools.py              # Check all tools
python3 scripts/check-tools.py --tool hadolint # Check specific tool
python3 scripts/check-tools.py --quiet      # Exit code only
```

**Exit codes**:

- `0` - All tools correct
- `1` - Missing or wrong versions

#### clean-tools.py

**Purpose**: Uninstall external tools

**Usage**:

```bash
python3 scripts/clean-tools.py              # Uninstall all (with prompt)
python3 scripts/clean-tools.py --tool hadolint # Uninstall specific tool
python3 scripts/clean-tools.py --dry-run    # Preview only
python3 scripts/clean-tools.py --force      # Skip confirmation
```

**Warning**: Requires sudo for most tools. Use `--dry-run` first!

## External Tools Plugin System

### Overview

External tools are managed through a **Markdown-driven plugin system** where each tool has a Markdown file that serves as both:

- **Documentation** for users (how to install, use, test)
- **Automation source** for scripts (what commands to run)

This ensures documentation never drifts from reality.

### How It Works

1. **Markdown Plugin** ([scripts/tools/hadolint.md](tools/hadolint.md) example):

   - Contains labeled code blocks: `check-version`, `install`, `uninstall`
   - Includes manual testing examples
   - Documents tool usage and configuration

1. **Python Framework** ([scripts/lib/tool_plugin.py](lib/tool_plugin.py)):

   - Parses Markdown files
   - Extracts and executes code blocks
   - Handles version substitution (`{VERSION}` placeholder)

1. **Version Management** ([pyproject.toml](../pyproject.toml)):

   - All tool versions in `[tool.external-tools]` section
   - Single source of truth for expected versions

### Available Tools

Current external tools managed by the plugin system:

| Tool | Version | Purpose | Plugin |
|------|---------|---------|--------|
| hadolint | 2.14.0 | Dockerfile linter | [hadolint.md](tools/hadolint.md) |
| lychee | 0.20.1 | Link checker | [lychee.md](tools/lychee.md) |
| markdownlint-cli2 | 0.18.1 | Markdown linter | [markdownlint-cli2.md](tools/markdownlint-cli2.md) |
| shellcheck | 0.11.0 | Shell script linter | [shellcheck.md](tools/shellcheck.md) |
| shfmt | 3.10.0 | Shell formatter | [shfmt.md](tools/shfmt.md) |
| taplo | 0.9.3 | TOML formatter | [taplo.md](tools/taplo.md) |

### Adding a New Tool

**Time**: ~15 minutes

**Steps**:

1. **Create Markdown plugin** in `scripts/tools/yourtool.md`:

   ```bash
   cp scripts/tools/TEMPLATE.md scripts/tools/yourtool.md
   # Edit the file with your tool's information
   ```

1. **Add version to pyproject.toml**:

   ```toml
   [tool.external-tools]
   yourtool = "1.2.3"
   ```

1. **Test manually**:

   ```bash
   # Copy commands from your Markdown file and test them
   # This validates the documentation before automation runs it
   ```

1. **Test with Python orchestrator**:

   ```bash
   python3 scripts/setup-external-tools.py --tool yourtool --dry-run
   python3 scripts/setup-external-tools.py --tool yourtool
   ```

That's it! The tool is now managed by the plugin system.

### Markdown Plugin Format

Each tool plugin must have these sections:

#### Required Code Blocks

**Check Version** (`check-version` label):

````markdown
## Check Version

```bash check-version
yourtool --version 2>&1 | grep -oP 'yourtool \K[\d.]+'
````

````

**Install** (`install` label):
```markdown
## Install

```bash install
wget -q "https://example.com/yourtool-v{VERSION}.tar.gz"
tar -xzf "yourtool-v{VERSION}.tar.gz"
sudo mv yourtool /usr/local/bin/yourtool
sudo chmod +x /usr/local/bin/yourtool
````

````

**Uninstall** (`uninstall` label):
```markdown
## Uninstall

```bash uninstall
sudo rm -f /usr/local/bin/yourtool
````

````

#### Recommended Sections

- **Prerequisites**: Dependencies or requirements
- **Manual Testing**: Copy-paste examples for manual validation
- **Usage in This Project**: How the tool is used here
- **Version Management**: How to update versions
- **Configuration**: Tool-specific config files
- **Troubleshooting**: Common issues and solutions

See [TEMPLATE.md](tools/TEMPLATE.md) for a complete example.

### Version Placeholder

Use `{VERSION}` in install commands - it's automatically replaced:

**Template**:
```bash
wget "https://example.com/tool-v{VERSION}.tar.gz"
````

**After substitution** (if version is `1.2.3`):

```bash
wget "https://example.com/tool-v1.2.3.tar.gz"
```

### Manual Testing First

**Important**: Always test commands manually before automation!

1. Copy commands from your Markdown file
1. Paste into terminal and run
1. Verify they work as expected
1. Only then let automation use them

This validates both documentation and automation at once.

## Framework Architecture

### Directory Structure

```
scripts/
├── README.md                      # This file
├── setup-environment.sh           # Main setup script (bash)
├── check-environment.sh           # Environment validation (bash)
├── clean-environment.sh           # Cleanup script (bash)
├── setup-external-tools.py        # Tool installer (Python)
├── check-tools.py                 # Tool version checker (Python)
├── clean-tools.py                 # Tool uninstaller (Python)
├── lib/
│   ├── __init__.py
│   └── tool_plugin.py             # Markdown plugin framework
└── tools/
    ├── TEMPLATE.md                # Template for new tools
    ├── hadolint.md                # Dockerfile linter
    ├── lychee.md                  # Link checker
    ├── markdownlint-cli2.md       # Markdown linter
    ├── shellcheck.md              # Shell linter
    ├── shfmt.md                   # Shell formatter
    └── taplo.md                   # TOML formatter
```

### Three-Layer Architecture

**Layer 1: Markdown (Data)**

- Tool documentation
- Installation commands
- Manual testing examples
- Single source of truth

**Layer 2: Python (Logic)**

- Parses Markdown plugins
- Executes code blocks
- Version management
- Error handling

**Layer 3: Bash (Orchestration)**

- High-level workflows
- User interface
- Integration with other tools
- Dry-run support

### Benefits

1. **Documentation = Code**: Can't drift apart
1. **Manual Testing**: Commands are visible and testable
1. **Maintainability**: One file per tool, clear structure
1. **Extensibility**: Add tools without modifying framework
1. **Safety**: Dry-run at every level

## Troubleshooting

### Tool Version Mismatch

**Problem**: Tool installed but wrong version

**Solution**:

```bash
# Reinstall specific tool
python3 scripts/setup-external-tools.py --tool yourtool

# Or reinstall all tools
python3 scripts/setup-external-tools.py
```

### Tool Not Found

**Problem**: Command not found after installation

**Cause**: Tool installed to location not in PATH

**Solutions**:

1. Check where tool was installed: `which yourtool`
1. Add `/usr/local/bin` to PATH: `export PATH="/usr/local/bin:$PATH"`
1. Verify plugin installs to correct location

### Sudo Permission Issues

**Problem**: Installation fails with permission denied

**Solution**:

- Most tools install to `/usr/local/bin` (requires sudo)
- Ensure you can run `sudo` commands
- Use `--dry-run` to see what would be executed first

### npm Permission Issues

**Problem**: markdownlint-cli2 installation fails

**Causes**:

1. npm not installed
1. npm permission issues (global installs)

**Solutions**:

```bash
# Check npm is installed
npm --version

# If not installed (Ubuntu/Debian):
sudo apt-get install nodejs npm

# If permission issues, configure user directory:
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Pre-commit Hooks Not Working

**Problem**: Commits succeed without running hooks

**Cause**: Hooks not installed

**Solution**:

```bash
# Verify hooks are installed
ls -la .git/hooks/pre-commit

# Install manually if missing
uv run pre-commit install

# Test hooks
uv run pre-commit run --all-files
```

## Design Documentation

For detailed design decisions and implementation details, see:

- [docs/design/tools-plugin-architecture/](../docs/design/tools-plugin-architecture/)
  - [01-architecture.md](../docs/design/tools-plugin-architecture/01-architecture.md) - Plugin architecture proposal
  - [02-implementation-decision.md](../docs/design/tools-plugin-architecture/02-implementation-decision.md) - Bash vs Python analysis
  - [03-implementation-plan.md](../docs/design/tools-plugin-architecture/03-implementation-plan.md) - Implementation roadmap
  - [04-validation-results.md](../docs/design/tools-plugin-architecture/04-validation-results.md) - Proof-of-concept validation
  - [05-phase4-migration-complete.md](../docs/design/tools-plugin-architecture/05-phase4-migration-complete.md) - Migration completion
  - [06-phase5-orchestrators-complete.md](../docs/design/tools-plugin-architecture/06-phase5-orchestrators-complete.md) - Orchestrators update

## Contributing

When contributing, please:

1. **Test locally first**: Run `./scripts/setup-environment.sh`
1. **Use pre-commit hooks**: They catch issues before commit
1. **Update documentation**: Keep README and Markdown plugins in sync
1. **Test new tools**: Manual testing before adding to automation
1. **Follow the template**: Use [TEMPLATE.md](tools/TEMPLATE.md) for new tools

## FAQ

### Why Markdown for tool plugins?

**Answer**: Documentation-driven development. The commands you document are the commands automation runs. This ensures:

- Documentation stays accurate (it IS the automation)
- Manual testing validates both docs and automation
- No duplication between docs and code

### How do I update a tool version?

**Answer**:

1. Edit version in `pyproject.toml` `[tool.external-tools]`
1. Run `python3 scripts/setup-external-tools.py`
1. Verify with `./scripts/check-environment.sh`

### What if I only need one tool?

**Answer**: Use the `--tool` flag:

```bash
python3 scripts/setup-external-tools.py --tool hadolint
python3 scripts/check-tools.py --tool hadolint
```

### Can I add a tool that doesn't use binary downloads?

**Answer**: Yes! See [markdownlint-cli2.md](tools/markdownlint-cli2.md) for an npm-based example. The install block can contain any bash commands.

### What about macOS or Windows?

**Answer**: Currently Linux-only (x86_64). The plugin system supports multiple platforms (add `install-macos` blocks), but current plugins only have Linux commands. Contributions welcome!
