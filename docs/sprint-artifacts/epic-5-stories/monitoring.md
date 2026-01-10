# Real-Time API Usage Monitoring

The eleven-video CLI includes real-time API usage monitoring that tracks consumption and costs during video generation.

## Features

- **Live Cost Tracking**: See running totals for Gemini API costs
- **Character Tracking**: Monitor ElevenLabs character consumption
- **Session Summaries**: View complete breakdown at session end

## Understanding the Display

### Gemini (Pay-Per-Use)

Gemini API costs are displayed in dollars based on actual usage:

```
Gemini API: $0.75
  ├─ Input Tokens: 1,000,000 ($0.50)
  ├─ Output Tokens: 50,000 ($0.075)
  └─ Images: 5 ($0.20)
```

**Pricing (Gemini 2.5 Flash):**
- Input tokens: $0.50 per million
- Output tokens: $1.50 per million
- Images: $0.04 per image

### ElevenLabs (Subscription)

ElevenLabs uses a subscription model with monthly character quotas. The display shows character consumption only (not dollar costs):

```
ElevenLabs: 5,000 characters
```

This prevents displaying misleading "costs" since ElevenLabs usage consumes your monthly quota, not additional charges.

## Configuration

### Custom Pricing

You can override default pricing for Gemini if rates change:

```python
from eleven_video.monitoring.usage import PricingStrategy

PricingStrategy.configure({
    "gemini": {
        "input_token_price_per_million": 0.60,  # Updated rate
        "output_token_price_per_million": 1.80,
        "image_price": 0.05,
    }
})
```

### Resetting Usage

Usage tracking resets automatically between video generation sessions. You can also reset manually:

```python
from eleven_video.monitoring.usage import UsageMonitor, PricingStrategy

# Reset usage tracking
monitor = UsageMonitor.get_instance()
monitor.reset()

# Reset to default pricing
PricingStrategy.reset()
```

## Session Summary

At the end of each video generation, a summary is displayed:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            API Usage Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Gemini Cost: $1.05
  gemini-2.5-flash: $0.65
  gemini-2.5-flash-image: $0.40

ElevenLabs Characters: 5,000
  Voice: Rachel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Programmatic Access

Access usage data programmatically:

```python
from eleven_video.monitoring.usage import UsageMonitor

monitor = UsageMonitor.get_instance()
summary = monitor.get_summary()

# Summary structure:
# {
#     "total_cost": 1.05,  # Gemini only (ElevenLabs = $0)
#     "by_service": {
#         "gemini": {"metrics": {...}, "cost": 1.05},
#         "elevenlabs": {"metrics": {"characters": 5000}, "cost": 0.0}
#     },
#     "by_model": {
#         "gemini-2.5-flash": {"metrics": {...}, "cost": 0.65},
#         "gemini-2.5-flash-image": {"metrics": {...}, "cost": 0.40},
#         "Rachel": {"metrics": {"characters": 5000}, "cost": 0.0}
#     },
#     "events_count": 5
# }
```

## Constants

Import constants for consistent usage:

```python
from eleven_video.monitoring.usage import (
    SERVICE_GEMINI,
    SERVICE_ELEVENLABS,
    METRIC_INPUT_TOKENS,
    METRIC_OUTPUT_TOKENS,
    METRIC_CHARACTERS,
    METRIC_IMAGES,
    MODEL_GEMINI_FLASH,
    MODEL_GEMINI_FLASH_IMAGE,
    MODEL_GEMINI_PRO,
)
```

## Related Stories

- Story 5.1: Real-time API Usage Monitoring
- Story 5.2: Model-specific Usage Metrics
- Story 5.3: Live Consumption Data Viewing
- Story 5.4: API Quota Information Display
- Story 5.5: API Cost Tracking During Generation
