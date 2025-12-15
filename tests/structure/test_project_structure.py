"""
Project Structure Tests for Story 1-1: Terminal Installation and Basic Execution

These tests verify the acceptance criteria for project structure:
- AC3: Project structure aligns with Architecture boundaries
- AC4: Dependency management (pyproject.toml configuration)

Tests follow ATDD red-green-refactor cycle - written BEFORE implementation.
"""

from pathlib import Path

import pytest


# =============================================================================
# Constants
# =============================================================================

# Project root calculated relative to test file location
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Required directories per architecture (using eleven_video/ as module root)
REQUIRED_DIRECTORIES = [
    "eleven_video",
    "eleven_video/config",
    "eleven_video/api",
    "eleven_video/orchestrator",
    "eleven_video/processing",
    "eleven_video/ui",
    "eleven_video/models",
    "eleven_video/exceptions",
    "eleven_video/utils",
    "eleven_video/constants",
]

# Required files for basic project structure
REQUIRED_FILES = [
    "pyproject.toml",
    "README.md",
    ".env.example",
    ".gitignore",
    "eleven_video/__init__.py",
    "eleven_video/main.py",
]


# =============================================================================
# AC3: Directory Structure Tests
# =============================================================================

class TestDirectoryStructure:
    """Tests for project directory structure (AC3)."""

    def test_required_directories_exist(self):
        """
        GIVEN the project structure requirements from architecture
        WHEN checking the file system
        THEN all required directories exist
        """
        missing_dirs = []

        for dir_path in REQUIRED_DIRECTORIES:
            full_path = PROJECT_ROOT / dir_path
            if not full_path.is_dir():
                missing_dirs.append(dir_path)

        assert not missing_dirs, \
            f"Missing required directories: {missing_dirs}"

    def test_directories_have_init_files(self):
        """
        GIVEN the required Python package directories
        WHEN checking each directory
        THEN each has an __init__.py file
        """
        # Only check directories that should be Python packages
        package_dirs = [d for d in REQUIRED_DIRECTORIES if d.startswith("eleven_video")]
        missing_init = []

        for dir_path in package_dirs:
            init_path = PROJECT_ROOT / dir_path / "__init__.py"
            if not init_path.is_file():
                missing_init.append(dir_path)

        assert not missing_init, \
            f"Missing __init__.py in directories: {missing_init}"

    def test_tests_directory_exists(self):
        """
        GIVEN the project structure
        WHEN checking for test directory
        THEN tests/ directory exists with proper structure
        """
        tests_dir = PROJECT_ROOT / "tests"
        assert tests_dir.is_dir(), "tests/ directory should exist"

        # Check for test subdirectories
        expected_test_dirs = ["tests/cli", "tests/structure"]
        for test_dir in expected_test_dirs:
            dir_path = PROJECT_ROOT / test_dir
            assert dir_path.is_dir(), f"Test directory {test_dir} should exist"


# =============================================================================
# AC4: Dependency Management Tests
# =============================================================================

class TestDependencyManagement:
    """Tests for dependency management configuration (AC4)."""

    def test_pyproject_toml_exists(self):
        """
        GIVEN the project root
        WHEN checking for pyproject.toml
        THEN the file exists
        """
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.is_file(), "pyproject.toml should exist in project root"

    def test_pyproject_has_project_metadata(self):
        """
        GIVEN pyproject.toml exists
        WHEN reading its content
        THEN required metadata sections are present
        """
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_path.read_text()

        required_sections = [
            "[project]",
            "name =",
            "version =",
            "dependencies",
        ]

        for section in required_sections:
            assert section in content, \
                f"pyproject.toml should contain '{section}'"

    def test_pyproject_defines_dependencies(self):
        """
        GIVEN pyproject.toml exists
        WHEN reading dependencies
        THEN required runtime dependencies are listed
        """
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_path.read_text()

        required_deps = ["typer", "rich"]

        for dep in required_deps:
            assert dep in content, \
                f"Required dependency '{dep}' should be in pyproject.toml"

    def test_pyproject_defines_dev_dependencies(self):
        """
        GIVEN pyproject.toml exists
        WHEN reading dev dependencies
        THEN testing and quality tools are listed
        """
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_path.read_text()

        required_dev_deps = ["pytest", "ruff", "black"]

        for dep in required_dev_deps:
            assert dep in content, \
                f"Required dev dependency '{dep}' should be in pyproject.toml"

    def test_pyproject_defines_script_entry(self):
        """
        GIVEN pyproject.toml exists
        WHEN reading script definitions
        THEN eleven-video CLI entry point is defined
        """
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        content = pyproject_path.read_text()

        assert "[project.scripts]" in content, \
            "pyproject.toml should define project scripts"
        assert "eleven-video" in content, \
            "Entry point 'eleven-video' should be defined"


# =============================================================================
# Required Files Tests
# =============================================================================

class TestRequiredFiles:
    """Tests for required project files."""

    def test_required_files_exist(self):
        """
        GIVEN the project requirements
        WHEN checking for required files
        THEN all required files exist
        """
        missing_files = []

        for file_path in REQUIRED_FILES:
            full_path = PROJECT_ROOT / file_path
            if not full_path.is_file():
                missing_files.append(file_path)

        assert not missing_files, \
            f"Missing required files: {missing_files}"

    def test_readme_has_content(self):
        """
        GIVEN README.md exists
        WHEN reading its content
        THEN it has meaningful content (not empty)
        """
        readme_path = PROJECT_ROOT / "README.md"
        if readme_path.is_file():
            content = readme_path.read_text()
            assert len(content) > 100, \
                "README.md should have meaningful content (>100 chars)"
            assert "eleven" in content.lower() or "video" in content.lower(), \
                "README.md should mention the project"

    def test_env_example_has_required_keys(self):
        """
        GIVEN .env.example exists
        WHEN reading its content
        THEN required API key placeholders are present
        """
        env_example_path = PROJECT_ROOT / ".env.example"
        if env_example_path.is_file():
            content = env_example_path.read_text()

            required_keys = ["ELEVENLABS_API_KEY", "GEMINI_API_KEY"]
            for key in required_keys:
                assert key in content, \
                    f".env.example should contain placeholder for {key}"

    def test_gitignore_excludes_sensitive_files(self):
        """
        GIVEN .gitignore exists
        WHEN reading its content
        THEN sensitive files are excluded
        """
        gitignore_path = PROJECT_ROOT / ".gitignore"
        if gitignore_path.is_file():
            content = gitignore_path.read_text()

            # Should exclude sensitive and generated files
            should_exclude = [".env", "__pycache__", "*.pyc"]
            for pattern in should_exclude:
                assert pattern in content, \
                    f".gitignore should exclude '{pattern}'"
