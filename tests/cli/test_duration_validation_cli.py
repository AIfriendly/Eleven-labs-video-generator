"""
Tests for CLI Duration Validation - Story 3.6 Fix
"""
import pytest
from typer.testing import CliRunner
from eleven_video.main import app

runner = CliRunner()

def test_generate_fails_with_invalid_duration():
    """[P0] [3.6-CLI-001] CLI should reject durations other than 3, 5, or 10."""
    result = runner.invoke(app, ["generate", "--duration", "7", "--prompt", "test"])
    assert result.exit_code == 1
    assert "Invalid duration: 7" in result.stdout
    assert "Must be 3, 5, or 10 minutes" in result.stdout

def test_generate_accepts_valid_duration():
    """[P0] [3.6-CLI-002] CLI should accept valid durations (3, 5, 10)."""
    # Using --help to avoid running actual pipeline, but passing validated args
    # Validation happens before help? No, usually Typer parses first.
    # Actually, running full pipeline is heavy. 
    # Let's check if validation happens before pipeline init.
    # We can mock VideoPipeline to make it fast.
    
    from unittest.mock import patch
    
    # Patching the re-exported class in the orchestrator package
    with patch("eleven_video.orchestrator.VideoPipeline") as mock_pipeline:
        mock_instance = mock_pipeline.return_value
        mock_instance.generate.return_value = None # Mock return
        
        result = runner.invoke(app, ["generate", "--duration", "5", "--prompt", "test"])
        
        # Should pass validation and try to run pipeline
        assert result.exit_code == 0
        assert mock_pipeline.called
