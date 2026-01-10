from typing import Dict, Any
import uuid
from datetime import datetime

class MockUsageEvent:
    """Mock usage event for testing."""
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", str(uuid.uuid4()))
        self.timestamp = data.get("timestamp", datetime.now())
        self.service = data.get("service", "unknown")
        self.metric_type = data.get("metric_type", "tokens")
        self.value = data.get("value", 0)
        self.model_id = data.get("model_id", "default")
        self.metadata = data.get("metadata", {})

def create_usage_event(overrides: Dict[str, Any] = None) -> MockUsageEvent:
    """Create a mock usage event with defaults."""
    overrides = overrides or {}
    defaults = {
        "service": "gemini",
        "metric_type": "input_tokens",
        "value": 100,
        "model_id": "gemini-1.5-flash",
        "metadata": {"cost_estimate": 0.001}
    }
    return MockUsageEvent({**defaults, **overrides})

def create_pricing_config(overrides: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a mock pricing configuration."""
    overrides = overrides or {}
    defaults = {
        "gemini": {
            "input_token_price_per_million": 0.50,
            "output_token_price_per_million": 1.50
        },
        "elevenlabs": {
            "character_price_per_1000": 0.18
        }
    }
    return {**defaults, **overrides}
