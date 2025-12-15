"""
Pytest configuration and shared fixtures.

API fixtures are available in tests/fixtures/api_fixtures.py.
Import them directly in test files when needed:

    from tests.fixtures.api_fixtures import mock_elevenlabs_tts

Or use the fixtures module:

    from tests.fixtures import mock_all_apis
"""
from dotenv import load_dotenv

# Load .env file at test collection time so integration tests can access API keys
load_dotenv()

# Note: pytest_plugins cannot be used here because 'tests' is not a package
# that's installed in the Python path during test collection.
# Import fixtures directly in test files that need them.

