# ATDD Checklist - Story 2.2: Default Text-to-Speech Generation

**Date:** 2025-12-15  
**Author:** Murat (TEA Agent)  
**Primary Test Level:** Unit + Integration

---

## Story Summary

TTS generation from scripts using ElevenLabs SDK with proper error handling and security.

**As a** user  
**I want** the system to automatically generate TTS audio from the generated script using Eleven Labs  
**So that** I have voiceover for my video without needing to record it

---

## Acceptance Criteria

| AC | Description |
|----|-------------|
| AC1 | Audio file created with mp3_44100_128 format |
| AC2 | API key never exposed in logs or errors |
| AC3 | Progress indicator shown during generation |
| AC4 | Empty/invalid script shows clear error |
| AC5 | API errors (401, 429, 500, timeout) show user-friendly messages |
| AC6 | Audio returned with duration/size for downstream processing |

---

## Failing Tests Created (RED Phase)

### Unit Tests (21 tests)

**File:** `tests/api/test_elevenlabs_speech.py`

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 2.2-UNIT-001 | `test_generate_speech_returns_audio_bytes` | RED - No Audio model | AC1 |
| 2.2-UNIT-002 | `test_generate_speech_uses_mp3_44100_128_format` | RED - No generate_speech | AC1 |
| 2.2-UNIT-003 | `test_generate_speech_uses_default_voice` | RED - No generate_speech | AC1 |
| 2.2-UNIT-004 | `test_api_key_never_in_logs` | RED - No generate_speech | AC2 |
| 2.2-UNIT-005 | `test_api_key_never_in_error_messages` | RED - No ElevenLabsAPIError | AC2 |
| 2.2-UNIT-006 | `test_progress_callback_called_during_generation` | RED - No generate_speech | AC3 |
| 2.2-UNIT-007 | `test_empty_text_raises_validation_error` | RED - No generate_speech | AC4 |
| 2.2-UNIT-008 | `test_whitespace_only_text_raises_error` | RED - No generate_speech | AC4 |
| 2.2-UNIT-009 | `test_none_text_raises_error` | RED - No generate_speech | AC4 |
| 2.2-UNIT-010 | `test_auth_error_shows_user_friendly_message` | RED - No ElevenLabsAPIError | AC5 |
| 2.2-UNIT-011 | `test_rate_limit_error_suggests_retry` | RED - No ElevenLabsAPIError | AC5 |
| 2.2-UNIT-012 | `test_server_error_shows_retry_message` | RED - No ElevenLabsAPIError | AC5 |
| 2.2-UNIT-013 | `test_timeout_error_shows_timeout_message` | RED - No ElevenLabsAPIError | AC5 |
| 2.2-UNIT-014 | `test_audio_model_exists` | RED - No Audio class | AC6 |
| 2.2-UNIT-015 | `test_audio_model_has_required_attributes` | RED - No Audio class | AC6 |
| 2.2-UNIT-016 | `test_speech_generator_protocol_exists` | RED - No SpeechGenerator | Protocol |
| 2.2-UNIT-017 | `test_elevenlabs_adapter_has_generate_speech_method` | RED - No method | Protocol |
| 2.2-UNIT-018 | `test_elevenlabs_api_error_exists` | RED - No exception | Exception |
| 2.2-UNIT-019 | `test_adapter_accepts_settings_parameter` | RED - No settings support | Settings |

### Integration Tests (2 tests - skip in CI)

| Test ID | Test Name | Status | Verifies |
|---------|-----------|--------|----------|
| 2.2-INT-001 | `test_real_api_generates_audio` | SKIP - No API key | Real TTS |
| 2.2-INT-002 | `test_real_api_with_settings_class` | SKIP - No API key | Settings + Real TTS |

---

## Mock Requirements

### ElevenLabs SDK Mock

The test file includes two fixtures for mocking:

**`mock_elevenlabs_sdk`** — Success scenario:
```python
@pytest.fixture
def mock_elevenlabs_sdk():
    with patch("elevenlabs.ElevenLabs") as mock_client_cls:
        mock_client = MagicMock()
        mock_audio_iterator = iter([b'\xff\xfb\x90\x00', b'\x00\x00\x00\x00'])
        mock_client.text_to_speech.convert.return_value = mock_audio_iterator
        mock_client_cls.return_value = mock_client
        yield mock_client_cls, mock_client, mock_audio_iterator
```

**`mock_elevenlabs_sdk_error`** — Error scenario:
```python
@pytest.fixture
def mock_elevenlabs_sdk_error():
    with patch("elevenlabs.ElevenLabs") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        def set_error(error):
            mock_client.text_to_speech.convert.side_effect = error
        yield mock_client_cls, mock_client, set_error
```

---

## Implementation Checklist

### Task 1: Add Dependencies ✅

- [x] Add `elevenlabs>=1.0.0` to `pyproject.toml`
- [x] Run `uv sync` to install
- [x] Verify import works: `from elevenlabs import ElevenLabs`

**Status:** Complete - elevenlabs 2.27.0 installed

---

### Task 2: Create Audio Domain Model ✅

- [x] Add `Audio` dataclass to `eleven_video/models/domain.py`
- [x] Include attributes: `data: bytes`, `duration_seconds: Optional[float]`, `file_size_bytes: Optional[int]`
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestAudioDomainModel -v`
- [x] ✅ Tests 2.2-UNIT-014, 2.2-UNIT-015 pass (green)

**Status:** Complete

---

### Task 3: Add SpeechGenerator Protocol ✅

- [x] Add `SpeechGenerator` protocol to `eleven_video/api/interfaces.py`
- [x] Define signature: `generate_speech(text: str, voice_id: str, progress_callback: Optional[Callable]) -> Audio`
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestSpeechGeneratorProtocol -v`
- [x] ✅ Test 2.2-UNIT-016 passes (green)

**Status:** Complete

---

### Task 4: Add ElevenLabsAPIError Exception ✅

- [x] Add `ElevenLabsAPIError` class to `eleven_video/exceptions/custom_errors.py`
- [x] Mirror `GeminiAPIError` pattern
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestElevenLabsAPIErrorExists -v`
- [x] ✅ Test 2.2-UNIT-018 passes (green)

**Status:** Complete

---

### Task 5: Add Settings Support to ElevenLabsAdapter ✅

- [x] Modify `ElevenLabsAdapter.__init__` to accept optional `settings` parameter
- [x] Extract API key from `settings.elevenlabs_api_key.get_secret_value()` if provided
- [x] Keep existing `api_key` parameter for backward compatibility
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestSettingsSupport -v`
- [x] ✅ Test 2.2-UNIT-019 passes (green)

**Status:** Complete

---

### Task 6: Implement generate_speech Method ✅

- [x] Add `generate_speech(text, voice_id, progress_callback)` method to `ElevenLabsAdapter`
- [x] Validate text is not empty/whitespace before API call
- [x] Initialize ElevenLabs SDK client with API key
- [x] Call `client.text_to_speech.convert()` with:
  - `voice_id`: default `21m00Tcm4TlvDq8ikWAM`
  - `model_id`: `eleven_multilingual_v2`
  - `output_format`: `mp3_44100_128`
- [x] Collect iterator bytes into `Audio` model
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestTTSGenerationSuccess -v`
- [x] ✅ Tests 2.2-UNIT-001, 2.2-UNIT-002, 2.2-UNIT-003 pass (green)

**Status:** Complete

---

### Task 7: Implement Progress Callback ✅

- [x] Add progress callback invocation at start of generation
- [x] Pattern: `progress_callback("Generating audio...")`
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestProgressIndicatorForTTS -v`
- [x] ✅ Test 2.2-UNIT-006 passes (green)

**Status:** Complete

---

### Task 8: Implement Input Validation ✅

- [x] Check for empty, None, or whitespace-only text
- [x] Raise `ValidationError` before API call
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestInvalidScriptHandling -v`
- [x] ✅ Tests 2.2-UNIT-007, 2.2-UNIT-008, 2.2-UNIT-009 pass (green)

**Status:** Complete

---

### Task 9: Implement Error Handling ✅

- [x] Wrap SDK calls in try/except
- [x] Map exception messages to user-friendly errors (pattern from GeminiAdapter)
- [x] Add `_format_error()` method that sanitizes API key from messages
- [x] Handle: 401, 429, 500/503, TimeoutError
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestTTSApiErrorHandling -v`
- [x] ✅ Tests 2.2-UNIT-010 through 2.2-UNIT-013 pass (green)

**Status:** Complete

---

### Task 10: Implement API Key Security ✅

- [x] Ensure API key is never logged
- [x] Sanitize API key from all error messages
- [x] Run tests: `uv run pytest tests/api/test_elevenlabs_speech.py::TestApiKeySecurityForTTS -v`
- [x] ✅ Tests 2.2-UNIT-004, 2.2-UNIT-005 pass (green)

**Status:** Complete

---

### Task 11: Verify Full Test Suite ✅

- [x] Run all Story 2.2 tests: `uv run pytest tests/api/test_elevenlabs_speech.py -v`
- [x] All 21 unit tests pass
- [x] Run project regression: `uv run pytest -v`
- [x] No regressions (2 pre-existing profile test failures unrelated to Story 2.2)

**Status:** Complete

---

### Task 12 (Optional): Integration Testing

- [ ] Set `ELEVENLABS_API_KEY` in environment
- [ ] Run: `uv run pytest tests/api/test_elevenlabs_speech.py -m integration -v`
- [ ] Verify real audio generated

**Estimated Effort:** 0.5 hours

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/api/test_elevenlabs_speech.py -v

# Run specific test class
uv run pytest tests/api/test_elevenlabs_speech.py::TestTTSGenerationSuccess -v

# Run tests with coverage
uv run pytest tests/api/test_elevenlabs_speech.py --cov=eleven_video.api.elevenlabs -v

# Run integration tests (requires ELEVENLABS_API_KEY)
uv run pytest tests/api/test_elevenlabs_speech.py -m integration -v

# Debug specific test
uv run pytest tests/api/test_elevenlabs_speech.py::TestTTSGenerationSuccess::test_generate_speech_returns_audio_bytes -v --pdb
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All 21 unit tests written and failing
- ✅ Mock fixtures created for SDK
- ✅ Implementation checklist created
- ✅ Test patterns mirror Story 2.1 (GeminiAdapter)

**Verification:**

```
======================= 6 failed, 15 errors in 6.63s =======================
```

All failures are due to missing implementation:
- `ModuleNotFoundError: No module named 'elevenlabs'`
- `ImportError: cannot import name 'Audio' from 'eleven_video.models.domain'`
- `ImportError: cannot import name 'ElevenLabsAPIError'`
- `ImportError: cannot import name 'SpeechGenerator'`

---

### GREEN Phase (Complete) ✅

**DEV Agent Responsibilities:**

1. ✅ **Completed Task 1** - Added elevenlabs>=1.0.0 dependency
2. ✅ **Worked through all 11 tasks in order**
3. ✅ **Ran specific test class after each task to verify green**
4. ✅ **All tasks checked off as completed**

**Final Test Results:**

```
21 passed in 10.42s
```

**All 21 Story 2.2 unit tests pass.**

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

1. Extract common error handling to shared utility
2. Consider factory pattern for adapter creation
3. Optimize audio byte collection

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/api/test_elevenlabs_speech.py -v --tb=short`

**Summary:**
- Total tests: 21 (excluding 2 integration skips)
- Passing: 0 (expected)
- Failing: 6 + 15 errors (expected)
- Status: ✅ RED phase verified

**Expected Failure Reasons:**
- `ModuleNotFoundError: No module named 'elevenlabs'` — SDK not installed
- `ImportError: cannot import name 'Audio'` — Model not created
- `ImportError: cannot import name 'ElevenLabsAPIError'` — Exception not created
- `ImportError: cannot import name 'SpeechGenerator'` — Protocol not defined

---

## Notes

- Tests use same fixture patterns as `test_gemini_script.py`
- `mock_elevenlabs_sdk` fixture mirrors `mock_genai` pattern
- Integration tests skip automatically when `ELEVENLABS_API_KEY` not set
- All tests follow Given-When-Then structure

---

**Generated by BMad TEA Agent (Murat)** - 2025-12-15
