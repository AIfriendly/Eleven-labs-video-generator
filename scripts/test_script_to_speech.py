"""
End-to-End Test: Story 2.1 → Story 2.2 Pipeline

Generates a script from a prompt using Gemini (Story 2.1),
then converts it to voiceover using ElevenLabs (Story 2.2).

Usage:
    uv run python scripts/test_script_to_speech.py

Requirements:
    - GOOGLE_API_KEY in environment or .env
    - ELEVENLABS_API_KEY in environment or .env
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def main():
    """Run the end-to-end script-to-speech test."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]Story 2.1 → 2.2 End-to-End Test[/bold cyan]\n"
        "Generate script with Gemini, then convert to voiceover with ElevenLabs",
        border_style="cyan"
    ))
    
    # Check for API keys
    gemini_key = os.environ.get("GEMINI_API_KEY")
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if not gemini_key:
        console.print("[red]❌ GEMINI_API_KEY not found in environment[/red]")
        return 1
    if not elevenlabs_key:
        console.print("[red]❌ ELEVENLABS_API_KEY not found in environment[/red]")
        return 1
    
    console.print("[green]✓ API keys found[/green]\n")
    
    # Get prompt from user
    console.print("[bold]Enter a topic for your video script:[/bold]")
    prompt = console.input("[cyan]> [/cyan]")
    
    if not prompt.strip():
        prompt = "A 30-second educational video about the wonders of space exploration"
        console.print(f"[dim]Using default: {prompt}[/dim]")
    
    console.print()
    
    # Step 1: Generate script with Gemini
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating script with Gemini...", total=None)
        
        try:
            from eleven_video.api.gemini import GeminiAdapter
            
            gemini = GeminiAdapter(api_key=gemini_key)
            script = gemini.generate_script(prompt)
            
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ Script generation failed: {e}[/red]")
            return 1
    
    console.print()
    console.print(Panel(
        script.content,
        title="[bold green]Generated Script[/bold green]",
        border_style="green"
    ))
    console.print(f"[dim]Script length: {len(script.content)} characters[/dim]\n")
    
    # Confirm before TTS (costs money)
    console.print("[yellow]⚠️  Converting to audio will use ElevenLabs credits.[/yellow]")
    proceed = console.input("[bold]Proceed with TTS? (y/n): [/bold]")
    
    if proceed.lower() != 'y':
        console.print("[dim]Cancelled.[/dim]")
        return 0
    
    console.print()
    
    # Step 2: Convert to speech with ElevenLabs
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating voiceover with ElevenLabs...", total=None)
        
        try:
            from eleven_video.api.elevenlabs import ElevenLabsAdapter
            
            elevenlabs = ElevenLabsAdapter(api_key=elevenlabs_key)
            audio = elevenlabs.generate_speech(
                text=script.content,
                voice_id="NFG5qt843uXKj4pFvR7C",  # Adam Stone - late night radio
                progress_callback=lambda msg: progress.update(task, description=f"[cyan]{msg}")
            )
            
            progress.update(task, completed=True)
        except Exception as e:
            console.print(f"[red]❌ TTS generation failed: {e}[/red]")
            return 1
    
    # Save the audio file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = output_dir / f"voiceover_{timestamp}.mp3"
    
    with open(audio_path, "wb") as f:
        f.write(audio.data)
    
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅ Success![/bold green]\n\n"
        f"[bold]Audio saved to:[/bold] {audio_path}\n"
        f"[bold]File size:[/bold] {audio.file_size_bytes:,} bytes\n"
        f"[bold]Duration:[/bold] {audio.duration_seconds or 'N/A'} seconds",
        border_style="green"
    ))
    
    # Also save the script
    script_path = output_dir / f"script_{timestamp}.txt"
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script.content)
    console.print(f"[dim]Script saved to: {script_path}[/dim]")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
