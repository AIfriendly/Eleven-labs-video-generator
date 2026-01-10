"""
Quota domain models for API usage quota tracking.

Used by adapters to report quota information (Story 5.4).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class QuotaInfo:
    """Domain model for API quota information.
    
    Represents the quota/limit information for an API service.
    Used by adapters and displayed in the status command.
    
    Attributes:
        service: Human-readable name of the API service (e.g., "ElevenLabs", "Gemini").
        used: Amount of quota currently used, or None if unavailable.
        limit: Maximum quota limit, or None if unavailable.
        unit: Unit of measurement (e.g., "chars", "rpm", "tpm").
        reset_date: When the quota resets, or None if unknown.
    """
    service: str
    used: Optional[int]
    limit: Optional[int]
    unit: str
    reset_date: Optional[datetime]
    
    @property
    def percent_used(self) -> Optional[float]:
        """Calculate percentage of quota used.
        
        Returns:
            Percentage (0-100) if both used and limit are available,
            None otherwise.
        """
        if self.used is None or self.limit is None or self.limit == 0:
            return None
        return (self.used / self.limit) * 100
    
    @property
    def is_available(self) -> bool:
        """Check if quota information is available.
        
        Returns:
            True if limit is known, False otherwise.
        """
        return self.limit is not None
    
    @property
    def remaining(self) -> Optional[int]:
        """Calculate remaining quota.
        
        Returns:
            Remaining quota if both used and limit are available,
            None otherwise.
        """
        if self.used is None or self.limit is None:
            return None
        return self.limit - self.used
