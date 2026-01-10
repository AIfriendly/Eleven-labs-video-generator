"""
Quota display component for Rich terminal UI.

Displays API quota information in a styled table (Story 5.4).
"""
from typing import List, Optional
from rich.console import Console, ConsoleOptions, RenderResult
from rich.table import Table
from rich.text import Text

from eleven_video.models.quota import QuotaInfo


class QuotaDisplay:
    """Rich-compatible quota display component (Story 5.4 - AC #3).
    
    Renders API quota information as a styled Rich table with
    color-coded usage indicators:
    - Green: < 80% usage
    - Yellow: >= 80% usage 
    - Red: >= 90% usage or exhausted
    """
    
    def __init__(self, quotas: List[QuotaInfo]):
        """Initialize the quota display.
        
        Args:
            quotas: List of QuotaInfo objects to display.
        """
        self.quotas = quotas
    
    def get_usage_color(self, quota: QuotaInfo) -> str:
        """Determine the color for usage percentage (AC #3).
        
        Args:
            quota: The quota info to evaluate.
            
        Returns:
            Color name: "green", "yellow", or "red".
        """
        if not quota.is_available:
            return "dim"
            
        percent = quota.percent_used
        if percent is None:
            return "dim"
        
        if percent >= 90:
            return "red"
        elif percent >= 80:
            return "yellow"
        else:
            return "green"
    
    def _format_usage(self, quota: QuotaInfo) -> Text:
        """Format usage display with appropriate styling.
        
        Args:
            quota: The quota info to format.
            
        Returns:
            Styled Rich Text object.
        """
        if not quota.is_available:
            return Text("Unavailable", style="dim italic")
        
        usage_str = f"{quota.used} / {quota.limit} {quota.unit}"
        color = self.get_usage_color(quota)
        return Text(usage_str, style=color)
    
    def _format_percent(self, quota: QuotaInfo) -> Text:
        """Format percentage display with color coding.
        
        Args:
            quota: The quota info to format.
            
        Returns:
            Styled Rich Text object.
        """
        percent = quota.percent_used
        if percent is None:
            return Text("—", style="dim")
        
        color = self.get_usage_color(quota)
        return Text(f"{percent:.1f}%", style=color)
    
    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        """Render the quota display as a Rich table.
        
        Args:
            console: The Rich console.
            options: Console rendering options.
            
        Yields:
            RenderResult for the quota table.
        """
        table = Table(
            title="API Quota Status",
            title_style="bold cyan",
            show_header=True,
            header_style="bold",
            border_style="dim",
        )
        
        table.add_column("Service", style="bold")
        table.add_column("Current / Limit", justify="right")
        table.add_column("Usage %", justify="right")
        
        for quota in self.quotas:
            table.add_row(
                quota.service,
                self._format_usage(quota),
                self._format_percent(quota),
            )
        
        yield table
