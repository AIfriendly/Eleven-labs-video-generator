"""Quick test to see what the panel output looks like."""
from unittest.mock import MagicMock, patch
from eleven_video.ui.usage_panel import UsageDisplay
from rich.console import Console
from io import StringIO

mock = MagicMock()
mock.get_summary.return_value = {
    'total_cost': 0.75,
    'events_count': 15,
    'by_service': {
        'gemini': {
            'metrics': {'input_tokens': 2_000_000, 'output_tokens': 500_000},
            'cost': 0.50
        },
        'elevenlabs': {
            'metrics': {'characters': 5_000},
            'cost': 0.25
        }
    },
    'by_model': {
        'gemini-2.5-flash': {
            'metrics': {'input_tokens': 1_500_000, 'output_tokens': 400_000},
            'cost': 0.35
        }
    }
}

with patch('eleven_video.ui.usage_panel.UsageMonitor.get_instance', return_value=mock):
    display = UsageDisplay()
    panel = display.__rich__()
    
    # Render to string
    string_io = StringIO()
    console = Console(file=string_io, force_terminal=False, width=120)
    console.print(panel)
    panel_str = string_io.getvalue()
    
    print("Panel output:")
    print(panel_str)
    print("\n---\n")
    print("Checking for 'Gemini':", "Gemini" in panel_str)
    print("Checking for 'gemini':", "gemini" in panel_str)

