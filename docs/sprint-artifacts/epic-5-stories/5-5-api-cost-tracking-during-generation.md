# Story 5.5: API Cost Tracking During Generation

Status: Done


## Story

**As a** user,  
**I want** the system to track API costs during video generation,  
**so that** I can understand the financial impact as it occurs.

## Acceptance Criteria

1. **Given** I am generating a video, **When** Gemini API calls are made (script, images), **Then** I can see running dollar cost totals for Gemini usage.
2. **Given** I am generating a video, **When** ElevenLabs API calls are made (TTS), **Then** I see character credit consumption (not dollar cost, since ElevenLabs is subscription-based).
3. **Given** the cost/usage display, **When** viewing during generation, **Then** costs are displayed with appropriate formatting (`$0.0125` for Gemini, `5,000 chars` for ElevenLabs).
4. **Given** the generation completes, **When** viewing the final summary, **Then** I see Gemini dollar cost and ElevenLabs character consumption clearly separated.
5. **Given** I am running multiple generations, **When** starting a new video, **Then** the tracking resets for the new session.

## Tasks / Subtasks

- [x] **Task 1 (AC: #1, #2, #3):** Fix cost display to differentiate services
  - [x] Subtask 1.1: Update `UsageDisplay.__rich__()` to show Gemini as dollar cost (`$X.XX`)
  - [x] Subtask 1.2: Update `UsageDisplay.__rich__()` to show ElevenLabs as credit consumption (`X chars`)
  - [x] Subtask 1.3: Remove misleading ElevenLabs "cost" from `total_cost` calculation OR relabel to "Gemini API Cost"

- [x] **Task 2 (AC: #2):** Refactor PricingStrategy for service-specific behavior
  - [x] Subtask 2.1: Set ElevenLabs `character_price_per_million` to 0 (no per-call cost)
  - [-] Subtask 2.2: ~~add `is_subscription_based` flag~~ (N/A - price=0 approach works)
  - [x] Subtask 2.3: Ensure `total_cost` represents only pay-per-use services (Gemini)

- [x] **Task 3 (AC: #4):** Enhance session-end summary
  - [x] Subtask 3.1: Display "Gemini API Cost: $X.XX" instead of misleading "Total Cost" (ElevenLabs now shows chars only)
  - [x] Subtask 3.2: Display "ElevenLabs Credits Used: X characters" separately
  - [-] Subtask 3.3: ~~show quota remaining~~ (N/A - deferred to future enhancement)

- [x] **Task 4 (AC: #5):** Validate session reset behavior
  - [x] Subtask 4.1: Verify `UsageMonitor.reset()` clears tracking for new session
  - [x] Subtask 4.2: Confirm `VideoPipeline` resets monitor at session start (verified by test)

- [x] **Task 5:** P0 Unit Tests (Risk R-001 Mitigation)
  - [x] Subtask 5.1: [5.5-UNIT-001] Test token-to-cost calculation matches expected values within **$0.0001 precision**
  - [x] Subtask 5.2: [5.5-UNIT-002] Test cost accumulates correctly across multiple Gemini API calls
  - [x] Subtask 5.3: Test ElevenLabs returns 0 cost and shows character count only

- [x] **Task 6:** P1 Integration Test
  - [x] Subtask 6.1: [5.5-INT-001] Test final cost report is generated at end of flow (AC #4)
  - [x] Subtask 6.2: Verify cost accumulates correctly across script + image generation

- [x] **Task 7:** P2 Edge Case Tests
  - [x] Subtask 7.1: [5.5-UNIT-003] Test zero-usage scenarios (dry runs) show $0.00 cost
  - [x] Subtask 7.2: Test session reset clears accumulated data

## Dev Notes

### 🚨 CRITICAL: ElevenLabs is Subscription-Based

> [!CAUTION]
> **ElevenLabs does NOT have per-character API costs.**
> 
> - **Pricing Model**: Monthly subscription tiers with character quotas
> - **Free Tier**: 10,000 chars/month
> - **Paid Tiers**: Fixed monthly price with higher character limits
> 
> The current `PricingStrategy` incorrectly assigns `$110/million chars` to ElevenLabs, which is misleading. Users pay a **fixed subscription fee**, not per-character costs.

### Risk R-001: Inaccurate Cost Calculations

> [!IMPORTANT]
> **From test-design-epic-5.md (Risk R-001):**
> 
> *"Inaccurate cost calculations due to stale pricing rates or wrong token counts"*
> - **Probability**: 3 (Likely) | **Impact**: 3 (Major) | **Score**: 9
> - **Mitigation**: Implement `PricingStrategy` pattern with unit tests for each model; Allow config override for rates
> 
> **Quality Gate (MANDATORY):** Token-to-cost calculation must match expected values within **$0.0001 precision**.

### Correct Cost Model

| Service | Pricing Model | What to Display |
|---------|---------------|-----------------|
| **Gemini** | Pay-per-use (tokens, images) | Dollar cost: `$0.0125` |
| **ElevenLabs** | Subscription (monthly quota) | Credit usage: `5,000 chars` |

### Current Implementation Issue

```python
# CURRENT (Misleading):
_defaults = {
    "gemini": {...},  # ✅ Correct - actual per-token/image costs
    "elevenlabs": {
        "character_price_per_million": 110.00,  # ❌ WRONG - no per-char cost
    },
}
```

### Recommended Fix Options

**Option 1: Zero-cost for ElevenLabs (Minimal Change)**
```python
"elevenlabs": {
    "character_price_per_million": 0.0,  # Subscription-based, no per-call cost
}
```

**Option 2: Service-aware display (Better UX)**
```python
# In UsageDisplay.__rich__():
for service, data in summary['by_service'].items():
    if service == "gemini":
        lines.append(f"  Gemini API Cost: ${data['cost']:.4f}")
    elif service == "elevenlabs":
        chars = data['metrics'].get('characters', 0)
        lines.append(f"  ElevenLabs: {chars:,} characters used")
```

### Expected Display Output

**During Generation:**
```
┌─ Live API Usage ─────────────────────────────────┐
│ Gemini API Cost: $0.0625                          │
│ ElevenLabs: 5,000 characters used                 │
│                                                   │
│ By Model:                                         │
│   gemini-2.5-flash: $0.0350 (1M input, 50K out)  │
│   gemini-2.5-flash-image: $0.0275 (5 images)     │
│   Rachel (voice): 5,000 characters               │
└───────────────────────────────────────────────────┘
```

**Session Summary:**
```
╔══════════════════════════════════════════════════════════════╗
║                  VIDEO GENERATION COMPLETE                    ║
╠══════════════════════════════════════════════════════════════╣
║  Gemini API Cost: $0.0625                                     ║
║  ElevenLabs Credits: 5,000 characters                         ║
║                                                               ║
║  Video saved to: output/my_video.mp4                         ║
╚══════════════════════════════════════════════════════════════╝
```

### Previous Story Intelligence

**From Story 5.1:**
- `UsageMonitor` is thread-safe singleton with `track_usage()`
- **DO NOT** create new `Console()` - use `from eleven_video.ui.console import console`
- Tests must use `clean_monitor_state` fixture

**From Story 5.3:**
- `UsageDisplay.__rich__()` shows breakdown by service/model
- `_format_metrics()` formats token/character counts

**From Story 5.4:**
- ElevenLabs quota available via `get_quota_info()` - can integrate for "remaining" display

### Testing Standards

**Test ID Convention:**
```
[5.5-UNIT-001] Token-to-cost precision test
[5.5-UNIT-002] Cost accumulation test
[5.5-UNIT-003] Zero-usage scenario test
[5.5-INT-001] Final cost report integration test
```

**Quality Gate (from test-design-epic-5.md):**
- Cost Accuracy: Token-to-cost calculation must match expected values within **$0.0001 precision**
- UI changes must NOT break layout (visual verification)

### File Locations

**Modify:**
- `eleven_video/monitoring/usage.py` - Fix ElevenLabs pricing (set to 0)
- `eleven_video/ui/usage_panel.py` - Update display to differentiate Gemini cost vs ElevenLabs credits

**Test Files:**
- `tests/monitoring/test_cost_tracking.py` - NEW

### References

- [Source: docs/sprint-artifacts/test-design-epic-5.md#Risk R-001] - Cost accuracy requirements
- [Source: eleven_video/monitoring/usage.py#PricingStrategy] - Current incorrect ElevenLabs pricing
- [Source: docs/sprint-artifacts/5-4-api-quota-information-display.md] - ElevenLabs quota model

---

## Dev Agent Record

### Agent Model Used

Claude claude-sonnet-4-20250514

### Completion Notes List

- ✅ Fixed ElevenLabs pricing: Set `character_price_per_million` to 0.0 (subscription-based, no per-call cost)
- ✅ Updated `UsageDisplay.__rich__()` to show ElevenLabs as "X characters used" instead of fake dollar amount
- ✅ Gemini continues to show dollar cost format `$X.XXXX`
- ✅ Total cost now only includes Gemini (pay-per-use), not ElevenLabs
- ✅ All 15 ATDD tests pass (4 were failing before implementation)
- ✅ Updated legacy test `test_combined_service_costs` to reflect subscription model
- ✅ All monitoring tests pass, no regressions

### File List

- `eleven_video/monitoring/usage.py` (MODIFIED) - Set ElevenLabs price to 0.0
- `eleven_video/ui/usage_panel.py` (MODIFIED) - Differentiate Gemini/ElevenLabs display, fixed M-003 by-model consistency
- `tests/monitoring/test_cost_tracking.py` (NEW) - 15 ATDD tests for Story 5.5, fixed M-002 docstring
- `tests/monitoring/test_automation_expansion.py` (NEW) - 18 automation expansion tests (thread-safety, edge cases)
- `tests/monitoring/test_usage_monitor_extended.py` (MODIFIED) - Updated test for subscription model
- `docs/atdd-checklist-5-5.md` (NEW) - ATDD checklist document
- `docs/automation-summary-5-5.md` (NEW) - Test automation expansion summary


---

## Change Log

| Date       | Change                                                              |
|------------|---------------------------------------------------------------------|
| 2026-01-09 | Story created by Scrum Master agent                                 |
| 2026-01-09 | Updated to fix ElevenLabs cost model (subscription vs pay-per-use)  |
| 2026-01-09 | Quality review: Added R-001 risk reference, P0/P1/P2 test specs, precision requirement |
| 2026-01-09 | Implementation complete: All tasks done, 15 tests pass, ready for review |

---

## Notes for Developer

> [!WARNING]
> **Key Insight:** ElevenLabs is subscription-based with character quotas. Do NOT display fake "$X.XX" costs for ElevenLabs - show character consumption instead.

> [!TIP]
> **Recommended Approach:** Option 2 (service-aware display) provides better UX and correctly labels "Gemini API Cost" instead of misleading "Total Cost".
