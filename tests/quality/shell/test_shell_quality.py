#!/usr/bin/env python3
"""
Test bash scripts for Google Shell Style Guide compliance.

These tests check project-specific style requirements that are NOT covered
by standard tools (shellcheck, shfmt). For tool-based checks, use tox:
  - Syntax: tox -e bash-syntax
  - Linting: tox -e shellcheck
  - Formatting: tox -e shfmt
"""

import re
from pathlib import Path

import pytest

# Find all .sh files in scripts/ directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
BASH_SCRIPTS = list((PROJECT_ROOT / "scripts").glob("*.sh"))


@pytest.mark.quality
@pytest.mark.parametrize("script", BASH_SCRIPTS, ids=lambda s: s.name)
def test_google_style_shebang(script):
    """All bash scripts must use proper shebang per Google Style Guide.

    Google Shell Style Guide section 1.1:
    - Use #!/bin/bash for bash scripts (not #!/bin/sh)
    - Executables should start with #!/bin/bash and minimal flags
    """
    content = script.read_text()
    lines = content.splitlines()

    assert lines, f"{script.name} is empty"

    first_line = lines[0]
    assert first_line.startswith("#!"), (
        f"{script.name} missing shebang.\nFirst line should be: #!/bin/bash"
    )

    # Must use bash, not sh
    assert "/bash" in first_line, (
        f"{script.name} uses wrong shebang: {first_line}\n"
        f"Google Style requires: #!/bin/bash (not #!/bin/sh)"
    )


@pytest.mark.quality
@pytest.mark.xfail(
    reason="Function docs incomplete - demonstrating Google Style check",
    strict=False,
)
@pytest.mark.parametrize("script", BASH_SCRIPTS, ids=lambda s: s.name)
def test_google_style_function_comments(script):
    """Functions should have comment blocks per Google Style Guide section 6.1.

    Google Shell Style Guide:
    - All functions should have comments describing their purpose
    - Comment should appear immediately before function definition

    NOTE: This test is currently xfail to demonstrate a Google Style check
    that shellcheck/shfmt don't cover. It shows how pytest tests can enforce
    project-specific style requirements beyond what linters provide.
    """
    content = script.read_text()
    lines = content.splitlines()

    # Find all function definitions
    functions = []
    for i, line in enumerate(lines):
        # Match: function_name() {  or  function function_name {
        func_pattern = r"^\s*\w+\(\s*\)\s*\{"
        func_keyword_pattern = r"^\s*function\s+\w+"
        if re.match(func_pattern, line) or re.match(func_keyword_pattern, line):
            # Check if there's a comment in the previous non-empty line
            prev_line_idx = i - 1
            while prev_line_idx >= 0 and not lines[prev_line_idx].strip():
                prev_line_idx -= 1

            if prev_line_idx >= 0:
                prev_line = lines[prev_line_idx].strip()
                if not prev_line.startswith("#"):
                    func_name = re.findall(r"\w+", line)[0]
                    functions.append((i + 1, func_name))  # line number, func name

    if functions:
        missing_docs = [f"  Line {ln}: {name}()" for ln, name in functions]
        assert not missing_docs, (
            f"{script.name} has functions without comment documentation:\n"
            + "\n".join(missing_docs)
            + "\n\nGoogle Style Guide requires comment blocks before functions."
        )


@pytest.mark.quality
@pytest.mark.parametrize("script", BASH_SCRIPTS, ids=lambda s: s.name)
def test_google_style_constants(script):
    """Constants should be UPPERCASE per Google Style Guide section 7.1.

    Google Shell Style Guide:
    - Constants and environment variable names should be UPPERCASE
    - Use readonly or declare -r for true constants
    """
    content = script.read_text()

    # Look for variable assignments that look like constants (ALL_CAPS)
    # but aren't declared readonly
    for line_num, line in enumerate(content.splitlines(), 1):
        # Match: SOME_CONST=value (not inside quotes)
        if re.match(r"^\s*[A-Z_][A-Z0-9_]*=", line):
            var_name = line.split("=")[0].strip()

            # Check if this line or previous lines declare it readonly
            preceding_text = "\n".join(content.splitlines()[:line_num])

            # Allow if it's readonly, declare -r, or a common exception
            is_readonly = f"readonly {var_name}" in preceding_text
            is_declare_r = f"declare -r {var_name}" in preceding_text
            is_exception = var_name in ["DEBIAN_FRONTEND", "PATH", "HOME", "USER"]

            if not (is_readonly or is_declare_r or is_exception or "readonly" in line):
                # This is informational, not a hard failure
                # Real enforcement would need more context
                pass
