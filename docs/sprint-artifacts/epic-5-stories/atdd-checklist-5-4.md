# ATDD Checklist - Epic 5, Story 5-4: API Quota Information Display

**Date:** 2026-01-09
**Author:** Test Architect (Agent)
**Primary Test Level:** API / Component

---

## Story Summary

**As a** user,
**I want** to see API quota information during processing (via status check),
**So that** I know how much capacity I have remaining.

---

## Acceptance Criteria

1. **Given** I am using API services, **When** I run the status check command (`eleven-video status`), **Then** I see current quota usage and remaining capacity for ElevenLabs.
2. **Given** I am using API services, **When** I run the status check command, **Then** I see the relevant tier limits for Gemini (e.g., RPM/TPM) and current session usage against them (if total usage unavailable).
3. **Given** the quota display, **When** I view it, **Then** it clearly indicates if a limit is being approached (e.g., >80% usage colored yellow/red).
4. **Given** an API error fetching quota, **When** the status command runs, **Then** it fails gracefully for that service (shows "Unavailable") without crashing the entire status check.

---

## Failing Tests Created (RED Phase)

### Unit Tests (3 tests)

**File:** `tests/unit/adapters/test_elevenlabs_quota.py`

- ✅ **Test:** `test_get_quota_info_success`
  - **Status:** RED - Method `get_quota_info` missing in Adapter
  - **Verifies:** `ElevenLabsAdapter.get_quota_info` returns correct `QuotaInfo` object from mocked API response (AC #1).

- ✅ **Test:** `test_get_quota_info_api_failure`
  - **Status:** RED - Method `get_quota_info` missing
  - **Verifies:** Adapter handles API errors gracefully and returns unknown/unavailable state (AC #4).

- ✅ **Test:** `test_quota_info_domain_model`
  - **Status:** RED - `QuotaInfo` class missing
  - **Verifies:** `QuotaInfo` correctly calculates `percent_used` property.

### Component Tests (2 tests)

**File:** `tests/component/ui/test_quota_display.py`

- ✅ **Test:** `test_quota_display_rendering`
  - **Status:** RED - `QuotaDisplay` component missing
  - **Verifies:** UI correctly renders the Quota Table with provided data (AC #1, #2).

- ✅ **Test:** `test_quota_display_color_coding`
  - **Status:** RED - `QuotaDisplay` component missing
  - **Verifies:** Logic for coloring usage (>80% yellow, >90% red) works correctly (AC #3).

### Integration Tests (1 test)

**File:** `tests/integration/cli/test_status_command_quota.py`

- ✅ **Test:** `test_status_command_shows_quota`
  - **Status:** RED - Status command update missing
  - **Verifies:** Full `status` command flow integrates quota fetching and display (AC #1, #2, #4).

---

## Data Factories Created

### Quota Factory

**File:** `tests/support/factories/quota_factory.py`

**Exports:**

- `createQuotaInfo(overrides?)` - Create `QuotaInfo` domain object

**Example Usage:**

```python
from tests.support.factories.quota_factory import createQuotaInfo
quota = createQuotaInfo(service="ElevenLabs", used=500, limit=1000)
```

---

## Fixtures Created

### Mock API Fixtures

**File:** `tests/support/fixtures/api_mock_fixtures.py`

**Fixtures:**

- `mock_elevenlabs_quota` - Mocks `v1/user/subscription` response
  - **Setup:** Intercepts ElevenLabs API calls
  - **Provides:** Mock function to configure response
  - **Cleanup:** Unregisters mock

- `mock_gemini_quota` - Mocks Gemini model info (if applicable) or fallback
  - **Setup:** Intercepts Gemini API calls
  - **Provides:** Mock function
  - **Cleanup:** Unregisters mock

---

## Mock Requirements

### ElevenLabs Subscription Mock

**Endpoint:** `GET https://api.elevenlabs.io/v1/user/subscription`

**Success Response:**

```json
{
  "character_count": 12500,
  "character_limit": 50000,
  "next_character_count_reset_unix": 1735689600
}
```

**Failure Response:**

```json
{
  "detail": {
    "status": "quota_exceeded",
    "message": "Quota exceeded"
  }
}
```

---

## Required data-testid Attributes

### Status Command UI (Rich Console)

*Note: Rich renderables don't support `data-testid` directly like DOM, but we verify content strings/styles.*

- N/A for Terminal UI - Verification via `capsys` or `rich.console.Capture`

---

## Implementation Checklist

### Test: Unit - ElevenLabs Quota Parsing

**File:** `tests/unit/adapters/test_elevenlabs_quota.py`

**Tasks to make this pass:**

- [ ] Create `QuotaInfo` dataclass in `eleven_video/models/quota.py`
- [ ] Add `get_quota_info()` to `ElevenLabsAdapter`
- [ ] Implement SDK call `client.user.get_subscription()`
- [ ] Map response fields to `QuotaInfo`
- [ ] Run test: `pytest tests/unit/adapters/test_elevenlabs_quota.py`
- [ ] ✅ Test passes

### Test: Component - Quota Display

**File:** `tests/component/ui/test_quota_display.py`

**Tasks to make this pass:**

- [ ] Create `QuotaDisplay` class in `eleven_video/ui/quota_display.py`
- [ ] Implement `__rich__` or rendering method
- [ ] Add color logic for <80% (green), >80% (yellow), >90% (red)
- [ ] Run test: `pytest tests/component/ui/test_quota_display.py`
- [ ] ✅ Test passes

### Test: Integration - Status Command

**File:** `tests/integration/cli/test_status_command_quota.py`

**Tasks to make this pass:**

- [ ] Update `handle_status_command` in `cli/commands.py`
- [ ] Call `adapter.get_quota_info()` for all services
- [ ] Render `QuotaDisplay` with results
- [ ] Implement caching (R-004)
- [ ] Run test: `pytest tests/integration/cli/test_status_command_quota.py`
- [ ] ✅ Test passes

---

## Running Tests

```bash
# Run all failing tests for this story
pytest tests/unit/adapters/test_elevenlabs_quota.py tests/component/ui/test_quota_display.py tests/integration/cli/test_status_command_quota.py

# Run unit tests
pytest tests/unit/adapters/test_elevenlabs_quota.py

# Run component tests
pytest tests/component/ui/test_quota_display.py

# Run integration tests
pytest tests/integration/cli/test_status_command_quota.py
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written and failing
- ✅ Fixtures and factories created
- ✅ Mock requirements documented
- ✅ Implementation checklist created

### GREEN Phase (DEV Team - Next Steps)

1. Pick one failing test
2. Implement minimal code
3. Run test -> GREEN
4. Repeat

### REFACTOR Phase

- Extract common UI patterns
- Optimize caching logic
