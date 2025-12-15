"""
CLI Integration Tests for Story 1-1: Terminal Installation and Basic Execution

These tests verify the acceptance criteria for the CLI entry point:
- AC1: Tool is installed and available in terminal
- AC2: Help command displays available options and executes successfully

Tests follow ATDD red-green-refactor cycle - written BEFORE implementation.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from eleven_video.main import app


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a CLI runner for testing Typer commands."""
    return CliRunner()


# =============================================================================
# AC2: Help Command Tests
# =============================================================================

class TestHelpCommand:
    """Tests for --help command functionality (AC2)."""

    def test_cli_help_command_displays_usage(self, cli_runner: CliRunner):
        """
        GIVEN the eleven-video CLI is invoked
        WHEN the user runs --help
        THEN usage information is displayed and exit code is 0
        """
        # WHEN: User runs help command
        result = cli_runner.invoke(app, ["--help"])

        # THEN: Help text is displayed with exit code 0
        assert result.exit_code == 0, f"Expected exit code 0, got {result.exit_code}"
        assert "Usage:" in result.output or "usage:" in result.output.lower(), \
            "Help output should contain usage information"

    def test_cli_help_shows_available_options(self, cli_runner: CliRunner):
        """
        GIVEN the eleven-video CLI is invoked
        WHEN the user runs --help
        THEN all expected options are displayed
        """
        # WHEN: User runs help command
        result = cli_runner.invoke(app, ["--help"])

        # THEN: All expected options are present
        expected_options = [
            "--prompt",
            "--voice",
            "--api-key",
            "--gemini-key",
            "--output",
        ]

        for option in expected_options:
            assert option in result.output, \
                f"Expected option '{option}' not found in help output"

    def test_cli_help_shows_short_options(self, cli_runner: CliRunner):
        """
        GIVEN the eleven-video CLI is invoked
        WHEN the user runs --help
        THEN short option aliases are displayed
        """
        # WHEN: User runs help command
        result = cli_runner.invoke(app, ["--help"])

        # THEN: Short option aliases are present
        expected_short_options = ["-p", "-v", "-k", "-g", "-o"]

        for short_opt in expected_short_options:
            assert short_opt in result.output, \
                f"Expected short option '{short_opt}' not found in help output"

    def test_cli_version_option_exists(self, cli_runner: CliRunner):
        """
        GIVEN the eleven-video CLI is invoked
        WHEN the user runs --version
        THEN version information is displayed

        Note: This test will FAIL until version option is implemented.
        """
        # WHEN: User runs version command
        result = cli_runner.invoke(app, ["--version"])

        # THEN: Version is displayed (not an error)
        # Accept either successful version display or graceful handling
        assert result.exit_code == 0, \
            f"Expected exit code 0 for --version, got {result.exit_code}"
        assert "0.1.0" in result.output or "version" in result.output.lower(), \
            "Version information should be displayed"


# =============================================================================
# AC1: Entry Point Tests
# =============================================================================

class TestEntryPoint:
    """Tests for CLI entry point installation (AC1)."""

    def test_cli_entrypoint_callable(self, cli_runner: CliRunner):
        """
        GIVEN the package is installed
        WHEN the CLI app is invoked
        THEN it executes without import errors
        """
        # WHEN: CLI app is invoked with help (safe command)
        result = cli_runner.invoke(app, ["--help"])

        # THEN: No import or execution errors
        assert result.exit_code == 0, \
            f"CLI should execute cleanly, but got exit code {result.exit_code}"
        assert result.exception is None, \
            f"CLI raised unexpected exception: {result.exception}"

    def test_pyproject_defines_script_entry(self):
        """
        GIVEN the pyproject.toml exists
        WHEN we check script definitions
        THEN eleven-video entry point is defined
        """
        # GIVEN: pyproject.toml path
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"

        # WHEN: We read the file
        content = pyproject_path.read_text()

        # THEN: Entry point is defined
        assert "eleven-video" in content, \
            "Entry point 'eleven-video' should be defined in pyproject.toml"
        assert "eleven_video.main:app" in content, \
            "Entry point should reference eleven_video.main:app"


# =============================================================================
# Subcommand Tests
# =============================================================================

class TestSubcommands:
    """Tests for CLI subcommands."""

    def test_setup_subcommand_exists(self, cli_runner: CliRunner):
        """
        GIVEN the eleven-video CLI is invoked
        WHEN checking available commands
        THEN setup subcommand is available
        """
        # WHEN: User runs help command
        result = cli_runner.invoke(app, ["--help"])

        # THEN: setup command is listed
        assert "setup" in result.output.lower(), \
            "Setup subcommand should be available in CLI"

    def test_setup_help_displays(self, cli_runner: CliRunner):
        """
        GIVEN the setup subcommand exists
        WHEN the user runs setup --help
        THEN help for setup is displayed
        """
        # WHEN: User runs setup help
        result = cli_runner.invoke(app, ["setup", "--help"])

        # THEN: Help is displayed
        assert result.exit_code == 0, \
            f"Setup --help should succeed, got exit code {result.exit_code}"
        assert "setup" in result.output.lower() or "api" in result.output.lower(), \
            "Setup help should describe the command"
