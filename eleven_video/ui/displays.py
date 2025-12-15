"""
UI display components for terminal output.

Provides Rich-based display functions for API status tables and other UI elements.
"""
from typing import List, Dict, Any
from rich.table import Table
from rich.panel import Panel

from eleven_video.ui.console import console
from eleven_video.api.interfaces import HealthResult, UsageResult


def render_status_table(services: List[Dict[str, Any]]) -> None:
    """Render API status as a Rich table.
    
    Args:
        services: List of service status dictionaries with keys:
            - service_name: str
            - health: HealthResult
            - usage: UsageResult
    """
    table = Table(title="API Service Status", show_header=True, header_style="bold cyan")
    
    table.add_column("Service", style="bold")
    table.add_column("Status", justify="center")
    table.add_column("Latency", justify="right")
    table.add_column("Usage", justify="right")
    table.add_column("Message")
    
    for svc in services:
        service_name = svc["service_name"]
        health: HealthResult = svc["health"]
        usage: UsageResult = svc["usage"]
        
        # Status indicator
        if health.status == "ok":
            status_str = "[green]✓ OK[/green]"
        else:
            status_str = "[red]❌ Error[/red]"
        
        # Latency
        if health.latency_ms is not None:
            latency_str = f"{health.latency_ms:.0f}ms"
        else:
            latency_str = "-"
        
        # Usage
        if usage.available and usage.used is not None and usage.limit is not None:
            usage_str = f"{usage.used:,}/{usage.limit:,} {usage.unit or ''}"
        elif not usage.available:
            usage_str = "[dim]N/A[/dim]"
        else:
            usage_str = "-"
        
        # Message (truncate if too long)
        message = health.message[:50] if len(health.message) > 50 else health.message
        
        table.add_row(service_name, status_str, latency_str, usage_str, message)
    
    console.print(table)


def build_status_json(services: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build JSON-serializable status data.
    
    Args:
        services: List of service status dictionaries.
        
    Returns:
        Dictionary suitable for JSON serialization.
    """
    result = {"services": []}
    
    for svc in services:
        health: HealthResult = svc["health"]
        usage: UsageResult = svc["usage"]
        
        service_data = {
            "name": svc["service_name"],
            "status": health.status,
            "message": health.message,
            "latency_ms": health.latency_ms,
            "usage": {
                "available": usage.available,
                "used": usage.used,
                "limit": usage.limit,
                "unit": usage.unit,
            } if usage else None
        }
        result["services"].append(service_data)
    
    return result
