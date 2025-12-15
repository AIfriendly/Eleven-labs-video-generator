# ATDD Checklist - Story 1-4: Terminal Help System

**Date:** 2025-12-13  
**Author:** Murat (TEA Agent)  
**Primary Test Level:** Unit / CLI Integration

---

## Story Summary

**As a** user  
**I want** to access comprehensive help documentation within the terminal  
**So that** I can understand how to use the tool without leaving my workflow

---

## Acceptance Criteria

1. `--help` shows clear documentation including a list of available commands, arguments, and options
2. Subcommand-specific help (e.g., `setup --help`) shows context-aware documentation
3. Help output uses Rich formatting (colors, ANSI codes) per Architecture decision
4. `rich-click` package is NOT installed (Typer's native Rich mode is sufficient)

---

## Failing Tests Created (RED Phase)

### Unit/CLI Tests (15 tests total)

**File:** `tests/cli/test_help_system.py` (~250 lines)

#### AC1: Help Documentation (4 tests) - ✅ ALL PASSING
- ✅ `test_help_returns_exit_code_zero` - PASSED
- ✅ `test_help_shows_available_commands_list` - PASSED
- ✅ `test_help_shows_command_descriptions` - PASSED
- ✅ `test_help_shows_options_section` - PASSED

#### AC2: Subcommand Help (3 tests) - ✅ ALL PASSING
- ✅ `test_setup_help_returns_exit_code_zero` - PASSED
- ✅ `test_setup_help_shows_specific_description` - PASSED
- ✅ `test_setup_help_differs_from_main_help` - PASSED

#### AC3: Rich Formatting (3 tests) - 🔴 3 FAILING
- 🔴 `test_typer_app_has_rich_markup_mode`
  - **Status:** RED - `rich_markup_mode="rich"` not found in main.py
  - **Verifies:** Typer app configured for Rich markup
- 🔴 `test_help_output_contains_ansi_codes`
  - **Status:** RED - No ANSI escape codes in help output
  - **Verifies:** Rich formatting produces colored output
- 🔴 `test_console_singleton_exists`
  - **Status:** RED - `eleven_video.ui.console` module doesn't exist
  - **Verifies:** Console singleton pattern per Architecture

#### AC4: No rich-click (2 tests) - ✅ ALL PASSING
- ✅ `test_rich_click_not_in_dependencies` - PASSED
- ✅ `test_rich_click_not_in_pyproject` - PASSED

#### Console Singleton (3 tests) - 🔴 3 FAILING
- 🔴 `test_console_module_exports_console`
  - **Status:** RED - Module doesn't exist
  - **Verifies:** `console` exported from module
- 🔴 `test_console_is_rich_console_instance`
  - **Status:** RED - Module doesn't exist
  - **Verifies:** Console is `rich.console.Console` type
- 🔴 `test_get_console_function_returns_same_instance`
  - **Status:** RED - `get_console` function doesn't exist
  - **Verifies:** Singleton pattern returns same instance

---

## Implementation Checklist

### Test: test_console_singleton_exists (+ related Console tests)

**File:** `tests/cli/test_help_system.py`

**Tasks to make these tests pass:**

- [ ] Create `eleven_video/ui/__init__.py`
- [ ] Create `eleven_video/ui/console.py` with:
  - [ ] Module-level `console = Console()` singleton
  - [ ] `get_console()` function that returns the singleton
- [ ] Verify tests pass: `uv run pytest tests/cli/test_help_system.py::TestConsoleSingleton -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_typer_app_has_rich_markup_mode

**File:** `tests/cli/test_help_system.py`

**Tasks to make this test pass:**

- [ ] Modify `eleven_video/main.py`:
  - [ ] Change `app = typer.Typer(help=...)` to include `rich_markup_mode="rich"`
- [ ] Update docstrings to use Rich markup (optional enhancement)
- [ ] Verify test passes: `uv run pytest tests/cli/test_help_system.py::TestRichFormatting::test_typer_app_has_rich_markup_mode -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: test_help_output_contains_ansi_codes

**File:** `tests/cli/test_help_system.py`

**Tasks to make this test pass:**

- [ ] After enabling `rich_markup_mode="rich"`, verify Rich produces ANSI output
- [ ] Test may auto-pass once `rich_markup_mode` is set
- [ ] Verify test passes: `uv run pytest tests/cli/test_help_system.py::TestRichFormatting::test_help_output_contains_ansi_codes -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.1 hours (likely auto-pass after Task 1)

---

## Running Tests

```bash
# Run all Story 1-4 tests (verify RED phase)
uv run pytest tests/cli/test_help_system.py -v

# Run specific test class
uv run pytest tests/cli/test_help_system.py::TestRichFormatting -v

# Run specific test
uv run pytest tests/cli/test_help_system.py::TestConsoleSingleton::test_console_singleton_exists -v

# Run with coverage
uv run pytest tests/cli/test_help_system.py --cov=eleven_video -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ 15 tests written (5 failing, 10 passing)
- ✅ Test file created: `tests/cli/test_help_system.py`
- ✅ All ACs covered with specific tests

**Verification:**

```
======================= 5 failed, 10 passed in 3.01s =======================
```

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Create Console singleton** (`eleven_video/ui/console.py`)
2. **Add `rich_markup_mode="rich"`** to Typer app in `main.py`
3. **Run tests** after each change to verify green

**Key Files to Create/Modify:**

| File | Action |
|------|--------|
| `eleven_video/ui/__init__.py` | CREATE (empty or minimal) |
| `eleven_video/ui/console.py` | CREATE (Console singleton) |
| `eleven_video/main.py` | MODIFY (add `rich_markup_mode`) |

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. Consider migrating existing `console = Console()` in `main.py` to use singleton
2. Ensure consistent Console usage across all modules
3. Add Rich markup to docstrings for enhanced help display

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/cli/test_help_system.py -v --tb=short`

**Summary:**

- Total tests: 15
- Passing: 10 (expected)
- Failing: 5 (expected)
- Status: ✅ RED phase verified

**Expected Failure Messages:**

1. `No module named 'eleven_video.ui'`
2. `rich_markup_mode="rich"` not found in main.py
3. `get_console function should exist`

---

## Notes

- AC1 and AC2 already pass with current implementation
- AC4 passes (no rich-click installed)
- Only AC3 requires implementation work
- Console singleton is an Architecture requirement, not just story AC

---

**Generated by BMad TEA Agent** - 2025-12-13
