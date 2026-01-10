"""
Test fixtures for UI tests - Story 3.3.

Provides common fixtures for VoiceSelector testing.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Optional


# =============================================================================
# Factory Functions for Test Data
# =============================================================================

def create_voice_info(
    voice_id: str = "test-voice-id",
    name: str = "Test Voice",
    category: Optional[str] = "premade",
    preview_url: Optional[str] = None
):
    """Factory function for creating VoiceInfo test data.
    
    Uses pattern from data-factories.md knowledge base.
    """
    from eleven_video.models.domain import VoiceInfo
    return VoiceInfo(
        voice_id=voice_id,
        name=name,
        category=category,
        preview_url=preview_url
    )


def create_mock_voice_list(count: int = 3) -> List:
    """Create a list of mock VoiceInfo objects for testing."""
    from eleven_video.models.domain import VoiceInfo
    
    voices = []
    for i in range(count):
        voices.append(VoiceInfo(
            voice_id=f"voice-{i+1}",
            name=f"Voice {i+1}",
            category="premade",
            preview_url=None
        ))
    return voices


# =============================================================================
# Fixtures for VoiceSelector
# =============================================================================

@pytest.fixture
def mock_adapter():
    """Create a mock ElevenLabsAdapter for VoiceSelector testing."""
    return Mock()


@pytest.fixture
def voice_selector(mock_adapter):
    """Create a VoiceSelector instance with mock adapter."""
    from eleven_video.ui.voice_selector import VoiceSelector
    return VoiceSelector(mock_adapter)


@pytest.fixture
def sample_voices():
    """Return a standard list of 3 sample voices for testing."""
    from eleven_video.models.domain import VoiceInfo
    return [
        VoiceInfo(voice_id="voice-rachel", name="Rachel", category="premade"),
        VoiceInfo(voice_id="voice-domi", name="Domi", category="premade"),
        VoiceInfo(voice_id="voice-bella", name="Bella", category="premade"),
    ]


@pytest.fixture
def single_voice():
    """Return a single voice for minimal testing."""
    from eleven_video.models.domain import VoiceInfo
    return [VoiceInfo(voice_id="voice-1", name="Test Voice", category="premade")]


@pytest.fixture
def mock_console():
    """Patch console for testing without terminal output."""
    with patch("eleven_video.ui.voice_selector.console") as mock:
        mock.is_terminal = True
        yield mock


@pytest.fixture
def mock_prompt():
    """Patch Rich Prompt for testing user input."""
    with patch("eleven_video.ui.voice_selector.Prompt") as mock:
        yield mock


# =============================================================================
# Fixtures for ImageModelSelector (Story 3.4)
# =============================================================================

def create_image_model_info(
    model_id: str = "gemini-2.5-flash-image",
    name: str = "Gemini 2.5 Flash Image",
    description: Optional[str] = "Fast image generation",
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


def create_mock_image_model_list(count: int = 3) -> List:
    """Create a list of mock ImageModelInfo objects for testing."""
    from eleven_video.models.domain import ImageModelInfo
    
    models = []
    for i in range(count):
        models.append(ImageModelInfo(
            model_id=f"model-{i+1}",
            name=f"Model {i+1}",
            description=f"Description {i+1}",
            supports_image_generation=True
        ))
    return models


@pytest.fixture
def mock_gemini_adapter():
    """Create a mock GeminiAdapter for ImageModelSelector testing."""
    return Mock()


@pytest.fixture
def image_model_selector(mock_gemini_adapter):
    """Create an ImageModelSelector instance with mock adapter."""
    from eleven_video.ui.image_model_selector import ImageModelSelector
    return ImageModelSelector(mock_gemini_adapter)


@pytest.fixture
def sample_image_models():
    """Return a standard list of 3 sample image models for testing."""
    from eleven_video.models.domain import ImageModelInfo
    return [
        ImageModelInfo(model_id="gemini-2.5-flash-image", name="Gemini 2.5 Flash Image", description="Fast generation"),
        ImageModelInfo(model_id="gemini-3-flash", name="Gemini 3 Flash", description="Latest model"),
        ImageModelInfo(model_id="imagen-3.0-generate-001", name="Imagen 3", description="Highest quality"),
    ]


@pytest.fixture
def single_image_model():
    """Return a single image model for minimal testing."""
    from eleven_video.models.domain import ImageModelInfo
    return [ImageModelInfo(model_id="gemini-2.5-flash-image", name="Test Model", description="Test")]


@pytest.fixture
def mock_console_image():
    """Patch console for testing without terminal output (ImageModelSelector)."""
    with patch("eleven_video.ui.image_model_selector.console") as mock:
        mock.is_terminal = True
        yield mock


@pytest.fixture
def mock_prompt_image():
    """Patch Rich Prompt for testing user input (ImageModelSelector)."""
    with patch("eleven_video.ui.image_model_selector.Prompt") as mock:
        yield mock


# =============================================================================
# Fixtures for GeminiModelSelector (Story 3.5)
# =============================================================================

def create_gemini_model_info(
    model_id: str = "gemini-2.5-flash",
    name: str = "Gemini 2.5 Flash",
    description: Optional[str] = "Fast text generation",
    supports_text_generation: bool = True
):
    """Factory function for creating GeminiModelInfo test data.
    
    Uses pattern from data-factories.md knowledge base.
    """
    from eleven_video.models.domain import GeminiModelInfo
    return GeminiModelInfo(
        model_id=model_id,
        name=name,
        description=description,
        supports_text_generation=supports_text_generation
    )


def create_mock_gemini_model_list(count: int = 3) -> List:
    """Create a list of mock GeminiModelInfo objects for testing."""
    from eleven_video.models.domain import GeminiModelInfo
    
    models = []
    for i in range(count):
        models.append(GeminiModelInfo(
            model_id=f"gemini-model-{i+1}",
            name=f"Gemini Model {i+1}",
            description=f"Description {i+1}",
            supports_text_generation=True
        ))
    return models


@pytest.fixture
def gemini_model_selector(mock_gemini_adapter):
    """Create a GeminiModelSelector instance with mock adapter."""
    from eleven_video.ui.gemini_model_selector import GeminiModelSelector
    return GeminiModelSelector(mock_gemini_adapter)


@pytest.fixture
def sample_gemini_models():
    """Return a standard list of 3 sample Gemini models for testing."""
    from eleven_video.models.domain import GeminiModelInfo
    return [
        GeminiModelInfo(model_id="gemini-2.5-flash", name="Gemini 2.5 Flash", description="Fast generation"),
        GeminiModelInfo(model_id="gemini-2.5-flash-lite", name="Gemini 2.5 Flash Lite", description="Ultra-fast, efficient"),
        GeminiModelInfo(model_id="gemini-2.5-pro", name="Gemini 2.5 Pro", description="Highest quality"),
    ]


@pytest.fixture
def single_gemini_model():
    """Return a single Gemini model for minimal testing."""
    from eleven_video.models.domain import GeminiModelInfo
    return [GeminiModelInfo(model_id="gemini-2.5-flash", name="Test Model", description="Test")]


@pytest.fixture
def mock_console_gemini():
    """Patch console for testing without terminal output (GeminiModelSelector)."""
    with patch("eleven_video.ui.gemini_model_selector.console") as mock:
        mock.is_terminal = True
        yield mock


@pytest.fixture
def mock_prompt_gemini():
    """Patch Rich Prompt for testing user input (GeminiModelSelector)."""
    with patch("eleven_video.ui.gemini_model_selector.Prompt") as mock:
        yield mock


# =============================================================================
# Fixtures for DurationSelector (Story 3.6)
# =============================================================================

def create_duration_option(
    minutes: int = 3,
    label: str = "Standard",
    description: str = "~3 minutes (recommended)"
):
    """Factory function for creating DurationOption test data.
    
    Uses pattern from data-factories.md knowledge base.
    """
    from eleven_video.models.domain import DurationOption
    return DurationOption(minutes=minutes, label=label, description=description)


@pytest.fixture
def duration_selector():
    """Create a DurationSelector instance."""
    from eleven_video.ui.duration_selector import DurationSelector
    return DurationSelector()


@pytest.fixture
def sample_duration_options():
    """Return the standard DURATION_OPTIONS list for testing."""
    from eleven_video.models.domain import DURATION_OPTIONS
    return DURATION_OPTIONS


@pytest.fixture
def mock_console_duration():
    """Patch console for testing without terminal output (DurationSelector)."""
    with patch("eleven_video.ui.duration_selector.console") as mock:
        mock.is_terminal = True
        yield mock


@pytest.fixture
def mock_prompt_duration():
    """Patch Rich Prompt for testing user input (DurationSelector)."""
    with patch("eleven_video.ui.duration_selector.Prompt") as mock:
        yield mock
