"""Custom exceptions for the eleven-video application."""


class ConfigurationError(Exception):
    """Raised when application configuration is invalid or missing required values.
    
    This exception is raised when:
    - Required API keys (ELEVENLABS_API_KEY, GEMINI_API_KEY) are missing or empty
    - Configuration files are malformed or inaccessible
    - Environment variables fail validation
    """

    def __init__(self, message: str = "Configuration error occurred"):
        self.message = message
        super().__init__(self.message)


class GeminiAPIError(Exception):
    """Error from Gemini API with user-friendly message.
    
    This exception is raised when:
    - API authentication fails (401)
    - Rate limits are exceeded (429)
    - Server errors occur (500, 503)
    - Network timeouts occur
    
    The error message is sanitized to never expose API keys.
    """

    def __init__(self, message: str = "Gemini API error occurred"):
        self.message = message
        super().__init__(self.message)


class ValidationError(Exception):
    """Input validation error.
    
    This exception is raised when:
    - Prompt is empty or whitespace-only
    - Prompt is None
    - Other input validation failures
    """

    def __init__(self, message: str = "Validation error occurred"):
        self.message = message
        super().__init__(self.message)


class ElevenLabsAPIError(Exception):
    """Error from ElevenLabs API with user-friendly message.
    
    This exception is raised when:
    - API authentication fails (401)
    - Rate limits are exceeded (429)
    - Server errors occur (500, 503)
    - Network timeouts occur
    
    The error message is sanitized to never expose API keys.
    """

    def __init__(self, message: str = "ElevenLabs API error occurred"):
        self.message = message
        super().__init__(self.message)

