"""
Integration tests for real Gemini API - Image Generation (Story 2.3).

Test ID: 2.3-INT-001
Run manually with: uv run pytest tests/api/gemini/test_image_gen_integration.py -m integration -v
"""
import os
import pytest


@pytest.mark.integration
class TestImageGenerationIntegration:
    """Integration tests for real Gemini API - skip in CI."""

    @pytest.mark.skipif(
        not os.environ.get("GEMINI_API_KEY"),
        reason="GEMINI_API_KEY not set"
    )
    def test_real_api_generates_images(self):
        """
        [2.3-INT-001] Integration: Real API generates images.
        
        GIVEN a valid GEMINI_API_KEY in environment
        WHEN generate_images is called with a real script
        THEN images are returned from the actual API.
        
        Note: Uses retry logic for rate-limit resilience.
        """
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        from eleven_video.api.gemini import GeminiAdapter
        from eleven_video.models.domain import Script, Image
        from eleven_video.exceptions.custom_errors import GeminiAPIError
        
        api_key = os.environ.get("GEMINI_API_KEY")
        adapter = GeminiAdapter(api_key=api_key)
        script = Script(content="A beautiful mountain landscape at sunset.")
        
        # Retry on rate-limit errors
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=30),
            retry=retry_if_exception_type(GeminiAPIError),
            reraise=True
        )
        def generate_with_retry():
            return adapter.generate_images(script)
        
        try:
            images = generate_with_retry()
            assert len(images) >= 1
            assert all(isinstance(img, Image) for img in images)
            assert all(len(img.data) > 0 for img in images)
        except GeminiAPIError as e:
            if "rate limit" in str(e).lower():
                pytest.skip("Rate limit hit after retries - skipping integration test")
            raise
