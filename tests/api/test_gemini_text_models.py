"""
Tests for GeminiAdapter Text Model Listing - Story 3.5

Test Groups:
- Group 1: GeminiModelInfo domain model creation
- Group 2: list_text_models() method and caching
- Group 3: validate_text_model_id() method
- Group 4: generate_script() with model_id parameter

Test IDs: 3.5-UNIT-001 (Gemini model parameter in script generation)
Mirrors: tests/api/test_gemini_images.py (Story 3.2)
"""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch

from eleven_video.models.domain import GeminiModelInfo


# =============================================================================
# Test Group 1: GeminiModelInfo Domain Model - Creation
# =============================================================================

class TestGeminiModelInfo:
    """Tests for GeminiModelInfo dataclass creation and attributes."""

    def test_gemini_model_info_can_be_created_with_required_fields(self):
        """[P1] GeminiModelInfo should be creatable with required fields.
        
        Validates domain model structure is correct.
        """
        # Given: Required field values
        model_id = "gemini-2.5-flash"
        name = "Gemini 2.5 Flash"
        
        # When: Creating GeminiModelInfo
        model = GeminiModelInfo(model_id=model_id, name=name)
        
        # Then: Fields should be set correctly
        assert model.model_id == model_id
        assert model.name == name
        assert model.description is None  # Optional, default None
        assert model.supports_text_generation is True  # Default value

    def test_gemini_model_info_can_be_created_with_all_fields(self):
        """[P1] GeminiModelInfo should accept all optional fields.
        
        Validates all field combinations work.
        """
        # Given: All field values
        model_id = "gemini-2.5-pro"
        name = "Gemini 2.5 Pro"
        description = "Highest quality text generation"
        supports_text_generation = True
        
        # When: Creating GeminiModelInfo with all fields
        model = GeminiModelInfo(
            model_id=model_id,
            name=name,
            description=description,
            supports_text_generation=supports_text_generation
        )
        
        # Then: All fields should be set correctly
        assert model.model_id == model_id
        assert model.name == name
        assert model.description == description
        assert model.supports_text_generation is True


# =============================================================================
# Test Group 2: list_text_models() Method - 3.5-UNIT-001
# =============================================================================

class TestListTextModels:
    """Tests for GeminiAdapter.list_text_models() method."""

    @pytest.fixture
    def mock_genai_client(self):
        """Create a mock genai client for testing."""
        client = Mock()
        # Simulate models list response
        mock_model_1 = Mock()
        mock_model_1.name = "models/gemini-2.5-flash"
        mock_model_1.display_name = "Gemini 2.5 Flash"
        mock_model_1.description = "Fast text generation"
        
        mock_model_2 = Mock()
        mock_model_2.name = "models/gemini-2.5-pro"
        mock_model_2.display_name = "Gemini 2.5 Pro"
        mock_model_2.description = "High quality"
        
        # Include an image model to verify filtering
        mock_image_model = Mock()
        mock_image_model.name = "models/imagen-3.0-generate-001"
        mock_image_model.display_name = "Imagen 3"
        mock_image_model.description = "Image generation"
        
        client.models.list.return_value = [mock_model_1, mock_model_2, mock_image_model]
        return client

    def test_list_text_models_returns_gemini_model_info_list(self, mock_genai_client):
        """[P0] [3.5-UNIT-001] list_text_models() should return List[GeminiModelInfo].
        
        AC: #1 - Display a numbered list of available text generation model options.
        """
        # Given: A GeminiAdapter with mocked client
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = mock_genai_client
            adapter._text_model_cache = None
            adapter._text_model_cache_ttl = 60
            
            # When: Calling list_text_models
            models = adapter.list_text_models()
        
        # Then: Should return list of GeminiModelInfo objects
        assert isinstance(models, list)
        assert len(models) >= 1
        assert all(isinstance(m, GeminiModelInfo) for m in models)

    def test_list_text_models_filters_out_image_models(self, mock_genai_client):
        """[P0] [3.5-UNIT-001] list_text_models() should exclude image-specific models.
        
        Filters: Exclude models with 'image' or 'imagen' in the name.
        """
        # Given: A GeminiAdapter with mocked client that returns mixed models
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = mock_genai_client
            adapter._text_model_cache = None
            adapter._text_model_cache_ttl = 60
            
            # When: Calling list_text_models
            models = adapter.list_text_models()
        
        # Then: Should not include imagen model
        model_ids = [m.model_id for m in models]
        assert "imagen-3.0-generate-001" not in model_ids
        # Should include gemini text models
        assert any("gemini" in mid for mid in model_ids)

    def test_list_text_models_with_cache_enabled(self, mock_genai_client):
        """[P1] [3.5-UNIT-001] list_text_models(use_cache=True) should use cache if available.
        
        Caches model list for 60 seconds to reduce API calls.
        """
        # Given: A GeminiAdapter with existing cached models
        from eleven_video.api.gemini import GeminiAdapter
        
        cached_models = [
            GeminiModelInfo(model_id="cached-model", name="Cached Model")
        ]
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = mock_genai_client
            adapter._text_model_cache = (cached_models, time.perf_counter())
            adapter._text_model_cache_ttl = 60
            
            # When: Calling list_text_models with cache enabled
            models = adapter.list_text_models(use_cache=True)
        
        # Then: Should return cached models without API call
        assert models == cached_models
        # API should not be called
        mock_genai_client.models.list.assert_not_called()

    def test_list_text_models_cache_expires_correctly(self, mock_genai_client):
        """[P1] list_text_models() should refresh cache when TTL expires.
        
        Cache TTL is 60 seconds.
        """
        # Given: A GeminiAdapter with expired cached models
        from eleven_video.api.gemini import GeminiAdapter
        
        cached_models = [
            GeminiModelInfo(model_id="expired-model", name="Expired Model")
        ]
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = mock_genai_client
            # Set cache time to 120 seconds ago (expired)
            adapter._text_model_cache = (cached_models, time.perf_counter() - 120)
            adapter._text_model_cache_ttl = 60
            
            # When: Calling list_text_models with cache enabled
            models = adapter.list_text_models(use_cache=True)
        
        # Then: Should call API because cache expired
        mock_genai_client.models.list.assert_called_once()
        # Should return fresh models, not cached
        assert models != cached_models


# =============================================================================
# Test Group 3: validate_text_model_id() Method
# =============================================================================

class TestValidateTextModelId:
    """Tests for GeminiAdapter.validate_text_model_id() method."""

    @pytest.fixture
    def adapter_with_models(self):
        """Create adapter with mocked list_text_models."""
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter.list_text_models = Mock(return_value=[
                GeminiModelInfo(model_id="gemini-2.5-flash", name="Flash"),
                GeminiModelInfo(model_id="gemini-2.5-pro", name="Pro"),
            ])
            return adapter

    def test_validate_text_model_id_returns_true_for_valid_id(self, adapter_with_models):
        """[P0] validate_text_model_id() returns True for existing model ID."""
        # Given: An adapter with known models
        # When: Validating a known model ID
        result = adapter_with_models.validate_text_model_id("gemini-2.5-flash")
        
        # Then: Should return True
        assert result is True

    def test_validate_text_model_id_returns_false_for_invalid_id(self, adapter_with_models):
        """[P0] validate_text_model_id() returns False for non-existent model ID."""
        # Given: An adapter with known models
        # When: Validating an unknown model ID
        result = adapter_with_models.validate_text_model_id("nonexistent-model")
        
        # Then: Should return False
        assert result is False

    def test_validate_text_model_id_uses_cached_models(self, adapter_with_models):
        """[P1] validate_text_model_id() should use cached model list."""
        # Given: An adapter with mocked list_text_models
        # When: Validating a model ID
        adapter_with_models.validate_text_model_id("gemini-2.5-flash")
        
        # Then: Should call list_text_models with use_cache=True
        adapter_with_models.list_text_models.assert_called_with(use_cache=True)


# =============================================================================
# Test Group 4: generate_script() with model_id - 3.5-UNIT-001
# =============================================================================

class TestGenerateScriptWithModelId:
    """Tests for generate_script() with model_id parameter support."""

    def test_generate_script_accepts_model_id_parameter(self):
        """[P0] [3.5-UNIT-001] generate_script() should accept model_id parameter.
        
        AC: #2 - My selection is used for script generation.
        """
        # Given: A GeminiAdapter
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = Mock()
            adapter.validate_text_model_id = Mock(return_value=True)
            adapter.DEFAULT_MODEL = "gemini-2.5-flash-lite"
            
            # Mock the generate response
            mock_response = Mock()
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content = Mock()
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[0].text = "Generated script"
            adapter._genai_client.models.generate_content.return_value = mock_response
            
            # When: Calling generate_script with model_id
            from eleven_video.models.domain import Script
            result = adapter.generate_script(
                prompt="Test prompt",
                model_id="gemini-2.5-pro"
            )
        
        # Then: Should use the provided model_id
        call_args = adapter._genai_client.models.generate_content.call_args
        # Model is passed as a keyword argument
        assert call_args.kwargs.get('model') == "gemini-2.5-pro"

    def test_generate_script_uses_default_when_model_id_none(self):
        """[P1] [3.5-UNIT-001] generate_script() should use default when model_id is None.
        
        Fallback: Use DEFAULT_MODEL constant.
        """
        # Given: A GeminiAdapter
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = Mock()
            adapter.DEFAULT_MODEL = "gemini-2.5-flash-lite"
            
            # Mock the generate response
            mock_response = Mock()
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content = Mock()
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[0].text = "Generated script"
            adapter._genai_client.models.generate_content.return_value = mock_response
            
            # When: Calling generate_script without model_id
            result = adapter.generate_script(prompt="Test prompt")
        
        # Then: Should use DEFAULT_MODEL
        call_args = adapter._genai_client.models.generate_content.call_args
        assert "gemini-2.5-flash-lite" in str(call_args)

    def test_generate_script_falls_back_on_invalid_model_id(self):
        """[P1] [3.5-UNIT-001] generate_script() falls back to default for invalid model_id.
        
        AC: #3 - Falls back to default model with a warning.
        """
        # Given: A GeminiAdapter with validation returning False
        from eleven_video.api.gemini import GeminiAdapter
        
        with patch.object(GeminiAdapter, '__init__', lambda self, **kwargs: None):
            adapter = GeminiAdapter()
            adapter._genai_client = Mock()
            adapter.validate_text_model_id = Mock(return_value=False)  # Invalid
            adapter.DEFAULT_MODEL = "gemini-2.5-flash-lite"
            
            # Track warning callback
            warning_messages = []
            def warning_callback(msg):
                warning_messages.append(msg)
            
            # Mock the generate response
            mock_response = Mock()
            mock_response.candidates = [Mock()]
            mock_response.candidates[0].content = Mock()
            mock_response.candidates[0].content.parts = [Mock()]
            mock_response.candidates[0].content.parts[0].text = "Generated script"
            adapter._genai_client.models.generate_content.return_value = mock_response
            
            # When: Calling generate_script with invalid model_id
            result = adapter.generate_script(
                prompt="Test prompt",
                model_id="invalid-model",
                warning_callback=warning_callback
            )
        
        # Then: Should fall back to default and call warning
        assert len(warning_messages) == 1
        assert "invalid" in warning_messages[0].lower() or "fallback" in warning_messages[0].lower()
