# ATDD Checklist - Epic 5, Story 5.5: API Cost Tracking During Generation

**Date:** 2026-01-09
**Author:** Revenant
**Primary Test Level:** Unit + Integration

---

## Story Summary

Users need to understand the financial impact of video generation in real-time. This story fixes the misleading cost display by differentiating between Gemini (pay-per-use with actual dollar costs) and ElevenLabs (subscription-based with character quotas).

**As a** user,  
**I want** the system to track API costs during video generation,  
**So that** I can understand the financial impact as it occurs.

---

## Acceptance Criteria

1. **AC #1:** When Gemini API calls are made, I see running dollar cost totals for Gemini usage
2. **AC #2:** When ElevenLabs API calls are made, I see character credit consumption (not dollar cost - subscription-based)
3. **AC #3:** Costs are displayed with appropriate formatting (`$0.0125` for Gemini, `5,000 chars` for ElevenLabs)
4. **AC #4:** Final summary shows Gemini dollar cost and ElevenLabs character consumption clearly separated
5. **AC #5:** Starting a new video resets tracking for the new session

---

## Failing Tests Created (RED Phase)

### Unit Tests (14 tests total)

**File:** `tests/monitoring/test_cost_tracking.py` (400+ lines)

#### P0 Tests - Cost Precision (Risk R-001)

- ✅ **Test:** `test_gemini_input_token_cost_precision`
  - **Status:** ✅ PASSED
  - **Verifies:** Gemini input token cost calculates within $0.0001 precision

- ✅ **Test:** `test_gemini_output_token_cost_precision`
  - **Status:** ✅ PASSED
  - **Verifies:** Gemini output token cost calculates within $0.0001 precision

- ✅ **Test:** `test_gemini_image_cost_precision`
  - **Status:** ✅ PASSED
  - **Verifies:** Gemini image cost calculates correctly

#### P0 Tests - Cost Accumulation

- ✅ **Test:** `test_cost_accumulates_across_multiple_calls`
  - **Status:** ✅ PASSED
  - **Verifies:** Costs accumulate correctly across multiple API calls

#### P0 Tests - ElevenLabs Subscription Model (FAILING - Requires Implementation)

- ❌ **Test:** `test_elevenlabs_returns_zero_cost`
  - **Status:** RED - ElevenLabs returns $0.55 instead of $0.00
  - **Verifies:** ElevenLabs cost is $0 (subscription-based)

- ✅ **Test:** `test_elevenlabs_tracks_character_count`
  - **Status:** ✅ PASSED
  - **Verifies:** Character count is tracked correctly

- ❌ **Test:** `test_elevenlabs_does_not_affect_total_cost`
  - **Status:** RED - Total cost is $1.60 instead of $0.50
  - **Verifies:** Total cost only includes Gemini, not fake ElevenLabs cost

#### P0 Tests - UI Display Differentiation (FAILING - Requires Implementation)

- ✅ **Test:** `test_gemini_displays_dollar_cost`
  - **Status:** ✅ PASSED
  - **Verifies:** Gemini shows dollar format

- ❌ **Test:** `test_elevenlabs_displays_character_credits_not_dollars`
  - **Status:** RED - Shows "$0.5500" instead of just characters
  - **Verifies:** ElevenLabs displays character count, not fake dollar cost

- ✅ **Test:** `test_display_formatting_ac3`
  - **Status:** ✅ PASSED
  - **Verifies:** Cost formatting matches AC #3 requirements

#### P1 Tests - Integration (FAILING - Requires Implementation)

- ❌ **Test:** `test_final_summary_separates_gemini_and_elevenlabs`
  - **Status:** RED - ElevenLabs cost is $0.55, not $0.00
  - **Verifies:** Final summary correctly separates services

- ✅ **Test:** `test_cost_accumulates_across_script_and_images`
  - **Status:** ✅ PASSED
  - **Verifies:** Cost accumulates across script + image generation

#### P2 Tests - Edge Cases

- ✅ **Test:** `test_zero_usage_shows_zero_cost`
  - **Status:** ✅ PASSED
  - **Verifies:** Zero usage shows $0.00

- ✅ **Test:** `test_session_reset_clears_accumulated_data`
  - **Status:** ✅ PASSED
  - **Verifies:** Session reset clears data

- ✅ **Test:** `test_multiple_sessions_independent`
  - **Status:** ✅ PASSED
  - **Verifies:** Multiple sessions are independent

---

## Data Factories Used

### Usage Factory

**File:** `tests/support/factories/usage_factory.py`

**Exports:**
- `create_usage_event(overrides?)` - Create mock usage event
- `create_pricing_config(overrides?)` - Create pricing configuration

**Example Usage:**

```python
from tests.support.factories.usage_factory import create_pricing_config

pricing = create_pricing_config({
    "gemini": {"input_token_price_per_million": 2.00}
})
```

---

## Fixtures Used

### Clean Monitor State

**File:** `tests/monitoring/test_cost_tracking.py`

**Fixture:** `clean_monitor_state`
- **Setup:** Resets PricingStrategy and UsageMonitor
- **Provides:** Clean UsageMonitor instance
- **Cleanup:** Resets both after test

**Example Usage:**

```python
def test_example(clean_monitor_state):
    monitor = clean_monitor_state
    monitor.track_usage(...)
```

---

## Mock Requirements

No external service mocking required for these tests. All tests use in-memory `UsageMonitor` and `UsageDisplay` components.

---

## Implementation Checklist

### Test: `test_elevenlabs_returns_zero_cost`

**File:** `tests/monitoring/test_cost_tracking.py`

**Tasks to make this test pass:**

- [ ] Update `PricingStrategy._defaults["elevenlabs"]["character_price_per_million"]` to `0.0`
- [ ] OR add `is_subscription_based` flag to skip cost calculation
- [ ] Run test: `uv run pytest tests/monitoring/test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_returns_zero_cost -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours

---

### Test: `test_elevenlabs_does_not_affect_total_cost`

**File:** `tests/monitoring/test_cost_tracking.py`

**Tasks to make this test pass:**

- [ ] Same fix as above (set ElevenLabs price to 0)
- [ ] Verify `total_cost` only includes Gemini
- [ ] Run test: `uv run pytest tests/monitoring/test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_does_not_affect_total_cost -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours (same fix)

---

### Test: `test_elevenlabs_displays_character_credits_not_dollars`

**File:** `tests/monitoring/test_cost_tracking.py`

**Tasks to make this test pass:**

- [ ] Update `UsageDisplay.__rich__()` to check service name
- [ ] For Gemini: display `${cost:.4f}` format
- [ ] For ElevenLabs: display `{chars:,} characters` format (no dollar sign)
- [ ] Run test: `uv run pytest tests/monitoring/test_cost_tracking.py::TestUsageDisplayDifferentiation::test_elevenlabs_displays_character_credits_not_dollars -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours

---

### Test: `test_final_summary_separates_gemini_and_elevenlabs`

**File:** `tests/monitoring/test_cost_tracking.py`

**Tasks to make this test pass:**

- [ ] Ensure ElevenLabs pricing is $0 (from Task 1)
- [ ] Verify by_service breakdown shows $0 for ElevenLabs
- [ ] Run test: `uv run pytest tests/monitoring/test_cost_tracking.py::TestFinalCostReport::test_final_summary_separates_gemini_and_elevenlabs -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.25 hours (same fix)

---

## Running Tests

```bash
# Run all failing tests for this story
uv run pytest tests/monitoring/test_cost_tracking.py -v

# Run specific test file
uv run pytest tests/monitoring/test_cost_tracking.py::TestElevenLabsSubscriptionModel -v

# Run tests in verbose mode with short traceback
uv run pytest tests/monitoring/test_cost_tracking.py -v --tb=short

# Run only failing tests
uv run pytest tests/monitoring/test_cost_tracking.py --lf -v
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ All tests written
- ✅ 4 tests failing as expected (RED)
- ✅ 11 tests passing (existing behavior correct)
- ✅ Fixtures use existing patterns
- ✅ Implementation checklist created

**Verification:**

```
FAILED tests\monitoring\test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_returns_zero_cost
FAILED tests\monitoring\test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_does_not_affect_total_cost
FAILED tests\monitoring\test_cost_tracking.py::TestUsageDisplayDifferentiation::test_elevenlabs_displays_character_credits_not_dollars
FAILED tests\monitoring\test_cost_tracking.py::TestFinalCostReport::test_final_summary_separates_gemini_and_elevenlabs

4 failed, 11 passed
```

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Fix PricingStrategy** - Set ElevenLabs `character_price_per_million` to `0.0`
2. **Update UsageDisplay** - Differentiate Gemini (dollar) from ElevenLabs (characters)
3. **Run tests** to verify they now pass (green)
4. **Check off tasks** in implementation checklist

**Key Principles:**

- One test at a time
- Minimal implementation
- Run tests frequently

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. Review code quality
2. Consider labeling "Gemini API Cost" instead of "Total Cost"
3. Ensure tests still pass after refactoring

---

## Next Steps

1. ✅ **Review this checklist** - ATDD tests created and verified
2. **Run failing tests** to confirm RED phase: `uv run pytest tests/monitoring/test_cost_tracking.py -v`
3. **Begin implementation** using implementation checklist as guide
4. **Work one test at a time** (red → green for each)
5. **When all tests pass**, update story status to 'Ready for Review'

---

## Knowledge Base References Applied

- **fixture-architecture.md** - Used existing `clean_monitor_state` pattern
- **data-factories.md** - Leveraged existing `usage_factory.py`
- **test-quality.md** - Given-When-Then format, one assertion per test concept

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/monitoring/test_cost_tracking.py -v --tb=short`

**Results:**

```
4 failed, 11 passed in 0.99s

FAILED tests/monitoring/test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_returns_zero_cost
- AssertionError: ElevenLabs should have $0 cost (subscription-based), got $0.5500

FAILED tests/monitoring/test_cost_tracking.py::TestElevenLabsSubscriptionModel::test_elevenlabs_does_not_affect_total_cost  
- AssertionError: Total cost should be $0.50 (Gemini only), got $1.60

FAILED tests/monitoring/test_cost_tracking.py::TestUsageDisplayDifferentiation::test_elevenlabs_displays_character_credits_not_dollars
- AssertionError: ElevenLabs line should show characters, not fake dollar cost: Elevenlabs: $0.5500

FAILED tests/monitoring/test_cost_tracking.py::TestFinalCostReport::test_final_summary_separates_gemini_and_elevenlabs
- AssertionError: ElevenLabs cost should be $0, got $0.55
```

**Summary:**

- Total tests: 14
- Passing: 11
- Failing: 4 (expected - requires implementation)
- Status: ✅ RED phase verified

---

## Notes

- **Critical Fix:** Change `PricingStrategy._defaults["elevenlabs"]["character_price_per_million"]` from `110.00` to `0.0`
- **UI Change:** Update `UsageDisplay.__rich__()` to show characters for ElevenLabs, not fake dollar cost
- **Risk R-001:** Cost precision tests all pass, confirming Gemini cost calculation is accurate

---

**Generated by BMad TEA Agent** - 2026-01-09
