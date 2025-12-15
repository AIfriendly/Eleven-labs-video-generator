"""
Singleton Console provider for consistent Rich terminal output.

This module provides a centralized Console instance to prevent
stream conflicts and ensure consistent theming across the application.
"""

from rich.console import Console

# Singleton Console instance
# Using module-level instantiation per Python singleton pattern
_console: Console = Console()


def get_console() -> Console:
    """
    Get the singleton Console instance.
    
    Returns:
        Console: The shared Rich Console instance.
    
    Example:
        >>> from eleven_video.ui.console import get_console
        >>> console = get_console()
        >>> console.print("[bold]Hello World[/bold]")
    """
    return _console


# Module-level export for direct access
console = _console
