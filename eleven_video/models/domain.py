"""Domain models for the eleven-video application."""
from dataclasses import dataclass


@dataclass
class Script:
    """Generated video script from Gemini API.
    
    Attributes:
        content: The raw text content of the generated script.
    """
    content: str
