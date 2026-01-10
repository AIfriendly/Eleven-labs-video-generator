"""
Real-time API Usage Monitoring module (Story 5.1, extended Story 5.2, 5.5).

Provides UsageMonitor for tracking API consumption and cost estimation
during video generation. Supports Gemini token counts and ElevenLabs
character counts with configurable pricing. Story 5.2 added by_model
breakdown for per-model usage metrics. Story 5.5 fixed ElevenLabs pricing.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, ClassVar, Optional


logger = logging.getLogger(__name__)

# Service Constants
SERVICE_GEMINI = "gemini"
SERVICE_ELEVENLABS = "elevenlabs"

# Metric Constants
METRIC_INPUT_TOKENS = "input_tokens"
METRIC_OUTPUT_TOKENS = "output_tokens"
METRIC_CHARACTERS = "characters"
METRIC_IMAGES = "images"

# Common Model Constants
MODEL_GEMINI_FLASH = "gemini-2.5-flash"
MODEL_GEMINI_FLASH_IMAGE = "gemini-2.5-flash-image"
MODEL_GEMINI_PRO = "gemini-2.5-pro"


class MetricType(str, Enum):
    """Types of usage metrics tracked."""
    INPUT_TOKENS = "input_tokens"
    OUTPUT_TOKENS = "output_tokens"
    CHARACTERS = "characters"
    IMAGES = "images"


@dataclass
class UsageEvent:
    """A single usage event recorded during video generation."""
    service: str
    model_id: str
    metric_type: MetricType
    value: int
    timestamp: datetime = field(default_factory=datetime.now)


class PricingStrategy:
    """Configurable pricing for API usage calculations.
    
    Default rates can be overridden via configure() method.
    Pricing is per million tokens/characters or per image.
    
    Addresses Risk R-001: Allows custom pricing configuration
    when default rates become stale.
    """
    
    # Default pricing per million units (tokens, chars) or per image
    _defaults: ClassVar[dict[str, dict[str, float]]] = {
        "gemini": {
            "input_token_price_per_million": 0.50,  # Gemini 1.5 Flash input
            "output_token_price_per_million": 1.50,  # Gemini 1.5 Flash output
            "image_price": 0.04,  # Per image generated
        },
        "elevenlabs": {
            # Subscription-based: Monthly quota, NO per-character cost
            # Set to 0.0 - cost tracking shows character usage only, not fake dollar amounts
            "character_price_per_million": 0.0,
        },
    }
    
    _overrides: ClassVar[dict[str, dict[str, Any]]] = {}
    _lock: ClassVar[Lock] = Lock()
    
    @classmethod
    def configure(cls, overrides: dict[str, dict[str, Any]]) -> None:
        """Apply custom pricing overrides.
        
        Args:
            overrides: Dict of service -> pricing config overrides.
                      e.g., {"gemini": {"input_token_price_per_million": 2.00}}
        """
        with cls._lock:
            cls._overrides = overrides
    
    @classmethod
    def reset(cls) -> None:
        """Reset all pricing overrides to defaults."""
        with cls._lock:
            cls._overrides = {}
    
    @classmethod
    def get_price(cls, service: str, price_key: str) -> float:
        """Get price for a service metric, considering overrides.
        
        Args:
            service: Service name (e.g., "gemini", "elevenlabs").
            price_key: Specific price key (e.g., "input_token_price_per_million").
            
        Returns:
            The price value, using override if configured, else default.
        """
        with cls._lock:
            # Check overrides first
            if service in cls._overrides and price_key in cls._overrides[service]:
                return float(cls._overrides[service][price_key])
            
            # Fall back to defaults
            if service in cls._defaults and price_key in cls._defaults[service]:
                return cls._defaults[service][price_key]
            
            return 0.0


class UsageMonitor:
    """Singleton monitor for tracking real-time API usage across services.
    
    Thread-safe singleton pattern ensures consistent usage tracking
    throughout video generation. Supports multiple services and metrics.
    
    Example:
        >>> monitor = UsageMonitor.get_instance()
        >>> monitor.track_usage("gemini", "gemini-1.5-flash", "input_tokens", 1000)
        >>> summary = monitor.get_summary()
    """
    
    _instance: ClassVar[Optional["UsageMonitor"]] = None
    _lock: ClassVar[Lock] = Lock()
    
    def __init__(self) -> None:
        """Initialize UsageMonitor. Use get_instance() instead."""
        self._events: list[UsageEvent] = []
        self._events_lock = Lock()
    
    @classmethod
    def get_instance(cls) -> "UsageMonitor":
        """Get or create the singleton UsageMonitor instance.
        
        Returns:
            The singleton UsageMonitor.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def _reset_instance(cls) -> None:
        """Reset the singleton instance (for testing only)."""
        with cls._lock:
            cls._instance = None
    
    def reset(self) -> None:
        """Clear all tracked events and reset state.
        
        Useful for starting a fresh tracking session or for testing.
        Note: Does NOT reset PricingStrategy overrides - use 
        PricingStrategy.reset() separately if needed.
        """
        with self._events_lock:
            self._events.clear()
    
    def track_usage(
        self,
        service: str,
        model_id: str,
        metric_type: str,
        value: int
    ) -> None:
        """Record a usage event.
        
        Args:
            service: Service name (e.g., "gemini", "elevenlabs").
            model_id: Model identifier used.
            metric_type: Type of metric (e.g., "input_tokens", "characters").
            value: The metric value (token count, character count, etc.).
        """
        try:
            mt = MetricType(metric_type)
        except ValueError:
            # Handle unknown metric types gracefully
            logger.debug(
                f"Unknown metric type '{metric_type}' - falling back to INPUT_TOKENS"
            )
            mt = MetricType.INPUT_TOKENS
        
        event = UsageEvent(
            service=service,
            model_id=model_id,
            metric_type=mt,
            value=value
        )
        
        with self._events_lock:
            self._events.append(event)
    
    def get_summary(self) -> dict[str, Any]:
        """Calculate usage summary with cost estimation.
        
        Returns:
            Dict containing:
            - total_cost: Estimated total cost in USD
            - by_service: Breakdown by service
            - by_model: Breakdown by model ID (Story 5.2)
            - events_count: Total number of events tracked
        """
        with self._events_lock:
            events = list(self._events)
        
        # Aggregate by service and metric type
        aggregated: dict[str, dict[str, int]] = {}
        
        # NEW (Story 5.2): Aggregate by model_id, also tracking service per model
        aggregated_by_model: dict[str, dict[str, int]] = {}
        model_to_service: dict[str, str] = {}  # Map model_id to service for pricing
        
        for event in events:
            # Existing: aggregate by service
            if event.service not in aggregated:
                aggregated[event.service] = {}
            
            metric_key = event.metric_type.value
            if metric_key not in aggregated[event.service]:
                aggregated[event.service][metric_key] = 0
            
            aggregated[event.service][metric_key] += event.value
            
            # NEW (Story 5.2): aggregate by model_id
            if event.model_id not in aggregated_by_model:
                aggregated_by_model[event.model_id] = {}
                model_to_service[event.model_id] = event.service
            
            if metric_key not in aggregated_by_model[event.model_id]:
                aggregated_by_model[event.model_id][metric_key] = 0
            
            aggregated_by_model[event.model_id][metric_key] += event.value
        
        # Calculate costs by service
        total_cost = 0.0
        by_service: dict[str, dict[str, Any]] = {}
        
        for service, metrics in aggregated.items():
            service_cost = self._calculate_cost(service, metrics)
            by_service[service] = {
                "metrics": metrics,
                "cost": round(service_cost, 4)
            }
            total_cost += service_cost
        
        # NEW (Story 5.2): Calculate costs by model
        by_model: dict[str, dict[str, Any]] = {}
        
        for model_id, metrics in aggregated_by_model.items():
            service = model_to_service[model_id]
            model_cost = self._calculate_cost(service, metrics)
            by_model[model_id] = {
                "metrics": metrics,
                "cost": round(model_cost, 4)
            }
        
        return {
            "total_cost": round(total_cost, 2),
            "by_service": by_service,
            "by_model": by_model,
            "events_count": len(events)
        }
    
    def _calculate_cost(self, service: str, metrics: dict[str, int]) -> float:
        """Calculate cost for a set of metrics from a given service.
        
        Args:
            service: Service name for pricing lookup.
            metrics: Dict of metric_type -> value.
            
        Returns:
            Cost in USD.
        """
        cost = 0.0
        for metric_type, value in metrics.items():
            if metric_type == "input_tokens":
                price = PricingStrategy.get_price(service, "input_token_price_per_million")
                cost += (value / 1_000_000) * price
            elif metric_type == "output_tokens":
                price = PricingStrategy.get_price(service, "output_token_price_per_million")
                cost += (value / 1_000_000) * price
            elif metric_type == "characters":
                price = PricingStrategy.get_price(service, "character_price_per_million")
                cost += (value / 1_000_000) * price
            elif metric_type == "images":
                price = PricingStrategy.get_price(service, "image_price")
                cost += value * price
        return cost
    
    def get_events(self) -> list[UsageEvent]:
        """Get a copy of all tracked events.
        
        Returns:
            List of UsageEvent objects.
        """
        with self._events_lock:
            return list(self._events)
