"""
Live Usage Display panel for real-time API usage monitoring.

Stories: 5.1 (base implementation), 5.3 (consumption breakdown), 5.5 (service-specific display)

Provides a Rich-compatible component that renders current usage
statistics and cost estimates during video generation.
"""
import threading
from typing import Optional

from rich.console import RenderableType
from rich.panel import Panel
from rich.live import Live
from rich.console import Console

from eleven_video.monitoring.usage import UsageMonitor



class UsageDisplay:
    """Live usage display panel for real-time API monitoring.
    
    Renders a Rich Panel with current usage statistics that can be
    embedded in a Live context or Layout. Supports threaded updates
    to avoid blocking the main thread (Risk R-002).
    
    Example:
        >>> display = UsageDisplay()
        >>> display.start_live_update()
        >>> # ... run video generation ...
        >>> display.stop_live_update()
    """
    
    def __init__(
        self,
        console: Optional[Console] = None,
        update_interval: float = 5.0
    ):
        """Initialize the usage display.
        
        Args:
            console: Optional Rich Console for rendering.
            update_interval: Seconds between live updates (default 5s per AC2).
        """
        self.console = console
        self.update_interval = update_interval
        self._live: Optional[Live] = None
        self._update_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def __rich__(self) -> RenderableType:
        """Render the usage panel for Rich (Story 5.3: Enhanced with consumption breakdown).
        
        Returns:
            A Rich Panel containing detailed consumption data.
        """
        monitor = UsageMonitor.get_instance()
        summary = monitor.get_summary()
        
        # Build content with detailed breakdown
        lines = [
            f"[bold]Total Cost:[/bold] ${summary.get('total_cost', 0.0):.2f}",
            "",
        ]
        
        # By Service breakdown
        by_service = summary.get("by_service", {})
        if by_service:
            lines.append("[bold]By Service:[/bold]")
            for service, data in by_service.items():
                metrics = data.get("metrics", {})
                cost = data.get("cost", 0.0)
                metrics_str = self._format_metrics(metrics)
                
                # Story 5.5: Differentiate service display
                # - Gemini: pay-per-use → show dollar cost
                # - ElevenLabs: subscription-based → show character credits only
                if service.lower() == "elevenlabs":
                    # Show character count only (subscription-based, no per-call cost)
                    char_count = metrics.get("characters", 0)
                    if char_count >= 1000:
                        lines.append(f"  {service.capitalize()}: {char_count:,} characters used")
                    else:
                        lines.append(f"  {service.capitalize()}: {char_count} characters used")
                else:
                    # Pay-per-use services (Gemini) → show dollar cost
                    lines.append(f"  {service.capitalize()}: ${cost:.4f} ({metrics_str})")
            lines.append("")
        
        # By Model breakdown
        by_model = summary.get("by_model", {})
        if by_model:
            lines.append("[bold]By Model:[/bold]")
            # Sort by cost descending for better visibility (Review Fix)
            sorted_models = sorted(
                by_model.items(), 
                key=lambda x: x[1].get("cost", 0.0), 
                reverse=True
            )
            for model_id, data in sorted_models:
                metrics = data.get("metrics", {})
                cost = data.get("cost", 0.0)
                metrics_str = self._format_metrics(metrics)
                
                # Story 5.5 Fix (M-003): Consistent display for ElevenLabs models
                # Check if this is an ElevenLabs voice model (has characters metric, no tokens)
                if "characters" in metrics and "input_tokens" not in metrics:
                    # ElevenLabs voice model → show character count only
                    char_count = metrics.get("characters", 0)
                    if char_count >= 1000:
                        lines.append(f"  {model_id}: {char_count:,} characters")
                    else:
                        lines.append(f"  {model_id}: {char_count} characters")
                else:
                    # Gemini models → show dollar cost
                    lines.append(f"  {model_id}: ${cost:.4f} ({metrics_str})")

        
        content = "\n".join(lines)
        return Panel(
            content,
            title="[bold blue]📊 Live Usage[/bold blue]",
            border_style="blue",
            padding=(0, 1)
        )
    
    def _format_metrics(self, metrics: dict[str, int]) -> str:
        """Format metrics dict into human-readable string (Story 5.3).
        
        Args:
            metrics: Dict of metric_type -> value.
            
        Returns:
            Formatted string with metrics.
        """
        parts = []
        if "input_tokens" in metrics:
            parts.append(f"{self._format_value('input_tokens', metrics['input_tokens'])} input tokens")
        if "output_tokens" in metrics:
            parts.append(f"{self._format_value('output_tokens', metrics['output_tokens'])} output tokens")
        if "characters" in metrics:
            parts.append(f"{self._format_value('characters', metrics['characters'])} characters")
        if "images" in metrics:
            parts.append(f"{metrics['images']} images")
        return ", ".join(parts) if parts else "no metrics"
    
    def _format_value(self, metric_type: str, value: int) -> str:
        """Format metric value for display.
        
        Args:
            metric_type: Type of metric (tokens, characters, etc.).
            value: Raw numeric value.
            
        Returns:
            Formatted string with appropriate suffix.
        """
        if "token" in metric_type.lower():
            if value >= 1_000_000:
                return f"{value / 1_000_000:.2f}M"
            elif value >= 1_000:
                return f"{value / 1_000:.1f}K"
            return str(value)
        elif "character" in metric_type.lower():
            if value >= 1_000:
                return f"{value / 1_000:.1f}K"
            return str(value)
        return str(value)
    
    def start_live_update(self, console: Optional[Console] = None) -> None:
        """Start threaded live updates of the usage display.
        
        Runs updates in a background thread to avoid blocking
        the main execution thread during video generation (Risk R-002).
        
        Args:
            console: Optional console to use for live display.
        """
        if self._update_thread is not None and self._update_thread.is_alive():
            return  # Already running
        
        self._stop_event.clear()
        effective_console = console or self.console or Console()
        
        def _update_loop():
            with Live(self, console=effective_console, refresh_per_second=1) as live:
                self._live = live
                while not self._stop_event.is_set():
                    live.update(self)
                    # Wait for stop or interval
                    self._stop_event.wait(self.update_interval)
        
        self._update_thread = threading.Thread(target=_update_loop, daemon=True)
        self._update_thread.start()
    
    def stop_live_update(self) -> None:
        """Stop the live update thread gracefully."""
        self._stop_event.set()
        if self._update_thread is not None:
            self._update_thread.join(timeout=2.0)
            self._update_thread = None
        self._live = None
    
    def render_once(self, console: Optional[Console] = None) -> None:
        """Render the usage panel once to console (no live updates).
        
        Useful for final summary display after generation completes.
        
        Args:
            console: Console to render to.
        """
        effective_console = console or self.console or Console()
        effective_console.print(self)
