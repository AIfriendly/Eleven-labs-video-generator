"""
Interactive Voice Selection UI Component - Story 3.3

Provides user-friendly voice selection via Rich terminal prompts.
Uses ElevenLabsAdapter.list_voices() from Story 3.1 to fetch voices.
"""
from typing import Optional, List, TYPE_CHECKING

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import VoiceInfo

if TYPE_CHECKING:
    from eleven_video.api.elevenlabs import ElevenLabsAdapter


class VoiceSelector:
    """Interactive voice selection UI component.
    
    Displays available voices and prompts user to select one.
    Falls back to default voice on errors or non-TTY environments.
    """
    
    DEFAULT_VOICE_NAME = "Adam Stone"
    
    def __init__(self, adapter: "ElevenLabsAdapter") -> None:
        """Initialize VoiceSelector with ElevenLabs adapter.
        
        Args:
            adapter: ElevenLabsAdapter instance for fetching voices
        """
        self._adapter = adapter
    
    def select_voice_interactive(self) -> Optional[str]:
        """Display voice list and prompt user for selection.
        
        Returns:
            Voice ID string, or None to use default voice.
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default voice.[/dim]")
            return None
        
        try:
            voices = self._adapter.list_voices(use_cache=True)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not fetch voice list: {e}[/yellow]")
            console.print("[dim]Using default voice...[/dim]")
            return None
        
        if not voices:
            console.print("[yellow]No voices available. Using default.[/yellow]")
            return None
        
        self._display_voice_list(voices)
        return self._get_user_selection(voices)
    
    def _display_voice_list(self, voices: List[VoiceInfo]) -> None:
        """Display numbered voice options.
        
        Args:
            voices: List of VoiceInfo objects to display
        """
        console.print(Panel(
            "[bold cyan]Available Voices[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="white")
        table.add_column("Category", style="dim")
        
        # Default option
        table.add_row("0", f"Default ({self.DEFAULT_VOICE_NAME})", "recommended")
        
        for i, voice in enumerate(voices, start=1):
            table.add_row(str(i), voice.name, voice.category or "")
        
        console.print(table)
    
    def _get_user_selection(self, voices: List[VoiceInfo]) -> Optional[str]:
        """Prompt user for voice selection and return voice_id.
        
        Args:
            voices: List of VoiceInfo objects to select from
            
        Returns:
            Selected voice_id, or None for default voice
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select a voice number[/bold cyan]",
            default="0"
        )
        
        try:
            index = int(choice)
            if index == 0:
                return None  # Use default
            if 1 <= index <= len(voices):
                return voices[index - 1].voice_id
            console.print("[yellow]Invalid selection. Using default.[/yellow]")
            return None
        except ValueError:
            console.print("[yellow]Invalid input. Using default.[/yellow]")
            return None
