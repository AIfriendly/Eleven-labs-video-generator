# ATDD Checklist - Epic 5, Story 2: Model-specific Usage Metrics for Gemini API

**Date:** 2026-01-06
**Author:** Revenant
**Primary Test Level:** Unit (with Integration support)

---

## Story Summary

Extend the `UsageMonitor.get_summary()` method to include a `by_model` breakdown that aggregates usage metrics by individual model IDs, enabling users to understand how different models (gemini-2.5-flash, gemini-2.5-pro, ElevenLabs voices) affect their usage and costs.

**As a** user
**I want** to receive model-specific usage metrics for the Google Gemini API
**So that** I can understand how different models affect my usage

---

## Acceptance Criteria

1. **Given** I am using multiple Gemini models, **When** I check API usage via `get_summary()`, **Then** I can see usage metrics broken down by specific model ID
2. **Given** the usage summary, **When** I view `by_model`, **Then** each model ID appears with its own token counts and cost subtotal
3. **Given** I use the same model for multiple tasks, **When** I check usage, **Then** all usage from that model is aggregated together
4. **Given** I am using ElevenLabs for TTS, **When** I check by_model breakdown, **Then** the ElevenLabs voice model ID is also broken down
5. **Given** the `UsageDisplay` UI panel (optional), **When** rendering live usage, **Then** per-model breakdown can be shown

---

## Failing Tests Created (RED Phase)

### Unit Tests (7 tests)

**File:** `tests/monitoring/test_model_specific_usage.py` (~240 lines)

| Test ID | Test Name | Status | Failure Reason | Verifies |
|---------|-----------|--------|----------------|----------|
| 5.2-UNIT-001 | `test_model_specific_aggregation` | RED | `KeyError: 'by_model'` | AC #1 - Multiple models tracked separately |
| 5.2-UNIT-002 | `test_same_model_aggregation` | RED | `KeyError: 'by_model'` | AC #3 - Same model aggregates |
| 5.2-UNIT-003 | `test_model_cost_calculation` | RED | `KeyError: 'by_model'` | AC #2 - Per-model cost accuracy |
| 5.2-UNIT-004 | `test_mixed_service_model_breakdown` | RED | `KeyError: 'by_model'` | AC #4 - ElevenLabs voice ID appears |
| 5.2-UNIT-005 | `test_image_model_in_by_model` | RED | `KeyError: 'by_model'` | Image model tracking |
| 5.2-UNIT-006 | `test_empty_usage_has_empty_by_model` | RED | `KeyError: 'by_model'` | Edge case - no events |
| 5.2-UNIT-007 | `test_by_model_matches_by_service_total` | RED | `KeyError: 'by_model'` | Cost consistency |

### Integration Tests (2 tests)

**File:** `tests/integration/test_multi_model_usage.py` (~115 lines)

| Test ID | Test Name | Status | Failure Reason | Verifies |
|---------|-----------|--------|----------------|----------|
| 5.2-INT-001 | `test_multi_model_pipeline_usage_tracking` | RED | `AssertionError: 'by_model' not in summary` | Realistic pipeline flow |
| 5.2-INT-002 | `test_by_model_consistency_with_events` | RED | `AssertionError: 'by_model' not in summary` | Aggregate consistency |

---

## Data Factories (Existing)

### Usage Factory

**File:** `tests/support/factories/usage_factory.py`

**Exports:**
- `create_usage_event(overrides?)` - Create mock usage event
- `create_pricing_config(overrides?)` - Create mock pricing configuration

**Note:** Factory already supports `model_id` field. No new factories needed.

---

## Fixtures Created (Existing)

### Clean Monitor State Fixture

**File:** Used in both test files (defined inline)

**Fixtures:**
- `clean_monitor_state` - Resets `UsageMonitor` and `PricingStrategy` before/after each test
  - **Setup:** Calls `PricingStrategy.reset()` and `monitor.reset()`
  - **Provides:** Clean `UsageMonitor` instance
  - **Cleanup:** Resets both after test (in finally block)

---

## Mock Requirements

**None required for Story 5.2**

This story only extends `UsageMonitor.get_summary()` which is pure Python logic with no external dependencies. The adapters (Gemini, ElevenLabs) already pass `model_id` to `track_usage()`.

---

## Required Implementation Changes

### File: `eleven_video/monitoring/usage.py`

Update `get_summary()` method to add `by_model` aggregation:

```python
def get_summary(self) -> dict[str, Any]:
    # ... existing aggregation by service ...
    
    # NEW: Aggregate by model
    aggregated_by_model: dict[str, dict[str, int]] = {}
    for event in events:
        if event.model_id not in aggregated_by_model:
            aggregated_by_model[event.model_id] = {}
        
        metric_key = event.metric_type.value
        if metric_key not in aggregated_by_model[event.model_id]:
            aggregated_by_model[event.model_id][metric_key] = 0
        
        aggregated_by_model[event.model_id][metric_key] += event.value
    
    # Calculate per-model costs (similar to by_service)
    by_model: dict[str, dict[str, Any]] = {}
    for model_id, metrics in aggregated_by_model.items():
        # Determine service from model_id or events (need to track service per model)
        # ... calculate costs using PricingStrategy ...
        by_model[model_id] = {
            "metrics": metrics,
            "cost": model_cost
        }
    
    return {
        "total_cost": round(total_cost, 2),
        "by_service": by_service,
        "by_model": by_model,  # NEW
        "events_count": len(events)
    }
```

**Note:** Need to also store/derive `service` per model for cost calculation, since different services have different pricing.

---

## Implementation Checklist

### Test: test_model_specific_aggregation (5.2-UNIT-001)

**File:** `tests/monitoring/test_model_specific_usage.py`

**Tasks to make this test pass:**

- [ ] Add `by_model` key to `get_summary()` return dict
- [ ] Implement model-level aggregation loop
- [ ] Group events by `model_id` (similar to `by_service` pattern)
- [ ] Store metrics dict per model
- [ ] Run test: `uv run pytest tests/monitoring/test_model_specific_usage.py::test_model_specific_aggregation -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1 hour

---

### Test: test_same_model_aggregation (5.2-UNIT-002)

**File:** `tests/monitoring/test_model_specific_usage.py`

**Tasks to make this test pass:**

- [ ] Ensure aggregation sums values for same model_id
- [ ] Verify aggregation logic handles multiple events per model
- [ ] Run test: `uv run pytest tests/monitoring/test_model_specific_usage.py::test_same_model_aggregation -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours (should pass once 5.2-UNIT-001 passes)

---

### Test: test_model_cost_calculation (5.2-UNIT-003)

**File:** `tests/monitoring/test_model_specific_usage.py`

**Tasks to make this test pass:**

- [ ] Track service along with model_id in aggregation (to get correct pricing)
- [ ] Calculate cost per model using `PricingStrategy.get_price(service, price_key)`
- [ ] Round cost to 4 decimal places for precision
- [ ] Run test: `uv run pytest tests/monitoring/test_model_specific_usage.py::test_model_cost_calculation -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 1.5 hours

---

### Test: test_mixed_service_model_breakdown (5.2-UNIT-004)

**File:** `tests/monitoring/test_model_specific_usage.py`

**Tasks to make this test pass:**

- [ ] Verify ElevenLabs voice IDs appear in by_model
- [ ] Ensure cross-service model tracking works
- [ ] Run test: `uv run pytest tests/monitoring/test_model_specific_usage.py::test_mixed_service_model_breakdown -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours (should pass with correct service tracking)

---

### Test: test_multi_model_pipeline_usage_tracking (5.2-INT-001)

**File:** `tests/integration/test_multi_model_usage.py`

**Tasks to make this test pass:**

- [ ] Verify all unit tests pass first
- [ ] Run integration test to confirm full pipeline works
- [ ] Run test: `uv run pytest tests/integration/test_multi_model_usage.py::test_multi_model_pipeline_usage_tracking -v`
- [ ] ✅ Test passes (green phase)

**Estimated Effort:** 0.5 hours (verification only)

---

## Running Tests

```bash
# Run all failing tests for Story 5.2 (unit)
uv run pytest tests/monitoring/test_model_specific_usage.py -v

# Run all failing tests for Story 5.2 (integration)
uv run pytest tests/integration/test_multi_model_usage.py -v

# Run specific test file
uv run pytest tests/monitoring/test_model_specific_usage.py::test_model_specific_aggregation -v

# Run all Story 5.2 tests together
uv run pytest tests/monitoring/test_model_specific_usage.py tests/integration/test_multi_model_usage.py -v

# Run tests with coverage
uv run pytest tests/monitoring/test_model_specific_usage.py --cov=eleven_video.monitoring.usage --cov-report=term-missing
```

---

## Red-Green-Refactor Workflow

### RED Phase (Complete) ✅

**TEA Agent Responsibilities:**

- ✅ 7 unit tests written and failing (`KeyError: 'by_model'`)
- ✅ 2 integration tests written and failing
- ✅ Fixtures reuse existing `clean_monitor_state` pattern
- ✅ Factory reuse: `usage_factory.py` already has model_id support
- ✅ Implementation checklist created with clear tasks

**Verification:**

```
$ uv run pytest tests/monitoring/test_model_specific_usage.py -v
=========================== 7 failed in 0.46s ===========================

$ uv run pytest tests/integration/test_multi_model_usage.py -v
=========================== 2 failed in 0.46s ===========================
```

- All tests run and fail as expected
- Failure messages are clear: `KeyError: 'by_model'` or `AssertionError`
- Tests fail due to missing implementation, not test bugs

---

### GREEN Phase (DEV Team - Next Steps)

**DEV Agent Responsibilities:**

1. **Pick first failing test** (`test_model_specific_aggregation`)
2. **Read the test** to understand expected behavior
3. **Implement minimal code** in `usage.py`:
   - Add `by_model` key to return dict
   - Implement aggregation by model_id
4. **Run the test** to verify it passes
5. **Check off task** in implementation checklist
6. **Move to next test** and repeat

**Key Principles:**

- One test at a time (don't try to fix all at once)
- Minimal implementation (don't over-engineer)
- Run tests frequently (immediate feedback)
- Use implementation checklist as roadmap

---

### REFACTOR Phase (DEV Team - After All Tests Pass)

**DEV Agent Responsibilities:**

1. **Verify all 9 tests pass** (7 unit + 2 integration)
2. **Review code for quality** - can the aggregation be combined with existing by_service loop?
3. **Extract duplications** - if model and service aggregation share logic, DRY it up
4. **Ensure tests still pass** after each refactor
5. **Update UsageDisplay** (optional Task 5) if time permits

---

## Next Steps

1. **Run failing tests** to confirm RED phase: `uv run pytest tests/monitoring/test_model_specific_usage.py tests/integration/test_multi_model_usage.py -v`
2. **Begin implementation** in `eleven_video/monitoring/usage.py`
3. **Work one test at a time** (red → green for each)
4. **When all tests pass**, refactor and consider optional UsageDisplay enhancement
5. **Update story status** to 'review' when complete

---

## Knowledge Base References Applied

This ATDD workflow consulted the following knowledge fragments:

- **data-factories.md** - Factory patterns (existing `usage_factory.py` extended)
- **test-quality.md** - Given-When-Then format, one assertion per test
- **fixture-architecture.md** - `clean_monitor_state` fixture pattern from Story 5.1

---

## Test Execution Evidence

### Initial Test Run (RED Phase Verification)

**Command:** `uv run pytest tests/monitoring/test_model_specific_usage.py tests/integration/test_multi_model_usage.py -v`

**Results:**

```
FAILED tests/monitoring/test_model_specific_usage.py::test_model_specific_aggregation - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_same_model_aggregation - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_model_cost_calculation - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_mixed_service_model_breakdown - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_image_model_in_by_model - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_empty_usage_has_empty_by_model - KeyError: 'by_model'
FAILED tests/monitoring/test_model_specific_usage.py::test_by_model_matches_by_service_total - KeyError: 'by_model'
FAILED tests/integration/test_multi_model_usage.py::test_multi_model_pipeline_usage_tracking - AssertionError
FAILED tests/integration/test_multi_model_usage.py::test_by_model_consistency_with_events - AssertionError
```

**Summary:**

- Total tests: 9
- Passing: 0 (expected)
- Failing: 9 (expected)
- Status: ✅ RED phase verified

---

## Notes

- Story 5.2 is a focused enhancement to an existing module (`UsageMonitor`)
- The `model_id` is already tracked in `UsageEvent` (Story 5.1), just needs aggregation
- Cost calculation requires knowing `service` per model - may need to track this in aggregation
- `UsageDisplay` enhancement (AC #5) is marked optional and can be deferred

---

**Generated by BMad TEA Agent** - 2026-01-06
