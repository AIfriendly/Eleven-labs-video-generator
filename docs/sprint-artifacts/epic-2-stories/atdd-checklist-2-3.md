# ATDD Checklist - Epic 2, Story 2.3: Default Image Generation from Script

**Date:** 2025-12-16
**Author:** Murat (TEA Agent)
**Primary Test Level:** Unit + Integration (API Adapter)

---

## Story Summary

Migrate `GeminiAdapter` from deprecated `google-generativeai` SDK to `google-genai` and implement `generate_images()` method for visual content generation.

**As a** user,
**I want** the system to automatically generate matching images from the script using Gemini Nano Banana,
**So that** I have visual content for my video without needing to create images manually.

---

## Acceptance Criteria

1. **AC1:** Images generated from thematic keywords extracted from script sentences using `gemini-2.5-flash-image`
2. **AC2:** API key security - never exposed in logs, terminal, or error messages
3. **AC3:** Progress indicator shown with updates per image (FR23)
4. **AC4:** Empty/invalid script raises clear, actionable validation error
5. **AC5:** API errors (401, 429, 500, timeout) display user-friendly messages with corrective actions
6. **AC6:** Images returned as `List[Image]` domain models with metadata (`file_size_bytes`, `mime_type`)
7. **AC7:** Appropriate number of images generated (one per major sentence/paragraph)

---

## Failing Tests Created (RED Phase)

### Unit Tests (24 tests)

**File:** `tests/api/test_gemini_images.py`

| Test ID | Test Name | AC | Status | Verifies |
|---------|-----------|-----|--------|----------|
| 2.3-UNIT-001 | `test_generate_images_returns_list_of_images` | AC1 | RED | Valid script → returns images |
| 2.3-UNIT-002 | `test_generate_images_uses_nano_banana_model` | AC1 | RED | Uses `gemini-2.5-flash-image` model |
| 2.3-UNIT-003 | `test_generate_images_extracts_image_bytes` | AC1 | RED | Extracts bytes from `inline_data` |
| 2.3-UNIT-004 | `test_generate_images_appends_style_suffix` | AC1 | RED | Prompts have style suffix |
| 2.3-UNIT-005 | `test_api_key_never_in_logs_image_gen` | AC2 | RED | API key not in log output |
| 2.3-UNIT-006 | `test_api_key_never_in_error_messages_image_gen` | AC2 | RED | API key not in exceptions |
| 2.3-UNIT-007 | `test_progress_callback_invoked_per_image` | AC3 | RED | Callback called for each image |
| 2.3-UNIT-008 | `test_progress_format_generating_image_x_of_y` | AC3 | RED | Format "Generating image X of Y" |
| 2.3-UNIT-009 | `test_empty_script_raises_validation_error` | AC4 | RED | Empty script → ValidationError |
| 2.3-UNIT-010 | `test_whitespace_script_raises_validation_error` | AC4 | RED | Whitespace → ValidationError |
| 2.3-UNIT-011 | `test_auth_error_shows_user_friendly_message` | AC5 | RED | 401 → "Check GEMINI_API_KEY" |
| 2.3-UNIT-012 | `test_rate_limit_error_shows_retry_message` | AC5 | RED | 429 → rate limit message |
| 2.3-UNIT-013 | `test_server_error_shows_retry_message` | AC5 | RED | 500 → server error message |
| 2.3-UNIT-014 | `test_timeout_error_shows_timeout_message` | AC5 | RED | Timeout → timeout message |
| 2.3-UNIT-015 | `test_image_model_has_required_metadata` | AC6 | RED | Image has `mime_type`, `file_size_bytes` |
| 2.3-UNIT-016 | `test_images_returned_as_domain_models` | AC6 | RED | Returns `List[Image]` |
| 2.3-UNIT-017 | `test_multi_paragraph_generates_multiple_images` | AC7 | RED | 3 paragraphs → 3 images |
| 2.3-UNIT-018 | `test_single_sentence_generates_one_image` | AC7 | RED | 1 sentence → 1 image |
| 2.3-SDK-001 | `test_sdk_migration_generate_script_still_works` | SDK | RED | `generate_script()` works post-migration |
| 2.3-SDK-002 | `test_new_sdk_client_initialization` | SDK | RED | `genai.Client` used instead of `genai.configure` |

---

## Domain Model Requirements

### Image Model (NEW)

**File:** `eleven_video/models/domain.py`

```python
@dataclass
class Image:
    """Generated image from Gemini API (Story 2.3).
    
    Attributes:
        data: Raw image bytes (PNG format).
        mime_type: MIME type (e.g., "image/png").
        file_size_bytes: Size in bytes for downstream processing.
    """
    data: bytes
    mime_type: str = "image/png"
    file_size_bytes: Optional[int] = None
```

---

## Protocol Requirements

### ImageGenerator Protocol (NEW)

**File:** `eleven_video/api/interfaces.py`

```python
@runtime_checkable
class ImageGenerator(Protocol):
    """Protocol for image generation from script (Story 2.3)."""
    
    def generate_images(
        self,
        script: Script,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> List[Image]:
        """Generate images from script content.
        
        Args:
            script: The Script domain model to generate images for.
            progress_callback: Optional callback with format "Generating image X of Y".
            
        Returns:
            List of Image domain models with bytes and metadata.
            
        Raises:
            ValidationError: If script is empty or invalid.
            GeminiAPIError: If API call fails.
        """
        ...
```

---

## Mock Requirements

### Google GenAI SDK Mock (NEW SDK)

**Endpoint:** `client.models.generate_content(model=..., contents=...)`

**Success Response:**
```python
# Mock structure for new google-genai SDK
response.candidates[0].content.parts[0].inline_data.data = b"PNG_BYTES"
response.candidates[0].content.parts[0].inline_data.mime_type = "image/png"
```

**Error Responses:**
- 401 Unauthorized → `Exception("401 Unauthorized")`
- 429 Rate Limit → `Exception("429 Resource exhausted")`
- 500 Server Error → `Exception("500 Internal Server Error")`
- Timeout → `TimeoutError("Request timed out")`

---

## Test Fixtures Required

### New SDK Fixtures (Update `tests/api/conftest.py`)

```python
@pytest.fixture
def mock_genai_new_sdk():
    """Fixture providing mocked google-genai SDK (NEW)."""
    with patch("google.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_response = MagicMock()
        
        # Setup text generation response
        mock_text_part = MagicMock()
        mock_text_part.text = "Generated script"
        mock_text_part.inline_data = None
        
        # Setup image generation response
        mock_image_part = MagicMock()
        mock_image_part.inline_data = MagicMock()
        mock_image_part.inline_data.data = b"fake_png_bytes"
        mock_image_part.inline_data.mime_type = "image/png"
        
        mock_response.candidates[0].content.parts = [mock_image_part]
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client
        
        yield mock_client_cls, mock_client, mock_response
```

---

## Implementation Checklist

### Test: SDK Migration - `generate_script()` Still Works
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Update `pyproject.toml`: Replace `google-generativeai>=0.8.0` with `google-genai>=0.5.0`
- [ ] Run `uv pip install` to update dependencies
- [ ] Refactor `GeminiAdapter.__init__` to use `genai.Client(api_key=...)`
- [ ] Update `_generate_with_retry()` to use `client.models.generate_content(model=..., contents=...)`
- [ ] Update response parsing: `response.candidates[0].content.parts[0].text`
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestSDKMigration -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1-2 hours

---

### Test: Image Domain Model Exists
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Add `Image` dataclass to `eleven_video/models/domain.py`
- [ ] Include `data: bytes`, `mime_type: str`, `file_size_bytes: Optional[int]`
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestImageDomainModel -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 15 minutes

---

### Test: ImageGenerator Protocol Exists
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Add `ImageGenerator` protocol to `eleven_video/api/interfaces.py`
- [ ] Define `generate_images(script, progress_callback) -> List[Image]` signature
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestImageGeneratorProtocol -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 15 minutes

---

### Test: Image Generation from Valid Script
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Implement script segmentation (split by paragraphs/sentences)
- [ ] Create image prompts with style suffix
- [ ] Call `client.models.generate_content(model="gemini-2.5-flash-image", contents=prompt)`
- [ ] Parse response to extract `inline_data.data` and `inline_data.mime_type`
- [ ] Return `List[Image]` with metadata
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestImageGenerationSuccess -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 2-3 hours

---

### Test: Error Handling and Security
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Add validation: empty/whitespace script → `ValidationError`
- [ ] Reuse `_format_error()` pattern for user-friendly messages
- [ ] Ensure API key never in error messages (already implemented)
- [ ] Add `@retry` decorator for transient failures
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestImageGenApiErrorHandling -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: Progress Callback
**File:** `tests/api/test_gemini_images.py`

**Tasks to pass this test:**
- [ ] Accept `progress_callback` parameter in `generate_images()`
- [ ] Call callback with format "Generating image X of Y" for each image
- [ ] Run test: `uv run pytest tests/api/test_gemini_images.py::TestProgressIndicatorForImageGen -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 30 minutes

---

## Running Tests

```bash
# Run all failing tests for Story 2.3
uv run pytest tests/api/test_gemini_images.py -v

# Run specific test class
uv run pytest tests/api/test_gemini_images.py::TestImageGenerationSuccess -v

# Run with coverage
uv run pytest tests/api/test_gemini_images.py --cov=eleven_video.api.gemini -v

# Run integration test (requires GEMINI_API_KEY)
uv run pytest tests/api/test_gemini_images.py -m integration -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**
- ✅ All 20 tests written and failing
- ✅ Mock requirements documented for new SDK
- ✅ Domain model requirements specified
- ✅ Protocol requirements specified
- ✅ Implementation checklist created

### GREEN Phase (DEV Team - Next Steps)

1. **Pick one failing test** from implementation checklist (start with SDK migration)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** to pass that test
4. **Run the test** to verify green
5. **Move to next test** and repeat

### REFACTOR Phase (After All Tests Pass)

1. Verify all tests pass
2. Review code for quality
3. Extract duplications (style suffix, segmentation logic)
4. Optimize retry logic
5. Ensure tests still pass

---

## Special Notes

> [!CAUTION]
> **SDK Migration Impact:** The SDK migration affects existing `generate_script()` tests. Updating test fixtures is required.

> [!IMPORTANT]
> **Style Suffix:** All image prompts must append: `, photorealistic, cinematic composition, 16:9 aspect ratio, high quality`

> [!NOTE]
> **Segmentation Strategy:** Split script by paragraphs first, then by major sentences if paragraphs are too long.

---

## Knowledge Base References Applied

- **data-factories.md** - Script factory patterns for test data
- **test-quality.md** - Given-When-Then structure, one assertion per test
- **fixture-architecture.md** - Mock patterns for SDK testing
- **network-first.md** - Not applicable (SDK handles network)

---

**Generated by Murat (TEA Agent)** - 2025-12-16
