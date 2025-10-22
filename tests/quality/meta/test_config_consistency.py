"""Test project-wide configuration consistency.

Validates that versions and settings are consistent across different config files,
using pyproject.toml as the single source of truth where applicable.
"""

import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml
from packaging.version import Version
from packaging.version import parse as parse_version

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


def get_build_tool_versions():
    """Load build tool versions from pyproject.toml."""
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    return config.get("tool", {}).get("external-tools", {})


class TestConfigConsistency:
    """Ensure configuration is consistent across different files."""

    @pytest.mark.quality
    def test_ruff_version_matches_precommit(self):
        """Ruff version in pyproject.toml should match pre-commit config."""
        # Read pyproject.toml for ruff version
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)

        # Ruff version is in dev dependency group (PEP 735)
        ruff_version = None
        for dep in pyproject["dependency-groups"]["dev"]:
            if dep.startswith("ruff>="):
                ruff_version = dep.split(">=")[1].split(",")[0]
                break

        assert ruff_version, (
            "Could not find ruff version in pyproject.toml [dependency-groups] dev"
        )

        # Read pre-commit config for ruff version
        with open(PROJECT_ROOT / ".pre-commit-config.yaml") as f:
            precommit = yaml.safe_load(f)

        precommit_ruff_version = None
        for repo in precommit["repos"]:
            if "ruff-pre-commit" in repo["repo"]:
                # Version is like "v0.13.2"
                version = repo["rev"]
                # Remove 'v' prefix if present
                precommit_ruff_version = version.lstrip("v")
                break

        assert precommit_ruff_version, (
            "Could not find ruff version in .pre-commit-config.yaml"
        )

        # Compare versions (allow pre-commit to be >= project min version)
        assert parse_version(precommit_ruff_version) >= parse_version(ruff_version), (
            f"Pre-commit ruff version ({precommit_ruff_version}) "
            f"should be >= project ruff version ({ruff_version}). "
            "Update .pre-commit-config.yaml to match pyproject.toml"
        )

    @pytest.mark.quality
    def test_python_version_consistency(self):
        """Python version should be consistent across all config files.

        This test ensures Python version references are controlled by pyproject.toml.
        It extracts the minimum required Python version from pyproject.toml and
        validates that all other configuration files use compatible versions.

        The test understands semantic versioning:
        - If pyproject.toml says ">=3.12", config files should use exactly "3.12"
        - They should not use older versions (3.11) or different versions (3.13)
        """
        import subprocess

        # Read pyproject.toml for Python version (source of truth)
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)

        requires_python = pyproject["project"]["requires-python"]

        # Extract the minimum version from the specifier
        # For ">=3.12", "~=3.12.0", etc., extract the base version
        version_match = re.search(r"(\d+)\.(\d+)", requires_python)
        if not version_match:
            raise ValueError(f"Cannot parse version from: {requires_python}")

        major = int(version_match.group(1))
        minor = int(version_match.group(2))

        # This is the version that all config files should reference
        python_version = f"{major}.{minor}"
        min_version = Version(python_version)

        # Expected alternative formats for the minimum version
        py_nodot = python_version.replace(".", "")  # "312"
        py_target = f"py{py_nodot}"  # "py312"

        # Search for ALL Python version references (not just our expected version)
        # This catches if someone accidentally uses 3.11 or 3.13
        general_python_pattern = r"(python[:\-]?\d+\.\d+|py3\d+|\d+\.\d+-)"

        exclude_patterns = [
            ".venv",
            ".tox",
            ".git",
            ".pytest_cache",
            "__pycache__",
            "*.pyc",
            ".ruff_cache",
            "extracted_charts",
            ".uv-cache",
        ]

        # Build grep exclude args
        exclude_args = []
        for pattern in exclude_patterns:
            exclude_args.extend(["--exclude-dir", pattern])

        # Run grep to find all Python version references
        result = subprocess.run(
            [
                "grep",
                "-r",
                "-i",
                "-E",
                general_python_pattern,
                str(PROJECT_ROOT),
                *exclude_args,
                "--exclude=*.md",  # Exclude markdown (documentation)
                "--exclude=uv.lock",  # Exclude lock file
                "--exclude=*.json",  # Exclude test data
                "--exclude=*.csv",  # Exclude test data
            ],
            capture_output=True,
            text=True,
        )

        # Parse grep output and validate versions
        mismatches = []
        files_checked = set()

        for line in result.stdout.splitlines():
            if ":" not in line:
                continue

            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            file_path, content = parts
            file_path = Path(file_path).relative_to(PROJECT_ROOT)
            files_checked.add(str(file_path))

            # Skip this test file itself
            if "test_config_consistency" in str(file_path):
                continue

            # Extract Python version from content
            # Match patterns like: 3.12, python3.12, python:3.12, py312
            version_patterns = [
                r"python:(\d+)\.(\d+)",  # python:3.12
                r"python-?(\d+)\.(\d+)",  # python3.12, python-3.12
                r"py(\d)(\d+)",  # py312 -> 3.12
                r"(?<!\d)(\d+)\.(\d+)(?:-\w+)?(?!\d)",  # 3.12, 3.12-bookworm
            ]

            found_versions = set()
            for pattern in version_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    if pattern == r"py(\d)(\d+)":
                        # Handle py312 format: py312 -> 3.12
                        maj = match.group(1)
                        min_full = match.group(2)
                        version_str = f"{maj}.{min_full}"
                    else:
                        version_str = f"{match.group(1)}.{match.group(2)}"

                    # Use packaging.version.Version for proper comparison
                    try:
                        found_versions.add(Version(version_str))
                    except Exception:  # noqa: S112
                        # Skip invalid versions
                        continue

            # Validate all found versions match the minimum required version
            for found_ver in found_versions:
                if found_ver != min_version:
                    mismatches.append(
                        f"{file_path}: expected {python_version}, found {found_ver}"
                    )

        # Validate no mismatches
        assert not mismatches, (
            "Python version mismatches found:\n"
            + "\n".join(mismatches)
            + f"\n\nAll Python versions should match pyproject.toml "
            f"minimum requirement: {python_version}\n"
            f'(from requires-python = "{requires_python}")'
        )

        # Also check ruff target-version explicitly (it uses different format)
        ruff_target = (
            pyproject.get("tool", {}).get("ruff", {}).get("target-version", "")
        )
        if ruff_target:
            assert ruff_target == py_target, (
                f"Ruff target-version ({ruff_target}) should be {py_target} "
                f"to match Python minimum version {python_version}"
            )

    @pytest.mark.quality
    def test_line_length_consistency(self):
        """Line length should be consistent across configs."""
        # Read pyproject.toml for line length
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)

        line_length = pyproject["tool"]["ruff"]["line-length"]

        # Check VS Code settings (JSONC format with comments)
        vscode_settings = PROJECT_ROOT / ".vscode" / "settings.json"
        if vscode_settings.exists():
            with open(vscode_settings) as f:
                # Remove comments for JSON parsing (JSONC -> JSON)
                content = "\n".join(
                    line for line in f if not line.strip().startswith("//")
                )
                vscode = json.loads(content)

            rulers = vscode.get("editor.rulers", [])
            assert line_length in rulers, (
                f"VS Code ruler ({rulers}) should include "
                f"ruff line-length ({line_length})"
            )

        # Check devcontainer settings
        devcontainer_json = PROJECT_ROOT / ".devcontainer" / "devcontainer.json"
        if devcontainer_json.exists():
            with open(devcontainer_json) as f:
                content = f.read()

            # Look for editor.rulers in devcontainer
            ruler_match = re.search(r'"editor\.rulers":\s*\[(\d+)\]', content)
            if ruler_match:
                devcontainer_ruler = int(ruler_match.group(1))
                assert devcontainer_ruler == line_length, (
                    f"Devcontainer ruler ({devcontainer_ruler}) should match "
                    f"ruff line-length ({line_length})"
                )

    @pytest.mark.quality
    def test_formatting_tools_documented(self):
        """Formatting guidelines should document tool versions (if exists)."""
        guidelines = PROJECT_ROOT / "AGENTS.md"

        # AGENTS.md is optional - skip test if not present
        if not guidelines.exists():
            pytest.skip("AGENTS.md not found - skipping formatting check")

        content = guidelines.read_text()

        # Check that it mentions using ruff format
        assert "ruff format" in content, "AGENTS.md should document ruff format usage"

        # Check line length is mentioned
        with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        line_length = pyproject["tool"]["ruff"]["line-length"]

        # Should mention the line length (88)
        assert str(line_length) in content, (
            f"AGENTS.md should mention line length ({line_length})"
        )

    @pytest.mark.quality
    def test_build_tool_versions_in_precommit(self):
        """Pre-commit hook versions should match pyproject.toml build tools."""
        build_tools = get_build_tool_versions()

        assert build_tools, (
            "No build-tools found in pyproject.toml [tool.external-tools]"
        )

        with open(PROJECT_ROOT / ".pre-commit-config.yaml") as f:
            precommit = yaml.safe_load(f)

        # Check shellcheck version
        if "shellcheck" in build_tools:
            expected_version = build_tools["shellcheck"]
            shellcheck_repo = None
            for repo in precommit["repos"]:
                if "shellcheck-py" in repo["repo"]:
                    shellcheck_repo = repo
                    break

            assert shellcheck_repo, "shellcheck-py repo not found in pre-commit config"

            # Version format: v0.11.0.1 (adds .1 suffix to shellcheck version)
            actual_version = shellcheck_repo["rev"].lstrip("v").rsplit(".", 1)[0]
            assert actual_version == expected_version, (
                f"Pre-commit shellcheck version ({actual_version}) should match "
                f"pyproject.toml ({expected_version})"
            )

        # Check shfmt version
        if "shfmt" in build_tools:
            expected_version = build_tools["shfmt"]
            shfmt_repo = None
            for repo in precommit["repos"]:
                if "pre-commit-shfmt" in repo["repo"]:
                    shfmt_repo = repo
                    break

            assert shfmt_repo, "pre-commit-shfmt repo not found in pre-commit config"

            # Version format: v3.10.0-1 (adds -1 suffix)
            actual_version = shfmt_repo["rev"].lstrip("v").rsplit("-", 1)[0]
            assert actual_version == expected_version, (
                f"Pre-commit shfmt version ({actual_version}) should match "
                f"pyproject.toml ({expected_version})"
            )

    @pytest.mark.quality
    def test_devcontainer_uses_setup_environment_script(self):
        """Dev container setup should use scripts/setup-environment.sh."""
        setup_script = PROJECT_ROOT / ".devcontainer" / "setup.sh"
        if not setup_script.exists():
            return

        setup_content = setup_script.read_text()

        # Dev container should call the unified setup-environment.sh script
        assert "scripts/setup-environment.sh" in setup_content, (
            "Dev container setup.sh should call scripts/setup-environment.sh "
            "which handles all setup including build tools and dependencies"
        )

        # Should pass --devcontainer flag
        assert "--devcontainer" in setup_content, (
            "Dev container setup.sh should pass --devcontainer flag to "
            "scripts/setup-environment.sh"
        )

        # Should NOT have hardcoded versions or manual installations
        assert "SHELLCHECK_VERSION=" not in setup_content, (
            "Dev container setup.sh should not hardcode versions. "
            "All versions should come from pyproject.toml via setup-environment.sh"
        )
        assert "uv sync" not in setup_content, (
            "Dev container setup.sh should not directly run uv commands. "
            "These are handled by setup-environment.sh"
        )
