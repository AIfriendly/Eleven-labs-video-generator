# ATDD Checklist - Epic 3, Story 3.1: Custom Voice Model Selection

**Date:** 2025-12-18
**Author:** Revenant
**Primary Test Level:** Unit Tests (Backend-only story)

---

## Story Summary

This story enables users to select custom voice models for text-to-speech generation. It implements the backend API for voice selection, including voice listing, validation, and graceful fallback to the default voice when an invalid ID is provided.

**As a** user,
**I want** to specify a custom voice model for text-to-speech generation,
**So that** my video has the voice characteristics I prefer.

---

## Acceptance Criteria

1. **AC1**: Given I have access to multiple voice models, When I specify a voice ID via the pipeline, Then the ElevenLabs TTS uses my selected voice for audio generation.

2. **AC2**: Given I don't specify a voice model, When TTS generation runs, Then the system uses the default voice (Adam Stone - current behavior preserved).

3. **AC3**: Given I specify an invalid voice ID, When TTS generation runs, Then the system falls back to the default voice with a warning message.

4. **AC4**: Given I want to see available voices, When I call the voice listing functionality, Then I receive a list of available voices with their IDs and names.

---

## Passing Tests (GREEN Phase) ✅

### Unit Tests (15 tests)

**File:** `tests/api/test_elevenlabs_voices.py` (320 lines)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 3.1-UNIT-001 | `test_voiceinfo_can_be_imported` | ✅ GREEN | VoiceInfo model exists |
| 3.1-UNIT-002 | `test_voiceinfo_has_required_fields` | ✅ GREEN | VoiceInfo has voice_id, name, category, preview_url |
| 3.1-UNIT-003 | `test_voiceinfo_category_is_optional` | ✅ GREEN | Optional fields work correctly |
| 3.1-UNIT-004 | `test_voiceinfo_is_dataclass` | ✅ GREEN | VoiceInfo is a @dataclass |
| 3.1-UNIT-005 | `test_voicelister_protocol_can_be_imported` | ✅ GREEN | VoiceLister protocol exists |
| 3.1-UNIT-006 | `test_voicelister_is_runtime_checkable` | ✅ GREEN | VoiceLister is @runtime_checkable |
| 3.1-UNIT-007 | `test_elevenlabs_adapter_implements_voicelister` | ✅ GREEN | Adapter implements VoiceLister |
| 3.1-UNIT-008 | `test_list_voices_returns_list_of_voiceinfo` | ✅ GREEN | list_voices() returns list[VoiceInfo] |
| 3.1-UNIT-009 | `test_list_voices_handles_multiple_voices` | ✅ GREEN | Multiple voices mapped correctly |
| 3.1-UNIT-010 | `test_list_voices_handles_empty_response` | ✅ GREEN | Empty list handled gracefully |
| 3.1-UNIT-011 | `test_validate_voice_id_returns_true_for_valid_id` | ✅ GREEN | validate_voice_id() works for valid |
| 3.1-UNIT-012 | `test_validate_voice_id_returns_false_for_invalid_id` | ✅ GREEN | validate_voice_id() works for invalid |
| 3.1-UNIT-013 | `test_generate_speech_falls_back_with_warning_on_invalid_voice` | ✅ GREEN | Fallback + warning_callback (AC3) |
| 3.1-UNIT-014 | `test_generate_speech_no_warning_for_valid_voice` | ✅ GREEN | No warning for valid voice |
| 3.1-UNIT-015 | `test_generate_speech_uses_default_when_no_voice_specified` | ✅ GREEN | Default voice used (AC2) |

---

## Data Factories Created

### VoiceInfo Factory

**File:** `tests/api/test_elevenlabs_voices.py` (Factory functions at bottom of file)

**Exports:**

- `create_voice_info(voice_id, name, category, preview_url)` - Create VoiceInfo test data with overrides
- `create_mock_elevenlabs_voice(voice_id, name, category, preview_url)` - Create mock SDK Voice object

**Example Usage:**

```python
# Create VoiceInfo with defaults
voice = create_voice_info()

# Create with specific values
voice = create_voice_info(voice_id="custom-id", name="Custom Voice")

# Create mock SDK response
mock_voice = create_mock_elevenlabs_voice(voice_id="test", name="Test")
```

---

## Fixtures Created

This story uses the existing fixtures in `tests/fixtures/api_fixtures.py`:

- `ELEVENLABS_VOICES_RESPONSE` - Mock response for voices list API
- `mock_elevenlabs_voices` - Fixture for mocking voices list endpoint

**No new fixtures required** - existing infrastructure covers Story 3.1 needs.

---

## Mock Requirements

### ElevenLabs SDK Mock

**Method:** `client.voices.get_all()`

**Success Response (Mock):**

```python
mock_response = MagicMock()
mock_response.voices = [
    MagicMock(voice_id="21m00Tcm4TlvDq8ikWAM", name="Rachel", category="premade", preview_url=None),
    MagicMock(voice_id="AZnzlk1XvdvUeBnXmlld", name="Domi", category="premade", preview_url=None)
]
```

**Implementation Notes:**
- Uses `unittest.mock.patch.object(adapter, '_get_sdk_client')` pattern
- SDK returns `GetVoicesResponse` object with `voices` attribute
- Each voice has `voice_id`, `name`, `category`, `preview_url` attributes

---

## Required data-testid Attributes

**Not applicable** - This is a backend-only story with no UI components.

The interactive UI for voice selection is handled by **Story 3.3: Interactive Voice Selection Prompts**.

---

## Implementation Checklist

### Task 1: Add VoiceInfo Domain Model (AC: #4)

**Files:** `eleven_video/models/domain.py`

**Tests that will pass:**
- 3.1-UNIT-001: VoiceInfo can be imported
- 3.1-UNIT-002: VoiceInfo has required fields
- 3.1-UNIT-003: Optional fields work correctly
- 3.1-UNIT-004: VoiceInfo is a dataclass

**Tasks:**
- [x] 1.1: Add `VoiceInfo` dataclass to `eleven_video/models/domain.py`
- [x] 1.2: Include fields: `voice_id: str`, `name: str`, `category: Optional[str] = None`, `preview_url: Optional[str] = None`
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel -v`
- [x] ✅ All 4 VoiceInfo tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Task 2: Add VoiceLister Protocol (AC: #4)

**Files:** `eleven_video/api/interfaces.py`

**Tests that will pass:**
- 3.1-UNIT-005: VoiceLister can be imported
- 3.1-UNIT-006: VoiceLister is runtime_checkable

**Tasks:**
- [x] 3.1: Define `VoiceLister` protocol in `eleven_video/api/interfaces.py`
- [x] 3.2: Add `list_voices() -> list[VoiceInfo]` method signature
- [x] 3.3: Decorate with `@runtime_checkable`
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol::test_voicelister_protocol_can_be_imported tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol::test_voicelister_is_runtime_checkable -v`
- [x] ✅ Protocol tests pass (green phase)

**Estimated Effort:** 0.5 hours

---

### Task 3: Add list_voices() Method to ElevenLabsAdapter (AC: #4)

**Files:** `eleven_video/api/elevenlabs.py`

**Tests that will pass:**
- 3.1-UNIT-007: Adapter implements VoiceLister
- 3.1-UNIT-008: list_voices() returns list[VoiceInfo]
- 3.1-UNIT-009: Multiple voices handled
- 3.1-UNIT-010: Empty response handled

**Tasks:**
- [x] 2.1: Add `list_voices() -> list[VoiceInfo]` method to `ElevenLabsAdapter`
- [x] 2.2: Call `self._get_sdk_client().voices.get_all()` to fetch voices
- [x] 2.3: Map SDK `Voice` objects to `VoiceInfo` domain models
- [x] 2.4: Handle empty response gracefully (return empty list)
- [x] 2.5: Add retry logic consistent with existing adapter patterns
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_voices.py::TestListVoices -v`
- [x] ✅ All list_voices tests pass (green phase)

**Estimated Effort:** 1.5 hours

---

### Task 4: Add Voice ID Validation (AC: #3)

**Files:** `eleven_video/api/elevenlabs.py`

**Tests that will pass:**
- 3.1-UNIT-011: validate_voice_id returns True for valid
- 3.1-UNIT-012: validate_voice_id returns False for invalid

**Tasks:**
- [x] 4.1: Add `validate_voice_id(voice_id: str) -> bool` method
- [x] 4.2: Fetch voices list and check if voice_id exists
- [x] 4.3: Cache voice list to avoid repeated API calls (60s TTL implemented)
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceIdValidation -v`
- [x] ✅ Validation tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Task 5: Add Fallback with Warning Callback (AC: #2, #3)

**Files:** `eleven_video/api/elevenlabs.py`

**Tests that will pass:**
- 3.1-UNIT-013: Fallback with warning on invalid voice
- 3.1-UNIT-014: No warning for valid voice
- 3.1-UNIT-015: Default voice used when not specified

**Tasks:**
- [x] 4.3: Add `warning_callback: Optional[Callable[[str], None]] = None` parameter to `generate_speech()`
- [x] 4.4: In generate_speech, validate voice_id if provided
- [x] 4.5: If invalid, emit warning via callback and fallback to DEFAULT_VOICE_ID
- [x] 4.6: If valid or not specified, proceed without warning
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_voices.py::TestFallbackWithWarning tests/api/test_elevenlabs_voices.py::TestDefaultVoiceBehavior -v`
- [x] ✅ Fallback and default tests pass (green phase)

**Estimated Effort:** 1 hour

---

### Task 6: (Optional) Add Pipeline Integration (AC: #1)

**Files:** `eleven_video/orchestrator/video_pipeline.py`

**Note:** This task was deferred - pipeline implementation is handled in Story 3.3 (Interactive Voice Selection Prompts).

**Tasks:**
- [x] 5.1: Voice ID parameter already exists in `ElevenLabsAdapter.generate_speech()`
- [x] 5.2: Validation + fallback ensures callers can safely pass any voice ID
- [ ] 5.3: Write integration test for voice selection flow (requires API key)

**Estimated Effort:** Deferred to Story 3.3

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/api/test_elevenlabs_voices.py -v

# Run specific test group
uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel -v
uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol -v
uv run pytest tests/api/test_elevenlabs_voices.py::TestListVoices -v
uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceIdValidation -v
uv run pytest tests/api/test_elevenlabs_voices.py::TestFallbackWithWarning -v

# Run tests with coverage
uv run pytest tests/api/test_elevenlabs_voices.py -v --cov=eleven_video.api.elevenlabs --cov-report=term-missing

# Debug specific test
uv run pytest tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel::test_voiceinfo_can_be_imported -v -s
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All 15 tests written and failing
- ✅ Factory functions created for test data
- ✅ Mock requirements documented
- ✅ Implementation checklist created

**Verification:**

- All tests run and fail as expected (15 failed)
- Failure messages are clear (ImportError, AttributeError, TypeError)
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (Complete) ✅

**DEV Agent Responsibilities:**

1. ✅ All 15 tests now passing
2. ✅ VoiceInfo dataclass implemented
3. ✅ VoiceLister protocol implemented
4. ✅ list_voices() method implemented
5. ✅ validate_voice_id() method implemented
6. ✅ warning_callback parameter added

**Test Results:**
```
uv run pytest tests/api/test_elevenlabs_voices.py -v
=========================== 15 passed in 4.43s ===========================
```

**Suggested Order (All Complete):**
1. ✅ Task 1: VoiceInfo model (4 tests)
2. ✅ Task 2: VoiceLister protocol (2 tests)
3. ✅ Task 3: list_voices() method (4 tests)
4. ✅ Task 4: validate_voice_id() method (2 tests)
5. ✅ Task 5: Fallback with warning (3 tests)

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all tests pass** (green phase complete)
2. **Review code for quality** (readability, maintainability, performance)
3. **Consider caching** voice list to avoid repeated API calls
4. **Ensure tests still pass** after each refactor
5. **Update story file** with File List and Completion Notes

**Key Principles:**

- Tests provide safety net (refactor with confidence)
- Make small refactors (easier to debug if tests fail)
- Run tests after each change
- Don't change test behavior (only implementation)

---

## Next Steps

1. **Review this checklist** with team in standup or planning
2. **Run failing tests** to confirm RED phase: `uv run pytest tests/api/test_elevenlabs_voices.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red → green for each)
5. **Share progress** in daily standup
6. **When all tests pass**, refactor code for quality
7. **When refactoring complete**, update story status to 'done' in sprint-status.yaml

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns using overrides for VoiceInfo test data
- **test-quality.md** - Given-When-Then format, explicit assertions, isolated tests
- **fixture-architecture.md** - Reused existing ElevenLabs fixtures
- **selector-resilience.md** - Not applicable (backend-only story)
- **network-first.md** - Not applicable for unit tests

See `tea-index.csv` for complete knowledge fragment mapping.

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/api/test_elevenlabs_voices.py -v`

**Results:**

```
========================== test session starts ==========================
collected 15 items

tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel::test_voiceinfo_can_be_imported FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel::test_voiceinfo_has_required_fields FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel::test_voiceinfo_category_is_optional FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceInfoModel::test_voiceinfo_is_dataclass FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol::test_voicelister_protocol_can_be_imported FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol::test_voicelister_is_runtime_checkable FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceListerProtocol::test_elevenlabs_adapter_implements_voicelister FAILED
tests/api/test_elevenlabs_voices.py::TestListVoices::test_list_voices_returns_list_of_voiceinfo FAILED
tests/api/test_elevenlabs_voices.py::TestListVoices::test_list_voices_handles_multiple_voices FAILED
tests/api/test_elevenlabs_voices.py::TestListVoices::test_list_voices_handles_empty_response FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceIdValidation::test_validate_voice_id_returns_true_for_valid_id FAILED
tests/api/test_elevenlabs_voices.py::TestVoiceIdValidation::test_validate_voice_id_returns_false_for_invalid_id FAILED
tests/api/test_elevenlabs_voices.py::TestFallbackWithWarning::test_generate_speech_falls_back_with_warning_on_invalid_voice FAILED
tests/api/test_elevenlabs_voices.py::TestFallbackWithWarning::test_generate_speech_no_warning_for_valid_voice FAILED
tests/api/test_elevenlabs_voices.py::TestDefaultVoiceBehavior::test_generate_speech_uses_default_when_no_voice_specified FAILED

========================== 15 failed in 6.44s ===========================
```

**Summary:**

- Total tests: 15
- Passing: 0 (expected)
- Failing: 15 (expected)
- Status: ✅ RED phase verified

**Expected Failure Types:**
- VoiceInfo tests: `ImportError: cannot import name 'VoiceInfo' from 'eleven_video.models.domain'`
- VoiceLister tests: `ImportError: cannot import name 'VoiceLister' from 'eleven_video.api.interfaces'`
- list_voices tests: `AttributeError: 'ElevenLabsAdapter' object has no attribute 'list_voices'`
- validate_voice_id tests: `AttributeError: 'ElevenLabsAdapter' object has no attribute 'validate_voice_id'`
- Fallback tests: `TypeError: generate_speech() got an unexpected keyword argument 'warning_callback'`

---

## Notes

- **Scope**: This is a backend-only story. Interactive UI is in Story 3.3.
- **Dependency**: Story 3.1 (API) → Story 3.3 (UI) → User can interactively select voices
- **Risk Mitigation**: R-001 from test-design-epic-3.md - validate voice exists before use, fallback to default with warning
- **Coverage Target**: ≥80% for new code

---

## Contact

**Questions or Issues?**

- Ask in team standup
- Tag @Revenant in Slack/Discord
- Refer to `.bmad/bmm/docs/tea-README.md` for workflow documentation
- Consult `.bmad/bmm/testarch/knowledge` for testing best practices

---

**Generated by BMad TEA Agent** - 2025-12-18
