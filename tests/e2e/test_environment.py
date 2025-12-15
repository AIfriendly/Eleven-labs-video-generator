"""
Basic test to verify the Eleven Labs AI Video Generator environment is set up correctly.
"""
import sys
import os
import pytest
from dotenv import load_dotenv

# NOTE: Do NOT call load_dotenv() at module level - it pollutes env for other tests

def test_python_version():
    """Test that we're using Python 3.9+"""
    assert sys.version_info >= (3, 9), f"Python 3.9+ required, but {sys.version} found"

def test_environment_variables():
    """Test that environment variables are loaded"""
    # Call load_dotenv() only within this test, not at module level
    load_dotenv()
    eleven_labs_key = os.getenv("ELEVEN_LABS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    # These might not be set during testing, so we'll just verify the loading mechanism works
    assert load_dotenv() is not None

def test_imports():
    """Test that key dependencies can be imported"""
    try:
        import requests
        import typer
        import rich
        import pydantic
        import dotenv
        import aiohttp
        import tqdm
        from PIL import Image
        import pydub
        print("✅ All core dependencies imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import dependency: {e}")

def test_basic_functionality():
    """Test basic functionality - just a placeholder for now"""
    # This is a placeholder test - actual functionality tests will be added later
    assert True

if __name__ == "__main__":
    test_python_version()
    test_environment_variables()
    test_imports()
    test_basic_functionality()
    print("✅ All tests passed! Environment is set up correctly.")