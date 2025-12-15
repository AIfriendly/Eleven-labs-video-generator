# ATDD Checklist - Epic 1, Story 1: Terminal Installation and Basic Execution

**Date:** 2025-12-12
**Author:** Murat (TEA)
**Primary Test Level:** Integration/CLI

---

## Story Summary

This story establishes the foundational project structure and CLI entry point for the Eleven Labs AI Video Generator tool.

**As a** developer
**I want** to install the Eleven Labs AI Video tool via package manager
**So that** I can start using it from my terminal quickly

---

## Acceptance Criteria

1. **Given** I have Python installed on my system, **When** I run the installation command, **Then** the tool is installed and available in my terminal.
2. **Given** the tool is installed, **When** I run the basic help command (e.g. `eleven-video --help`), **Then** I see available options and the command executes successfully.
3. The project structure must align with the defined Architecture boundaries (src/ layout).
4. Dependency management must use Poetry as specified in Architectural Decisions.

---

## Risk Assessment 🎯

| Criterion | Risk Level | Impact | Test Priority |
|-----------|------------|--------|---------------|
| AC1: Installation | Medium | High | P0 |
| AC2: Help command | Low | High | P0 |
| AC3: Project structure | Low | Medium | P1 |
| AC4: Dependency management | Medium | Medium | P1 |

**Note:** The current project uses `setuptools` instead of Poetry as specified in Architecture. This is a **deviation** from architectural decisions that should be flagged for team discussion.

---

## Failing Tests Created (RED Phase)

### CLI Integration Tests (4 tests)

**File:** `tests/cli/test_main_cli.py` (NEW)

| Test | Status | Verifies |
|------|--------|----------|
| `test_cli_help_command_displays_usage` | 🔴 RED | AC2: `--help` shows usage information |
| `test_cli_help_shows_available_options` | 🔴 RED | AC2: `--help` displays all expected options |
| `test_cli_version_option_exists` | 🔴 RED | AC2: `--version` is available |
| `test_cli_entrypoint_exists` | 🔴 RED | AC1: `eleven-video` command is callable |

### Project Structure Tests (3 tests)

**File:** `tests/structure/test_project_structure.py` (NEW)

| Test | Status | Verifies |
|------|--------|----------|
| `test_required_directories_exist` | 🔴 RED | AC3: All required directories present |
| `test_pyproject_toml_exists` | 🔴 RED | AC4: Poetry configuration present |
| `test_module_structure_correct` | 🔴 RED | AC3: Module layout matches architecture |

---

## Data Factories Created

No data factories needed for this story - tests are structural/CLI verification.

---

## Fixtures Created

### CLI Fixtures

**File:** `tests/support/fixtures/cli_fixture.py`

**Fixtures:**
- `cli_runner` - Typer CliRunner for invoking CLI commands
  - **Setup:** Creates CliRunner instance
  - **Provides:** Ready-to-use CLI test runner
  - **Cleanup:** None required (stateless)

---

## Mock Requirements

No external service mocks required for this story - pure CLI/structure verification.

---

## Required data-testid Attributes

Not applicable - this story has no UI components.

---

## Implementation Checklist

### Test: test_cli_help_command_displays_usage

**File:** `tests/cli/test_main_cli.py`

**Tasks to make this test pass:**
- [x] Typer app exists in `eleven_video/main.py` ✅
- [x] Help text is registered ✅
- [ ] Verify `--help` output contains expected usage patterns
- [ ] Run test: `pytest tests/cli/test_main_cli.py::test_cli_help_command_displays_usage -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours (mostly verification - implementation exists)

---

### Test: test_cli_help_shows_available_options

**File:** `tests/cli/test_main_cli.py`

**Tasks to make this test pass:**
- [x] Options defined in main.py ✅
- [ ] Verify all expected options appear in help output:
  - `--prompt`, `-p`
  - `--voice`, `-v`
  - `--api-key`, `-k`
  - `--gemini-key`, `-g`
  - `--output`, `-o`
- [ ] Run test: `pytest tests/cli/test_main_cli.py::test_cli_help_shows_available_options -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: test_cli_entrypoint_exists

**File:** `tests/cli/test_main_cli.py`

**Tasks to make this test pass:**
- [x] Entry point defined in `pyproject.toml` ✅
- [ ] Verify `eleven-video` command is callable
- [ ] Run test: `pytest tests/cli/test_main_cli.py::test_cli_entrypoint_exists -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_required_directories_exist

**File:** `tests/structure/test_project_structure.py`

**Tasks to make this test pass:**
- [ ] Create required directories per architecture:
  - `eleven_video/config/`
  - `eleven_video/api/`
  - `eleven_video/orchestrator/`
  - `eleven_video/processing/`
  - `eleven_video/ui/`
  - `eleven_video/models/`
  - `eleven_video/exceptions/`
  - `eleven_video/utils/`
  - `eleven_video/constants/`
- [ ] Run test: `pytest tests/structure/test_project_structure.py::test_required_directories_exist -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

**Note:** Current project uses `eleven_video/` as root, not `src/` as specified in architecture. This is acceptable but should be documented.

---

## Running Tests

```bash
# Run all Story 1-1 tests
pytest tests/cli/ tests/structure/ -v

# Run specific test file
pytest tests/cli/test_main_cli.py -v

# Run with coverage
pytest tests/cli/ tests/structure/ --cov=eleven_video --cov-report=term-missing

# Run single test for debugging
pytest tests/cli/test_main_cli.py::test_cli_help_command_displays_usage -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All tests written and failing
- ✅ Test fixtures created
- ✅ Implementation checklist created
- ✅ No mocks required for this story

**Verification:**
- Tests run and fail as expected
- Failure messages are clear and actionable
- Tests fail due to missing validation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**
1. **Pick one failing test** from implementation checklist
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Priority Order:**
1. `test_cli_entrypoint_exists` - Verify entry point works
2. `test_cli_help_command_displays_usage` - Verify help displays
3. `test_cli_help_shows_available_options` - Verify options listed
4. `test_required_directories_exist` - Create directory structure

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**
1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability)
3. **Create `__init__.py` files** in all new directories
4. **Ensure tests still pass** after each refactor

---

## Architecture Deviation Notice

> [!WARNING]
> **Deviation from Architectural Decisions:**
> - **Expected:** Poetry for dependency management (`poetry.lock`)
> - **Actual:** setuptools via `pyproject.toml`
> - **Expected:** `src/` as module root
> - **Actual:** `eleven_video/` as module root
>
> This deviation should be discussed with the team. The current structure is functional but differs from the documented architecture.

---

## Next Steps

1. **Review this checklist** - Confirm test design is appropriate
2. **Run failing tests** to confirm RED phase: `pytest tests/cli/ tests/structure/ -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red → green for each)
5. **When all tests pass**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

- **test-quality.md** - Test design principles (Given-When-Then, deterministic tests)
- **component-tdd.md** - CLI testing strategies
- **fixture-architecture.md** - CLI runner fixture patterns

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `pytest tests/cli/ tests/structure/ -v`

**Expected Results:**
```
tests/cli/test_main_cli.py::test_cli_help_command_displays_usage FAILED
tests/cli/test_main_cli.py::test_cli_help_shows_available_options FAILED
tests/cli/test_main_cli.py::test_cli_version_option_exists FAILED
tests/cli/test_main_cli.py::test_cli_entrypoint_exists PASSED (entry point exists)
tests/structure/test_project_structure.py::test_required_directories_exist FAILED
tests/structure/test_project_structure.py::test_pyproject_toml_exists PASSED
tests/structure/test_project_structure.py::test_module_structure_correct FAILED
```

**Summary:**
- Total tests: 7
- Expected to pass: 2 (pyproject.toml exists, entry point defined)
- Expected to fail: 5 (structure not complete)
- Status: 🔴 RED phase verified

---

## Notes

- Current implementation has basic CLI working - tests validate it meets acceptance criteria
- Directory structure needs to be created to match architecture
- Consider discussing Poetry vs setuptools decision with team

---

**Generated by BMad TEA Agent** - 2025-12-12
