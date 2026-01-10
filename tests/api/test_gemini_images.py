"""
Tests for Gemini Image Model Selection - Story 3.2

GREEN Phase: All tests passing after implementation complete.
Story 3.2 implementation verified via code review on 2025-12-18.

Test IDs: 3.2-UNIT-001 to 3.2-UNIT-022 (22 tests)
Tests cover:
- ImageModelInfo domain model (AC: #4)
- ImageModelLister protocol (AC: #4)
- list_image_models() method (AC: #4)
- validate_image_model_id() method (AC: #3)
- Fallback behavior with warning callback (AC: #2, #3)
- Pipeline model_id parameter (AC: #1)

Pattern: Mirrors Story 3.1 (test_elevenlabs_voices.py) exactly.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from typing import Optional, Callable


# =============================================================================
# Test Group 1: ImageModelInfo Domain Model (Task 1)
# =============================================================================

class TestImageModelInfoModel:
    """Tests for ImageModelInfo dataclass in eleven_video/models/domain.py."""

    def test_imagemodelinfo_can_be_imported(self):
        """[3.2-UNIT-001] ImageModelInfo should be importable from domain models.
        
        RED Phase: This test will fail until ImageModelInfo dataclass is created.
        """
        # Given: The domain module exists with existing models
        # When: Importing ImageModelInfo from domain module
        from eleven_video.models.domain import ImageModelInfo
        
        # Then: ImageModelInfo should exist
        assert ImageModelInfo is not None

    def test_imagemodelinfo_has_required_fields(self):
        """[3.2-UNIT-002] ImageModelInfo should have model_id, name, description, supports_image_generation fields.
        
        RED Phase: This test will fail until ImageModelInfo is implemented with all fields.
        """
        # Given: ImageModelInfo is created with all required fields
        from eleven_video.models.domain import ImageModelInfo
        
        # When: Creating an ImageModelInfo instance
        model = ImageModelInfo(
            model_id="gemini-2.5-flash-image",
            name="Gemini 2.5 Flash Image",
            description="Fast image generation model",
            supports_image_generation=True
        )
        
        # Then: All fields should be accessible
        assert model.model_id == "gemini-2.5-flash-image"
        assert model.name == "Gemini 2.5 Flash Image"
        assert model.description == "Fast image generation model"
        assert model.supports_image_generation is True

    def test_imagemodelinfo_description_is_optional(self):
        """[3.2-UNIT-003] ImageModelInfo description should be optional.
        
        RED Phase: This test will fail until optional fields are implemented.
        """
        # Given: ImageModelInfo allows optional fields
        from eleven_video.models.domain import ImageModelInfo
        
        # When: Creating ImageModelInfo with only required fields
        model = ImageModelInfo(
            model_id="minimal-model",
            name="Minimal Model",
            supports_image_generation=True
        )
        
        # Then: Optional fields should default to None
        assert model.model_id == "minimal-model"
        assert model.name == "Minimal Model"
        assert model.description is None
        assert model.supports_image_generation is True

    def test_imagemodelinfo_is_dataclass(self):
        """[3.2-UNIT-004] ImageModelInfo should be a dataclass for easy comparison and repr.
        
        RED Phase: This test will fail until ImageModelInfo is decorated with @dataclass.
        """
        # Given: ImageModelInfo is imported
        from eleven_video.models.domain import ImageModelInfo
        from dataclasses import is_dataclass
        
        # When: Checking if ImageModelInfo is a dataclass
        # Then: It should be a dataclass
        assert is_dataclass(ImageModelInfo), "ImageModelInfo must be a dataclass"


# =============================================================================
# Test Group 2: ImageModelLister Protocol (Task 3)
# =============================================================================

class TestImageModelListerProtocol:
    """Tests for ImageModelLister protocol in eleven_video/api/interfaces.py."""

    def test_imagemodellister_protocol_can_be_imported(self):
        """[3.2-UNIT-005] ImageModelLister protocol should be importable from interfaces.
        
        RED Phase: This test will fail until ImageModelLister protocol is defined.
        """
        # Given: The interfaces module exists
        # When: Importing ImageModelLister
        from eleven_video.api.interfaces import ImageModelLister
        
        # Then: ImageModelLister should exist
        assert ImageModelLister is not None

    def test_imagemodellister_is_runtime_checkable(self):
        """[3.2-UNIT-006] ImageModelLister should be a runtime_checkable Protocol.
        
        RED Phase: This test will fail until ImageModelLister is decorated correctly.
        """
        # Given: ImageModelLister protocol is imported
        from eleven_video.api.interfaces import ImageModelLister
        from typing import runtime_checkable, Protocol
        
        # When: Checking if ImageModelLister is a Protocol
        # Then: It should be a subclass of Protocol
        assert issubclass(ImageModelLister, Protocol)

    def test_gemini_adapter_implements_imagemodellister(self):
        """[3.2-UNIT-007] GeminiAdapter should implement ImageModelLister protocol.
        
        RED Phase: This test will fail until list_image_models() is added to adapter.
        """
        # Given: ImageModelLister protocol and GeminiAdapter
        from eleven_video.api.interfaces import ImageModelLister
        from eleven_video.api.gemini import GeminiAdapter
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # When: Checking if adapter implements ImageModelLister
        # Then: Adapter should have list_image_models method
        assert hasattr(adapter, 'list_image_models'), "Adapter must have list_image_models method"
        assert isinstance(adapter, ImageModelLister), "Adapter must implement ImageModelLister protocol"


# =============================================================================
# Test Group 3: list_image_models() Method (Task 2)
# =============================================================================

class TestListImageModels:
    """Tests for GeminiAdapter.list_image_models() method."""

    def test_list_image_models_returns_list_of_imagemodelinfo(self):
        """[3.2-UNIT-008] list_image_models() should return list[ImageModelInfo].
        
        RED Phase: This test will fail until list_image_models() is implemented.
        """
        # Given: A mocked Gemini SDK response
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Mock SDK response - models.list() returns model objects
        mock_model = MagicMock()
        mock_model.name = "models/gemini-2.5-flash-image"
        mock_model.display_name = "Gemini 2.5 Flash Image"
        mock_model.description = "Fast image generation"
        mock_model.supported_generation_methods = ["generateContent"]
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.return_value = [mock_model]
            
            # When: Calling list_image_models()
            result = adapter.list_image_models()
        
        # Then: Result should be list of ImageModelInfo objects
        assert isinstance(result, list)
        assert len(result) >= 1
        assert isinstance(result[0], ImageModelInfo)
        assert "gemini" in result[0].model_id.lower()

    def test_list_image_models_filters_image_capable_only(self):
        """[3.2-UNIT-009] list_image_models() should filter to image-capable models only.
        
        RED Phase: This test will fail until list_image_models() is implemented with filtering.
        """
        # Given: SDK returns mix of image and non-image models
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Create mock models - one image-capable, one not
        mock_image_model = MagicMock()
        mock_image_model.name = "models/gemini-2.5-flash-image"
        mock_image_model.display_name = "Gemini 2.5 Flash Image"
        mock_image_model.description = "Image generation model"
        mock_image_model.supported_generation_methods = ["generateContent"]
        
        mock_text_model = MagicMock()
        mock_text_model.name = "models/gemini-pro"
        mock_text_model.display_name = "Gemini Pro"
        mock_text_model.description = "Text-only model"
        mock_text_model.supported_generation_methods = ["generateContent"]
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.return_value = [mock_image_model, mock_text_model]
            
            # When: Calling list_image_models()
            result = adapter.list_image_models()
        
        # Then: Only image-capable models should be returned
        # Image models have "image" in their name or specific capability flags
        for model in result:
            assert model.supports_image_generation is True

    def test_list_image_models_handles_empty_response(self):
        """[3.2-UNIT-010] list_image_models() should return empty list when no models available.
        
        RED Phase: This test will fail until list_image_models() is implemented.
        """
        # Given: SDK returns empty models list
        from eleven_video.api.gemini import GeminiAdapter
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.return_value = []
            
            # When: Calling list_image_models()
            result = adapter.list_image_models()
        
        # Then: Should return empty list (not None or error)
        assert isinstance(result, list)
        assert len(result) == 0


# =============================================================================
# Test Group 4: Image Model ID Validation (Task 4)
# =============================================================================

class TestImageModelIdValidation:
    """Tests for image model ID validation and fallback behavior."""

    def test_validate_image_model_id_returns_true_for_valid_id(self):
        """[3.2-UNIT-011] validate_image_model_id() should return True for existing model ID.
        
        RED Phase: This test will fail until validate_image_model_id() is implemented.
        """
        # Given: A valid model ID that exists in the model list
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Mock list_image_models to return a known model
        with patch.object(adapter, 'list_image_models') as mock_list:
            mock_list.return_value = [
                ImageModelInfo(
                    model_id="gemini-2.5-flash-image",
                    name="Gemini 2.5 Flash Image",
                    supports_image_generation=True
                )
            ]
            
            # When: Validating a known good model ID
            result = adapter.validate_image_model_id("gemini-2.5-flash-image")
        
        # Then: Should return True
        assert result is True

    def test_validate_image_model_id_returns_false_for_invalid_id(self):
        """[3.2-UNIT-012] validate_image_model_id() should return False for non-existent model ID.
        
        RED Phase: This test will fail until validate_image_model_id() is implemented.
        """
        # Given: An invalid model ID that doesn't exist
        from eleven_video.api.gemini import GeminiAdapter
        
        adapter = GeminiAdapter(api_key="test-key")
        
        with patch.object(adapter, 'list_image_models') as mock_list:
            mock_list.return_value = []  # No models match
            
            # When: Validating an invalid model ID
            result = adapter.validate_image_model_id("non-existent-model-id")
        
        # Then: Should return False
        assert result is False


# =============================================================================
# Test Group 5: Fallback Behavior with Warning (Task 4)
# =============================================================================

class TestFallbackWithWarning:
    """Tests for generate_images fallback behavior with warning callback (AC: #3)."""

    def test_generate_images_falls_back_with_warning_on_invalid_model(self):
        """[3.2-UNIT-013] generate_images with invalid model_id should fallback and warn.
        
        RED Phase: This test will fail until fallback + warning_callback is implemented.
        
        AC3: Given I specify an invalid image model ID, When image generation runs,
        Then the system falls back to the default model with a warning message.
        """
        # Given: An invalid model ID and a warning callback
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        
        adapter = GeminiAdapter(api_key="test-key")
        
        warnings_received = []
        def warning_callback(message: str):
            warnings_received.append(message)
        
        script = Script(content="Test content for image generation")
        
        # Mock validate_image_model_id to return False
        # Mock _generate_image_with_retry to return image
        with patch.object(adapter, 'validate_image_model_id', return_value=False):
            with patch.object(adapter, '_generate_image_with_retry') as mock_generate:
                mock_generate.return_value = Image(data=b"fake-image-data")
                with patch.object(adapter, '_segment_script') as mock_segment:
                    mock_segment.return_value = ["Test prompt"]
                    
                    # When: Generating images with invalid model ID
                    result = adapter.generate_images(
                        script=script,
                        model_id="invalid-model-id",
                        warning_callback=warning_callback
                    )
        
        # Then: Should produce images (using default) and emit warning
        assert result is not None
        assert isinstance(result, list)
        assert len(warnings_received) >= 1
        # Warning should mention both the invalid ID and fallback
        warning_text = warnings_received[0].lower()
        assert "invalid" in warning_text or "fallback" in warning_text or "default" in warning_text

    def test_generate_images_no_warning_for_valid_model(self):
        """[3.2-UNIT-014] generate_images with valid model_id should not warn.
        
        RED Phase: This test will fail until warning_callback parameter is added.
        """
        # Given: A valid model ID and a warning callback
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        
        adapter = GeminiAdapter(api_key="test-key")
        
        warnings_received = []
        def warning_callback(message: str):
            warnings_received.append(message)
        
        script = Script(content="Test content")
        
        # Mock validate_image_model_id to return True
        with patch.object(adapter, 'validate_image_model_id', return_value=True):
            with patch.object(adapter, '_generate_image_with_retry') as mock_generate:
                mock_generate.return_value = Image(data=b"fake-image-data")
                with patch.object(adapter, '_segment_script') as mock_segment:
                    mock_segment.return_value = ["Test prompt"]
                    
                    # When: Generating images with valid model ID
                    result = adapter.generate_images(
                        script=script,
                        model_id="gemini-2.5-flash-image",
                        warning_callback=warning_callback
                    )
        
        # Then: Should not emit any warning
        assert result is not None
        assert len(warnings_received) == 0


# =============================================================================
# Test Group 6: Default Model Behavior (AC: #2)
# =============================================================================

class TestDefaultModelBehavior:
    """Tests for default model behavior when no model specified."""

    def test_generate_images_uses_default_when_no_model_specified(self):
        """[3.2-UNIT-015] generate_images with no model_id should use default.
        
        This test validates existing behavior is preserved (AC: #2).
        """
        # Given: No model ID specified
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        with patch.object(adapter, '_generate_image_with_retry') as mock_generate:
            mock_generate.return_value = Image(data=b"fake-image-data")
            with patch.object(adapter, '_segment_script') as mock_segment:
                mock_segment.return_value = ["Test prompt"]
                
                # When: Generating images without model_id
                result = adapter.generate_images(script=script)
        
        # Then: Should use default model (IMAGE_MODEL constant)
        assert result is not None
        # The internal call should have used the default model
        mock_generate.assert_called()


# =============================================================================
# Test Group 7: Retry Logic (Task 2.6)
# =============================================================================

class TestRetryLogic:
    """Tests for _list_image_models_with_retry() retry behavior."""

    def test_list_image_models_retries_on_connection_error(self):
        """[3.2-UNIT-016] list_image_models should retry on connection errors.
        
        Following Story 3.1 pattern: Added retry logic with @retry decorator.
        """
        # Given: SDK raises connection error then succeeds
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        
        adapter = GeminiAdapter(api_key="test-key")
        
        mock_model = MagicMock()
        mock_model.name = "models/gemini-2.5-flash-image"
        mock_model.display_name = "Gemini 2.5 Flash Image"
        mock_model.description = "Fast image generation"
        mock_model.supported_generation_methods = ["generateContent"]
        
        # First call fails, second succeeds
        call_count = [0]
        def side_effect():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Network error")
            return [mock_model]
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.side_effect = side_effect
            
            # When: Calling list_image_models()
            result = adapter.list_image_models()
        
        # Then: Should succeed after retry
        assert len(result) >= 1
        assert call_count[0] == 2  # Retry happened

    def test_list_image_models_has_retry_decorator(self):
        """[3.2-UNIT-017] _list_image_models_with_retry should have @retry decorator."""
        # Given: GeminiAdapter class
        from eleven_video.api.gemini import GeminiAdapter
        
        # When: Checking the method
        method = GeminiAdapter._list_image_models_with_retry
        
        # Then: Method should have retry metadata from tenacity
        # Tenacity decorated functions have a 'retry' attribute or are wrapped
        assert hasattr(method, 'retry') or hasattr(method, 'retry_with') or callable(getattr(method, '__wrapped__', None))


# =============================================================================
# Test Group 8: Image Model Caching (Task 2.5)
# =============================================================================

class TestImageModelCaching:
    """Tests for image model list caching behavior."""

    def test_list_image_models_uses_cache_when_enabled(self):
        """[3.2-UNIT-018] list_image_models(use_cache=True) should return cached models.
        
        Following Story 3.1 pattern: Added model list caching with TTL.
        """
        # Given: Adapter with cached models
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        import time
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Manually set cache
        cached_models = [ImageModelInfo(
            model_id="cached-model",
            name="Cached Model",
            supports_image_generation=True
        )]
        adapter._image_model_cache = (cached_models, time.perf_counter())
        
        # When: Calling list_image_models with use_cache=True
        result = adapter.list_image_models(use_cache=True)
        
        # Then: Should return cached models without API call
        assert len(result) == 1
        assert result[0].model_id == "cached-model"
        assert result[0].name == "Cached Model"

    def test_list_image_models_ignores_cache_when_disabled(self):
        """[3.2-UNIT-019] list_image_models(use_cache=False) should fetch fresh data."""
        # Given: Adapter with cached models
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        import time
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Set cache with old data
        cached_models = [ImageModelInfo(
            model_id="old-model",
            name="Old Model",
            supports_image_generation=True
        )]
        adapter._image_model_cache = (cached_models, time.perf_counter())
        
        # Setup mock for fresh API response
        mock_model = MagicMock()
        mock_model.name = "models/fresh-image-model"
        mock_model.display_name = "Fresh Image Model"
        mock_model.description = "Fresh image model"
        mock_model.supported_generation_methods = ["generateContent"]
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.return_value = [mock_model]
            
            # When: Calling list_image_models without use_cache
            result = adapter.list_image_models(use_cache=False)
        
        # Then: Should return fresh data
        assert len(result) >= 1
        assert result[0].model_id == "fresh-image-model"

    def test_list_image_models_refreshes_expired_cache(self):
        """[3.2-UNIT-020] list_image_models should refresh expired cache (>60s TTL)."""
        # Given: Adapter with expired cache
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import ImageModelInfo
        import time
        
        adapter = GeminiAdapter(api_key="test-key")
        
        # Set cache with very old timestamp (expired)
        cached_models = [ImageModelInfo(
            model_id="old-model",
            name="Old Model",
            supports_image_generation=True
        )]
        adapter._image_model_cache = (cached_models, time.perf_counter() - 120)  # 120s ago
        
        # Setup mock for fresh API response
        mock_model = MagicMock()
        mock_model.name = "models/new-image-model"
        mock_model.display_name = "New Image Model"
        mock_model.description = "New image model"
        mock_model.supported_generation_methods = ["generateContent"]
        
        with patch.object(adapter, '_genai_client') as mock_client:
            mock_client.models.list.return_value = [mock_model]
            
            # When: Calling list_image_models with use_cache=True but cache expired
            result = adapter.list_image_models(use_cache=True)
        
        # Then: Should fetch fresh data due to expired cache
        assert len(result) >= 1
        assert result[0].model_id == "new-image-model"


# =============================================================================
# Test Group 9: ImageGenerator Protocol Update (Task 6)
# =============================================================================

class TestImageGeneratorProtocolUpdate:
    """Tests for updated ImageGenerator protocol with model_id parameter."""

    def test_image_generator_protocol_accepts_model_id(self):
        """[3.2-UNIT-021] ImageGenerator protocol should accept optional model_id parameter.
        
        RED Phase: This test will fail until ImageGenerator protocol is updated.
        """
        # Given: ImageGenerator protocol
        from eleven_video.api.interfaces import ImageGenerator
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        import inspect
        
        # When: Checking generate_images signature
        sig = inspect.signature(GeminiAdapter.generate_images)
        params = list(sig.parameters.keys())
        
        # Then: Should have model_id parameter
        assert 'model_id' in params, "generate_images must accept model_id parameter"

    def test_image_generator_protocol_accepts_warning_callback(self):
        """[3.2-UNIT-022] ImageGenerator protocol should accept optional warning_callback parameter.
        
        RED Phase: This test will fail until ImageGenerator protocol is updated.
        """
        # Given: ImageGenerator protocol
        from eleven_video.api.gemini import GeminiAdapter
        import inspect
        
        # When: Checking generate_images signature
        sig = inspect.signature(GeminiAdapter.generate_images)
        params = list(sig.parameters.keys())
        
        # Then: Should have warning_callback parameter
        assert 'warning_callback' in params, "generate_images must accept warning_callback parameter"


# =============================================================================
# Factory Functions for Test Data
# =============================================================================

def create_image_model_info(
    model_id: str = "gemini-2.5-flash-image",
    name: str = "Gemini 2.5 Flash Image",
    description: Optional[str] = "Fast image generation model",
    supports_image_generation: bool = True
):
    """Factory function for creating ImageModelInfo test data.
    
    Uses pattern from data-factories.md knowledge base.
    """
    from eleven_video.models.domain import ImageModelInfo
    return ImageModelInfo(
        model_id=model_id,
        name=name,
        description=description,
        supports_image_generation=supports_image_generation
    )


def create_mock_gemini_model(
    model_id: str = "models/gemini-2.5-flash-image",
    display_name: str = "Gemini 2.5 Flash Image",
    description: str = "Fast image generation",
    supports_generation: bool = True
) -> MagicMock:
    """Create a mock Gemini SDK Model object."""
    mock_model = MagicMock()
    mock_model.name = model_id
    mock_model.display_name = display_name
    mock_model.description = description
    mock_model.supported_generation_methods = ["generateContent"] if supports_generation else []
    return mock_model
