"""
Interactive Video Duration Selection UI Component - Story 3.6

Provides user-friendly duration selection via Rich terminal prompts.
Uses predefined DurationOption presets for consistency.
"""
from typing import Optional

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import DURATION_OPTIONS, DEFAULT_DURATION_MINUTES


class DurationSelector:
    """Interactive video duration selection UI component.
    
    Displays available duration options and prompts user to select one.
    Falls back to default duration on errors or non-TTY environments.
    """
    
    def __init__(self) -> None:
        """Initialize DurationSelector with predefined options."""
        self._options = DURATION_OPTIONS
    
    def select_duration_interactive(self) -> Optional[int]:
        """Display duration options and prompt user for selection.
        
        Returns:
            Duration in minutes, or None to use default (3 minutes).
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default duration.[/dim]")
            return None
        
        try:
            self._display_duration_options()
            return self._get_user_selection()
        except Exception:
            console.print("[yellow]Error in duration selection. Using default.[/yellow]")
            return None
    
    def _display_duration_options(self) -> None:
        """Display numbered duration options."""
        console.print(Panel(
            "[bold cyan]Select Video Duration[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Duration", style="white")
        table.add_column("Description", style="dim")
        
        # Default option
        table.add_row("0", f"Default ({DEFAULT_DURATION_MINUTES} min)", "recommended")
        
        for i, option in enumerate(self._options, start=1):
            table.add_row(str(i), f"{option.minutes} min ({option.label})", option.description)
        
        console.print(table)
    
    def _get_user_selection(self) -> Optional[int]:
        """Prompt user for duration selection and return minutes.
        
        Returns:
            Duration in minutes, or None for default
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select a duration number[/bold cyan]",
            default="0"
        )
        
        try:
            index = int(choice)
            if index == 0:
                return None  # Use default
            if 1 <= index <= len(self._options):
                return self._options[index - 1].minutes
            console.print("[yellow]Invalid selection. Using default.[/yellow]")
            return None
        except ValueError:
            console.print("[yellow]Invalid input. Using default.[/yellow]")
            return None
