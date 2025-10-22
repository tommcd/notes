"""Test documentation for project-specific quality standards.

These tests check aspects that aren't covered by standard tools:
- markdownlint-cli2: Lints markdown style (code blocks, headings, etc.)
- mdformat: Formats markdown syntax
- lychee: Checks all links (internal files + external URLs)

This test file only includes checks that are NOT covered by the above tools:
- README completeness (project-specific required sections)
- File references are links (enables refactoring safety + lychee validation)
"""

import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent


def get_markdown_files():
    """Get all markdown files, respecting .gitignore.

    Uses git ls-files to automatically exclude files in .gitignore
    (.venv/, .tox/, test data, etc.) without hardcoded exclude lists.

    This makes the test generic and reusable across projects - each
    project controls exclusions via their own .gitignore.
    """
    try:
        result = subprocess.run(
            ["git", "ls-files", "*.md", "**/*.md"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return [PROJECT_ROOT / f for f in files]
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback if not in git repo or git not available
        # (shouldn't happen in normal CI/development, but safer)
        return list(PROJECT_ROOT.rglob("*.md"))


def get_important_files():
    """Get list of important files that should be linked in docs.

    Checks for custom configuration file (.doc-quality-files.txt) first,
    otherwise uses sensible defaults.

    Custom config format (.doc-quality-files.txt):
        One filename per line, lines starting with # are comments.
        Example:
            # Project config files
            pyproject.toml
            tox.ini
            Dockerfile

    This allows projects to customize which files are important without
    modifying test code.

    Returns:
        list[str]: Filenames to check for links in documentation
    """
    config_file = PROJECT_ROOT / ".doc-quality-files.txt"

    # Default list - common important files for Python projects
    defaults = [
        "pyproject.toml",
        "tox.ini",
        "pytest.ini",
        "Dockerfile",
        ".dockerignore",
        ".gitignore",
        ".lychee.toml",
        ".markdownlint.yaml",
        "setup-environment.sh",
        "setup-external-tools.py",
        "check-environment.sh",
        "clean-environment.sh",
    ]

    if config_file.exists():
        # Read custom list from config file
        lines = config_file.read_text().splitlines()
        custom_files = [
            line.strip()
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        ]
        return custom_files if custom_files else defaults

    return defaults


@pytest.mark.docs
def test_readme_has_required_sections():
    """README.md should contain required sections for project documentation.

    Required sections:
    - Features (what the tool does)
    - Installation (how to install)
    - Usage (how to use)
    - Development (how to contribute)

    This ensures the README provides complete project documentation.

    NOTE: This is project-specific logic that linters can't enforce.
    """
    readme = PROJECT_ROOT / "README.md"
    assert readme.exists(), "README.md not found"

    content = readme.read_text()

    required_sections = {
        "Features": r"##\s+Features",
        "Installation": r"##\s+Installation",
        "Usage": r"##\s+Usage",
        "Development": r"##\s+Development",
    }

    missing_sections = []
    for section_name, pattern in required_sections.items():
        if not re.search(pattern, content, re.IGNORECASE):
            missing_sections.append(section_name)

    assert not missing_sections, (
        f"README.md missing required sections: {', '.join(missing_sections)}\n"
        f"Add these sections to provide complete project documentation."
    )


@pytest.mark.docs
@pytest.mark.xfail(
    reason="File link enforcement not yet complete - demonstrating refactoring safety",
    strict=False,
)
def test_important_files_are_linked_in_docs():
    """Important project files mentioned in docs should be links.

    Phase 1: Focuses on key config files that are commonly referenced.

    WHY THIS MATTERS:
    1. Refactoring safety: When files are renamed, lychee catches broken links
    2. Documentation accuracy: Forces docs to stay in sync with code structure
    3. Clickable navigation: Links work in GitHub, IDEs, and rendered docs
    4. Automated validation: lychee checks link validity automatically

    EXAMPLE:
    - Bad:  "See pyproject.toml for configuration"
    - Good: "See [pyproject.toml](pyproject.toml) for configuration"

    If files are renamed, the link breaks and lychee fails, alerting you
    to update documentation.

    See doc/design/DOCUMENTATION_QUALITY.md for Phase 2 improvements.

    To customize the list of important files for your project, create
    .doc-quality-files.txt in the project root. See get_important_files()
    docstring for format details.
    """
    # Get important files (from config file or defaults)
    important_files = get_important_files()

    md_files = get_markdown_files()
    violations = []

    for md_file in md_files:
        content = md_file.read_text()

        # Remove code blocks (don't check inside ``` ```)
        # This handles both single-line and multi-line code blocks
        content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        # Remove inline code (don't check inside ` `)
        content_no_inline = re.sub(r"`[^`]+`", "", content_no_code)

        for filename in important_files:
            # Check if file is mentioned but NOT as a link
            # Pattern: filename NOT preceded by ]( which would make it a link
            # e.g., [text](filename) is OK, but just "filename" is not
            pattern = rf"(?<!\]\(){re.escape(filename)}"

            if re.search(pattern, content_no_inline):
                violations.append(
                    f"{md_file.relative_to(PROJECT_ROOT)}: "
                    f"'{filename}' mentioned but not linked"
                )

    if violations:
        msg = (
            "Important files should be markdown links when mentioned:\n"
            + "\n".join(violations[:20])
            + "\n\nThis enables:\n"
            "- Refactoring safety (lychee catches broken links on rename)\n"
            "- Clickable navigation in GitHub/IDEs\n"
            "- Automatic link validation\n\n"
            "Example: [pyproject.toml](pyproject.toml) not just 'pyproject.toml'"
        )
        pytest.fail(msg)
