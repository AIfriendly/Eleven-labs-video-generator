"""
Tests for Image domain model (Story 2.3).

Test IDs: 2.3-UNIT-015a, 2.3-UNIT-015
Tests verify the Image domain model exists and has required metadata fields.
"""
import pytest


class TestImageDomainModel:
    """Tests for Image domain model existence (AC6)."""

    def test_image_model_exists(self):
        """
        [2.3-UNIT-015a] Image domain model exists.
        
        GIVEN the models.domain module
        WHEN importing Image
        THEN the class should exist.
        """
        from eleven_video.models.domain import Image
        
        assert Image is not None

    def test_image_model_has_required_metadata(self):
        """
        [2.3-UNIT-015] AC6: Image has required metadata fields.
        
        GIVEN an Image instance
        WHEN accessing metadata
        THEN it should have data, mime_type, and file_size_bytes attributes.
        """
        from eleven_video.models.domain import Image
        
        image = Image(
            data=b"fake_png_bytes",
            mime_type="image/png",
            file_size_bytes=14
        )
        
        assert hasattr(image, 'data')
        assert hasattr(image, 'mime_type')
        assert hasattr(image, 'file_size_bytes')
        assert image.data == b"fake_png_bytes"
        assert image.mime_type == "image/png"
        assert image.file_size_bytes == 14
