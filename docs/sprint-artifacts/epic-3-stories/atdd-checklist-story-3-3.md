# ATDD Checklist - Epic 3, Story 3.3: Interactive Voice Selection Prompts

**Date:** 2025-12-19
**Author:** Revenant
**Primary Test Level:** Component (Unit tests for VoiceSelector UI)

---

## Story Summary

Implement interactive voice selection UI that displays available voice options and allows users to select a voice by number during video generation.

**As a** user
**I want** to select from available voice options through interactive prompts
**So that** I can easily choose the voice I want without remembering specific model names

---

## Acceptance Criteria

1. Display a numbered list of available voice options when prompted to select a voice
2. When selecting a voice by number, the selection is used for TTS generation
3. If voice listing API fails, show helpful error and fall back to default voice with warning
4. Show option to use the default voice (e.g., "[0] Use default voice (Adam Stone)")
5. Skip the interactive voice prompt when `--voice` flag is provided via CLI

---

## Failing Tests Created (RED Phase)

### Unit Tests (14 tests)

**File:** `tests/ui/test_voice_selector.py` (280 lines)

| Test ID | Test Name | Status | Failure Reason | Verifies |
|---------|-----------|--------|----------------|----------|
| 3.3-UNIT-001 | `test_voice_selector_can_be_imported` | RED | ModuleNotFoundError | VoiceSelector class exists |
| 3.3-UNIT-002 | `test_voice_selector_displays_numbered_list` | RED | ModuleNotFoundError | AC #1 - Numbered list display |
| 3.3-UNIT-003 | `test_voice_selector_shows_default_option_first` | RED | ModuleNotFoundError | AC #4 - Default voice option |
| 3.3-UNIT-004 | `test_select_voice_returns_voice_id_for_valid_number` | RED | ModuleNotFoundError | AC #2 - Valid selection |
| 3.3-UNIT-005 | `test_select_voice_returns_none_for_zero` | RED | ModuleNotFoundError | AC #4 - Default selection |
| 3.3-UNIT-006 | `test_select_voice_handles_invalid_number` | RED | ModuleNotFoundError | Error handling |
| 3.3-UNIT-007 | `test_select_voice_handles_non_numeric_input` | RED | ModuleNotFoundError | Error handling |
| 3.3-UNIT-008 | `test_select_voice_interactive_fetches_voices` | RED | ModuleNotFoundError | list_voices() integration |
| 3.3-UNIT-009 | `test_select_voice_interactive_returns_selected_voice_id` | RED | ModuleNotFoundError | Full flow |
| 3.3-UNIT-010 | `test_select_voice_handles_api_failure` | RED | ModuleNotFoundError | AC #3 - API error handling |
| 3.3-UNIT-011 | `test_select_voice_handles_empty_voice_list` | RED | ModuleNotFoundError | Empty list handling |
| 3.3-UNIT-012 | `test_select_voice_skips_prompt_in_non_tty` | RED | ModuleNotFoundError | R-004 - Non-TTY fallback |
| 3.3-UNIT-013 | `test_select_voice_prints_message_in_non_tty` | RED | ModuleNotFoundError | R-004 - Non-TTY message |
| 3.3-UNIT-014 | `test_generate_skips_voice_prompt_when_voice_provided` | GREEN | Passes already | AC #5 - CLI flag skip |

---

## Data Factories Created

### VoiceInfo Factory

**File:** `tests/ui/test_voice_selector.py` (inline)

**Exports:**
- `create_voice_info(voice_id, name, category, preview_url)` - Create VoiceInfo with optional overrides
- `create_mock_voice_list(count)` - Create list of mock VoiceInfo objects

**Example Usage:**
```python
voice = create_voice_info(voice_id="specific-id", name="Rachel")
voices = create_mock_voice_list(5)  # Generate 5 test voices
```

---

## Fixtures Created

No new fixtures required. Tests use inline mocks with `unittest.mock`.

**Existing fixtures referenced:**
- `tests/fixtures/api_fixtures.py` - Contains `ELEVENLABS_VOICES_RESPONSE` for voice data

---

## Mock Requirements

### VoiceSelector Mocks

**Mock: `eleven_video.ui.voice_selector.console`**
- Mock the Rich console for output verification
- `console.is_terminal` - False for non-TTY tests, True otherwise
- `console.print()` - Capture output for assertions

**Mock: `eleven_video.ui.voice_selector.Prompt`**
- Mock Rich Prompt.ask() for user input simulation
- Return values: "0", "1", "99", "abc" for various test scenarios

**Mock: `ElevenLabsAdapter`**
- `list_voices(use_cache=True)` - Return mock VoiceInfo list
- For error tests: Raise `Exception("API Error")`

---

## Required data-testid Attributes

**Not applicable** - This story is CLI-only (no web UI).

---

## Implementation Checklist

### Test: test_voice_selector_can_be_imported (3.3-UNIT-001)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make this test pass:**
- [ ] Create file `eleven_video/ui/voice_selector.py`
- [ ] Define `VoiceSelector` class with `__init__(self, adapter)`
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorDisplay::test_voice_selector_can_be_imported -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Tests: Display methods (3.3-UNIT-002, 003)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make these tests pass:**
- [ ] Import Rich Table, Panel, console from eleven_video.ui.console
- [ ] Implement `_display_voice_list(voices: list[VoiceInfo])` method
- [ ] Add "[0] Default (Adam Stone)" as first row
- [ ] Iterate and add numbered voice rows with name and category
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorDisplay -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Tests: Input handling (3.3-UNIT-004, 005, 006, 007)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make these tests pass:**
- [ ] Import Prompt from rich.prompt
- [ ] Implement `_get_user_selection(voices: list[VoiceInfo]) -> Optional[str]`
- [ ] Parse user input as integer
- [ ] Return None for "0" (default voice)
- [ ] Return `voices[index-1].voice_id` for valid 1-N
- [ ] Handle invalid numbers (out of range) → return None with warning
- [ ] Handle non-numeric input (ValueError) → return None with warning
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorInput -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Tests: Interactive flow (3.3-UNIT-008, 009)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make these tests pass:**
- [ ] Implement `select_voice_interactive() -> Optional[str]`
- [ ] Check `console.is_terminal` for non-TTY handling
- [ ] Call `self._adapter.list_voices(use_cache=True)`
- [ ] Call `_display_voice_list(voices)`
- [ ] Call `_get_user_selection(voices)` and return result
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorInteractive -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Tests: Error handling (3.3-UNIT-010, 011)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make these tests pass:**
- [ ] Wrap `list_voices()` call in try/except
- [ ] On exception: print warning and return None
- [ ] If list is empty: print message and return None
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorErrorHandling -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.25 hours

---

### Tests: Non-TTY fallback (3.3-UNIT-012, 013)

**File:** `eleven_video/ui/voice_selector.py`

**Tasks to make these tests pass:**
- [ ] At start of `select_voice_interactive()`: check `console.is_terminal`
- [ ] If not terminal: print message and return None immediately
- [ ] Run test: `uv run pytest tests/ui/test_voice_selector.py::TestNonTTYFallback -v`
- [ ] ✅ Tests pass (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: CLI integration (3.3-UNIT-014) - ALREADY PASSING

This test already passes because `--voice` flag is already handled in `main.py` from Story 2.6.

---

### Task: Export VoiceSelector (Story Task 5)

**File:** `eleven_video/ui/__init__.py`

**Tasks:**
- [ ] Add `from eleven_video.ui.voice_selector import VoiceSelector` to exports
- [ ] Verify import works from main.py

**Estimated Effort:** 0.1 hours

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/ui/test_voice_selector.py -v

# Run specific test file
uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorDisplay -v

# Run tests with coverage
uv run pytest tests/ui/test_voice_selector.py -v --cov=eleven_video.ui.voice_selector

# Debug specific test
uv run pytest tests/ui/test_voice_selector.py::TestVoiceSelectorDisplay::test_voice_selector_can_be_imported -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing (13/14)
- ✅ Factory functions created for test data
- ✅ Mock requirements documented
- ✅ Implementation checklist created

---

### GREEN Phase (Complete) ✅

**DEV Agent Responsibilities:**

- ✅ VoiceSelector class created in `eleven_video/ui/voice_selector.py`
- ✅ All 14 unit tests passing
- ✅ VoiceSelector exported from `eleven_video.ui` module

**Code Review Fix (2025-12-19):**

- ✅ Added VoiceSelector integration to `main.py` generate() function
- ✅ Voice selection now triggers when `--voice` flag not provided

**Verification:**
```
========================== test session starts ==========================
========================== 14 passed in 4.61s ===========================
```

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick one failing test** from implementation checklist (start with 3.3-UNIT-001)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to make that specific test pass
4. **Run the test** to verify it now passes (green)
5. **Check off the task** in implementation checklist
6. **Move to next test** and repeat

**Recommended Order:**
1. 3.3-UNIT-001 - Create VoiceSelector class (enables all other tests)
2. 3.3-UNIT-002, 003 - Display methods
3. 3.3-UNIT-004, 005, 006, 007 - Input handling
4. 3.3-UNIT-008, 009 - Interactive flow
5. 3.3-UNIT-010, 011 - Error handling
6. 3.3-UNIT-012, 013 - Non-TTY fallback

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability)
3. **Extract duplications** (DRY principle)
4. **Ensure tests still pass** after each refactor

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `uv run pytest tests/ui/test_voice_selector.py -v`
2. **Begin implementation** using checklist as guide
3. **Work one test at a time** (red → green for each)
4. **When all tests pass**, refactor code for quality
5. **When complete**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

- **fixture-architecture.md** - Test fixture patterns (inline mocks used)
- **data-factories.md** - Factory patterns with overrides
- **test-quality.md** - Given-When-Then, determinism, isolation
- **selector-resilience.md** - Console.is_terminal detection

---

## Notes

- **Dependency on Story 3.1**: `ElevenLabsAdapter.list_voices()` must be implemented (already done)
- **Rich library**: All UI uses Rich for terminal output - follow existing patterns
- **Test 3.3-UNIT-014 passes**: CLI already handles `--voice` flag from Story 2.6
- **Coverage target**: ≥80% for new VoiceSelector code

---

**Generated by BMad TEA Agent** - 2025-12-19
