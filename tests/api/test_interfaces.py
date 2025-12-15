"""
Tests for API interfaces and service health protocol.

Test IDs: 1.5-UNIT-001 to 1.5-UNIT-011
RED phase tests - these should fail until implementation is complete.
"""
import pytest
from typing import Protocol, runtime_checkable


class TestServiceHealthProtocol:
    """Tests for ServiceHealth protocol definition."""

    def test_protocol_can_be_imported(self):
        """[1.5-UNIT-001] AC1: ServiceHealth protocol should be importable."""
        # Given: The interfaces module exists
        # When: ServiceHealth is imported
        from eleven_video.api.interfaces import ServiceHealth
        # Then: It should not be None
        assert ServiceHealth is not None

    def test_protocol_is_runtime_checkable(self):
        """[1.5-UNIT-002] AC1: ServiceHealth should be runtime_checkable."""
        # Given: ServiceHealth protocol is defined
        from eleven_video.api.interfaces import ServiceHealth
        # When: Checking for runtime checkability
        # Then: Protocol should have __subclasshook__ (runtime_checkable decorator)
        assert hasattr(ServiceHealth, '__subclasshook__')

    def test_protocol_has_check_health_method(self):
        """[1.5-UNIT-003] AC1: ServiceHealth must define check_health() method."""
        # Given: ServiceHealth protocol
        from eleven_video.api.interfaces import ServiceHealth
        # When: Checking protocol interface
        # Then: check_health method should exist
        assert hasattr(ServiceHealth, 'check_health')

    def test_protocol_has_get_usage_method(self):
        """[1.5-UNIT-004] AC2: ServiceHealth must define get_usage() method."""
        # Given: ServiceHealth protocol
        from eleven_video.api.interfaces import ServiceHealth
        # When: Checking protocol interface
        # Then: get_usage method should exist
        assert hasattr(ServiceHealth, 'get_usage')

    def test_protocol_has_service_name_property(self):
        """[1.5-UNIT-005] ServiceHealth should expose service_name property."""
        # Given: ServiceHealth protocol
        from eleven_video.api.interfaces import ServiceHealth
        # When: Checking protocol interface
        # Then: service_name property should exist
        assert hasattr(ServiceHealth, 'service_name')


class TestHealthResult:
    """Tests for HealthResult dataclass."""

    def test_health_result_can_be_imported(self):
        """[1.5-UNIT-006] HealthResult should be importable from interfaces."""
        # Given: The interfaces module
        # When: HealthResult is imported
        from eleven_video.api.interfaces import HealthResult
        # Then: It should not be None
        assert HealthResult is not None

    def test_health_result_has_required_fields(self):
        """[1.5-UNIT-007] HealthResult must have status, message, latency_ms."""
        # Given: A successful health check result
        from eleven_video.api.interfaces import HealthResult
        # When: Creating a HealthResult with all fields
        result = HealthResult(status="ok", message="Connected", latency_ms=42.5)
        # Then: All fields should be accessible
        assert result.status == "ok"
        assert result.message == "Connected"
        assert result.latency_ms == 42.5

    def test_health_result_error_status(self):
        """[1.5-UNIT-008] HealthResult supports error status with None latency."""
        # Given: A failed health check
        from eleven_video.api.interfaces import HealthResult
        # When: Creating an error HealthResult
        result = HealthResult(status="error", message="Connection failed", latency_ms=None)
        # Then: Status should be error and latency None
        assert result.status == "error"
        assert result.latency_ms is None


class TestUsageResult:
    """Tests for UsageResult dataclass."""

    def test_usage_result_can_be_imported(self):
        """[1.5-UNIT-009] UsageResult should be importable from interfaces."""
        # Given: The interfaces module
        # When: UsageResult is imported
        from eleven_video.api.interfaces import UsageResult
        # Then: It should not be None
        assert UsageResult is not None

    def test_usage_result_has_required_fields(self):
        """[1.5-UNIT-010] UsageResult must have quota-related fields."""
        # Given: Available usage data from ElevenLabs
        from eleven_video.api.interfaces import UsageResult
        # When: Creating a UsageResult with all fields
        result = UsageResult(
            available=True,
            used=5000,
            limit=10000,
            unit="characters",
            raw_data={"tier": "free"}
        )
        # Then: All fields should be accessible
        assert result.available is True
        assert result.used == 5000
        assert result.limit == 10000
        assert result.unit == "characters"
        assert result.raw_data == {"tier": "free"}

    def test_usage_result_not_available(self):
        """[1.5-UNIT-011] UsageResult supports unavailable usage (e.g., Gemini)."""
        # Given: An API that doesn't expose usage (Gemini)
        from eleven_video.api.interfaces import UsageResult
        # When: Creating an unavailable UsageResult
        result = UsageResult(available=False, used=None, limit=None, unit=None, raw_data=None)
        # Then: available should be False
        assert result.available is False
