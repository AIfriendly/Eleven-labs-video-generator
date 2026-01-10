from typing import Optional
from rich.prompt import Prompt
from eleven_video.ui.console import console
from eleven_video.models.domain import Resolution


class ResolutionSelector:
    """Handling for video resolution selection (Story 3.8)."""

    def select_resolution(self, interactive: bool = True) -> Resolution:
        """Select a resolution interactively or fallback to default.
        
        Args:
            interactive: Whether to show interactive prompt.
            
        Returns:
            Selected Resolution enum member.
        """
        # Story 3.8 - AC6: Default to 1080p if no resolution specified (implicit here via fallback)
        default_resolution = Resolution.HD_1080P
        
        # Check if we should skip interaction (Story 3.8 - AC2 & AC3)
        if not interactive:
            return default_resolution
            
        # Non-TTY Fallback (Story 3.8 - Task 2)
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode. Using default resolution.[/dim]")
            return default_resolution
            
        console.print("[bold cyan]Select Video Resolution:[/bold cyan]")
        
        # Build choices from Enum labels
        # AC3: "1080p (Landscape)", "720p (Landscape)", "Portrait (9:16)", "Square (1:1)"
        choices = [res.value["label"] for res in Resolution]
        label_to_enum = {res.value["label"]: res for res in Resolution}
        
        default_label = default_resolution.value["label"]
        
        selection = Prompt.ask(
            "Choose resolution",
            choices=choices,
            default=default_label,
            console=console
        )
        
        return label_to_enum[selection]
