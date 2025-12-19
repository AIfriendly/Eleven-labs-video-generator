"""
Interactive Image Model Selection UI Component - Story 3.4

Provides user-friendly image model selection via Rich terminal prompts.
Uses GeminiAdapter.list_image_models() from Story 3.2 to fetch models.
"""
from typing import Optional, List, TYPE_CHECKING

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from eleven_video.ui.console import console
from eleven_video.models.domain import ImageModelInfo

if TYPE_CHECKING:
    from eleven_video.api.gemini import GeminiAdapter


class ImageModelSelector:
    """Interactive image model selection UI component.
    
    Displays available image models and prompts user to select one.
    Falls back to default model on errors or non-TTY environments.
    """
    
    DEFAULT_MODEL_ID = "gemini-2.5-flash-image"
    DEFAULT_MODEL_NAME = "Gemini 2.5 Flash Image"
    
    def __init__(self, adapter: "GeminiAdapter") -> None:
        """Initialize ImageModelSelector with Gemini adapter.
        
        Args:
            adapter: GeminiAdapter instance for fetching models
        """
        self._adapter = adapter
    
    def select_model_interactive(self) -> Optional[str]:
        """Display image model list and prompt user for selection.
        
        Returns:
            Model ID string, or None to use default model.
        """
        # R-004 mitigation: Non-TTY fallback
        if not console.is_terminal:
            console.print("[dim]Non-interactive mode detected. Using default image model.[/dim]")
            return None
        
        try:
            models = self._adapter.list_image_models(use_cache=True)
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not fetch image model list: {e}[/yellow]")
            console.print("[dim]Using default image model...[/dim]")
            return None
        
        if not models:
            console.print("[yellow]No image models available. Using default.[/yellow]")
            return None
        
        self._display_model_list(models)
        return self._get_user_selection(models)
    
    def _display_model_list(self, models: List[ImageModelInfo]) -> None:
        """Display numbered image model options.
        
        Args:
            models: List of ImageModelInfo objects to display
        """
        console.print(Panel(
            "[bold cyan]Available Image Models[/bold cyan]",
            border_style="cyan"
        ))
        
        table = Table(show_header=False, box=None)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Name", style="white")
        table.add_column("Description", style="dim")
        
        # Default option
        table.add_row("0", f"Default ({self.DEFAULT_MODEL_NAME})", "recommended")
        
        for i, model in enumerate(models, start=1):
            table.add_row(str(i), model.name, model.description or "")
        
        console.print(table)
    
    def _get_user_selection(self, models: List[ImageModelInfo]) -> Optional[str]:
        """Prompt user for image model selection and return model_id.
        
        Args:
            models: List of ImageModelInfo objects to select from
            
        Returns:
            Selected model_id, or None for default model
        """
        choice = Prompt.ask(
            "\n[bold cyan]Select an image model number[/bold cyan]",
            default="0"
        )
        
        try:
            index = int(choice)
            if index == 0:
                return None  # Use default
            if 1 <= index <= len(models):
                return models[index - 1].model_id
            console.print("[yellow]Invalid selection. Using default.[/yellow]")
            return None
        except ValueError:
            console.print("[yellow]Invalid input. Using default.[/yellow]")
            return None
