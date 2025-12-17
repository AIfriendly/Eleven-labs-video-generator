"""
Tests for successful image generation (Story 2.3).

Test IDs: 2.3-UNIT-001 to 2.3-UNIT-004, 2.3-UNIT-016 to 2.3-UNIT-018
Tests cover AC1 (image generation), AC6 (domain models), AC7 (multi-segment).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestImageGenerationSuccess:
    """Tests for successful image generation (AC1, AC6, AC7)."""

    def test_generate_images_returns_list_of_images(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-001] AC1: Valid script generates images.
        
        GIVEN a valid Script domain model
        WHEN generate_images() is called
        THEN a list of Image domain models is returned.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="A beautiful sunrise over mountains.")
        
        images = adapter.generate_images(script)
        
        assert isinstance(images, list)
        assert len(images) > 0
        assert all(isinstance(img, Image) for img in images)

    def test_generate_images_uses_nano_banana_model(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-002] AC1: Uses image generation model.
        
        GIVEN a valid script
        WHEN generating images
        THEN the image generation model (gemini-2.5-flash-image) is used.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Ocean waves crashing on rocks.")
        
        adapter.generate_images(script)
        
        # Verify model parameter - uses gemini-2.5-flash-image for image generation
        call_args = mock_client.models.generate_content.call_args
        assert call_args is not None
        assert "gemini-2.5-flash-image" in str(call_args)

    def test_generate_images_extracts_image_bytes(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-003] AC1: Extracts bytes from inline_data.
        
        GIVEN an API response with inline_data
        WHEN parsing the response
        THEN image bytes are correctly extracted.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Golden sunset.")
        
        images = adapter.generate_images(script)
        
        assert images[0].data == b"fake_png_bytes"

    def test_generate_images_appends_style_suffix(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-004] AC1: Prompts have style suffix.
        
        GIVEN a script segment
        WHEN generating image prompt
        THEN the style suffix is appended.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Mountain landscape")
        
        adapter.generate_images(script)
        
        call_args = mock_client.models.generate_content.call_args
        prompt_used = str(call_args)
        
        assert "photorealistic" in prompt_used.lower() or "cinematic" in prompt_used.lower()

    def test_images_returned_as_domain_models(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-016] AC6: Returns List[Image] domain models.
        
        GIVEN successful image generation
        WHEN images are returned
        THEN they are Image domain model instances with correct types.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="Test content")
        
        images = adapter.generate_images(script)
        
        for image in images:
            assert isinstance(image, Image)
            assert isinstance(image.data, bytes)
            assert isinstance(image.mime_type, str)

    def test_multi_paragraph_generates_multiple_images(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-017] AC7: Multiple paragraphs generate multiple images.
        
        GIVEN a script with 3 paragraphs
        WHEN generating images
        THEN 3 images are generated (one per paragraph).
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="""Paragraph one about mountains.

Paragraph two about oceans.

Paragraph three about forests.""")
        
        images = adapter.generate_images(script)
        
        # Should generate one image per major paragraph
        assert len(images) == 3

    def test_single_sentence_generates_one_image(self, mock_genai_new_sdk_image):
        """
        [2.3-UNIT-018] AC7: Single sentence generates one image.
        
        GIVEN a script with a single sentence
        WHEN generating images
        THEN exactly one image is generated.
        """
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script
        
        mock_client_cls, mock_client, mock_response = mock_genai_new_sdk_image
        
        adapter = GeminiAdapter(api_key="test-key")
        script = Script(content="A single short sentence.")
        
        images = adapter.generate_images(script)
        
        assert len(images) == 1
