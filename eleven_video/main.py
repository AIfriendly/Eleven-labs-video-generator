import typer
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import asyncio
import json

from pathlib import Path
from typing import Optional
from eleven_video import __version__
from eleven_video.config.persistence import (
    load_config, save_config, get_config_path,
    create_profile, list_profiles, get_active_profile, 
    switch_profile, delete_profile
)
from eleven_video.config import Settings
from eleven_video.api.elevenlabs import ElevenLabsAdapter
from eleven_video.api.gemini import GeminiAdapter
from eleven_video.ui.console import console
from eleven_video.ui.displays import render_status_table, build_status_json
from eleven_video.exceptions import ConfigurationError

app = typer.Typer(
    help="Eleven Labs AI Video Generator CLI",
    no_args_is_help=True,
    rich_markup_mode="rich"
)

# Profile subapp for managing API key profiles
profile_app = typer.Typer(
    name="profile",
    help="Manage API key profiles for different environments",
    no_args_is_help=True
)
app.add_typer(profile_app, name="profile")

# Global state for profile override
_profile_override_state: dict[str, Optional[str]] = {"profile": None}

def version_callback(value: bool):
    if value:
        console.print(f"Eleven Labs AI Video Generator Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Text prompt to generate video from"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice ID to use"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="Eleven Labs API Key"),
    gemini_key: Optional[str] = typer.Option(None, "--gemini-key", "-g", help="Gemini API Key"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    profile: Optional[str] = typer.Option(None, "--profile", help="Use a specific profile for this command only"),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show the version and exit"
    ),
):
    """
    Eleven Labs AI Video Generator
    """
    # Store profile override in global state for other commands to use
    if profile:
        _profile_override_state["profile"] = profile

@app.command()
def setup():
    """
    Interactive setup wizard to configure default settings.
    
    Guides you through configuration options and saves preferences
    to a JSON file in your OS-standard config directory.
    """
    console.print(Panel.fit(
        "[bold cyan]Eleven Video Setup Wizard[/bold cyan]\n"
        "Configure your default settings",
        border_style="cyan"
    ))
    
    # Security warning about API keys (AC5)
    console.print()
    console.print(Panel(
        "[yellow]⚠️  Security Notice[/yellow]\n\n"
        "API keys are [bold]NOT[/bold] stored in this configuration file.\n"
        "Please set your API keys via environment variables or .env file:\n\n"
        "  • ELEVENLABS_API_KEY=your_key_here\n"
        "  • GEMINI_API_KEY=your_key_here\n\n"
        "See Story 1.2 for API key configuration.",
        border_style="yellow",
        title="API Key Security"
    ))
    console.print()
    
    # Load existing configuration (AC3)
    existing_config = load_config()
    
    # Prompt for configuration options
    console.print("[bold]Configure Default Settings[/bold]\n")
    
    # Default voice setting
    current_voice = existing_config.get("default_voice", "")
    default_voice_prompt = f" [{current_voice}]" if current_voice else ""
    default_voice = Prompt.ask(
        f"Default voice ID{default_voice_prompt}",
        default=current_voice if current_voice else None
    )
    
    # Default output format
    current_format = existing_config.get("output_format", "mp4")
    output_format = Prompt.ask(
        f"Default output format",
        default=current_format,
        choices=["mp4", "mov", "avi", "webm"]
    )
    
    # Default video duration
    current_duration = existing_config.get("default_duration", 30)
    duration_str = Prompt.ask(
        f"Default video duration (seconds)",
        default=str(current_duration)
    )
    try:
        default_duration = int(duration_str)
    except ValueError:
        default_duration = 30
    
    # Build new config
    new_config = {
        "default_voice": default_voice or "",
        "output_format": output_format,
        "default_duration": default_duration,
    }
    
    # Save configuration (AC4)
    save_config(new_config)
    config_path = get_config_path()
    
    console.print()
    console.print(Panel.fit(
        f"[green]✓ Configuration saved![/green]\n"
        f"Location: [dim]{config_path}[/dim]",
        border_style="green"
    ))


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format for scripting")
):
    """
    Check API connectivity status and usage quotas.
    
    Verifies your API keys are working and shows remaining quota
    for ElevenLabs (characters) and Google Gemini (connectivity only).
    """
    # Load settings to get API keys (use profile override if set via --profile)
    try:
        profile_override = _profile_override_state.get("profile")
        settings = Settings(_profile_override=profile_override)
    except ConfigurationError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        raise typer.Exit(1)
    
    # Get API keys
    elevenlabs_key = settings.elevenlabs_api_key.get_secret_value()
    gemini_key = settings.gemini_api_key.get_secret_value()
    
    # Create adapters
    adapters = []
    if elevenlabs_key:
        adapters.append(ElevenLabsAdapter(api_key=elevenlabs_key))
    if gemini_key:
        adapters.append(GeminiAdapter(api_key=gemini_key))
    
    if not adapters:
        console.print("[yellow]No API keys configured.[/yellow]")
        console.print("Run [bold]eleven-video setup[/bold] or set environment variables.")
        raise typer.Exit(1)
    
    # Check services in parallel using asyncio.gather()
    async def check_single_service(adapter):
        """Check a single service and return result dict."""
        health = await adapter.check_health()
        usage = await adapter.get_usage()
        await adapter.close()
        return {
            "service_name": adapter.service_name,
            "health": health,
            "usage": usage
        }

    async def check_all_services():
        # Run all service checks in parallel
        return await asyncio.gather(*[check_single_service(a) for a in adapters])
    
    # Run async checks
    services = asyncio.run(check_all_services())
    
    # Output results
    if json_output:
        output_data = build_status_json(services)
        print(json.dumps(output_data, indent=2))
    else:
        render_status_table(services)


# =============================================================================
# Profile Management Commands (Story 1.6)
# =============================================================================

@profile_app.command("create")
def profile_create_cmd(
    name: str = typer.Argument(..., help="Profile name (e.g., 'dev', 'prod')"),
    env_file: Path = typer.Option(..., "--env-file", "-e", help="Path to the .env file")
):
    """
    Create a new profile pointing to a .env file.
    
    Example: eleven-video profile create dev --env-file .env.dev
    """
    try:
        create_profile(name, str(env_file))
        console.print(f"[green]✓ Profile '{name}' created successfully![/green]")
        console.print(f"  Environment file: [dim]{env_file.resolve()}[/dim]")
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@profile_app.command("list")
def profile_list_cmd():
    """
    List all profiles and show which is active.
    """
    profiles = list_profiles()
    active = get_active_profile()
    
    if not profiles:
        console.print("[yellow]No profiles configured.[/yellow]")
        console.print("Use [bold]eleven-video profile create[/bold] to add a profile.")
        return
    
    table = Table(title="API Key Profiles")
    table.add_column("Active", justify="center", style="green")
    table.add_column("Name", style="cyan")
    table.add_column("Environment File", style="dim")
    
    for name, env_path in profiles.items():
        is_active = "✓" if name == active else ""
        table.add_row(is_active, name, env_path)
    
    console.print(table)


@profile_app.command("switch")
def profile_switch_cmd(
    name: str = typer.Argument(..., help="Profile name to switch to")
):
    """
    Switch the active profile.
    
    Example: eleven-video profile switch prod
    """
    try:
        switch_profile(name)
        console.print(f"[green]✓ Switched to profile '{name}'[/green]")
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@profile_app.command("delete")
def profile_delete_cmd(
    name: str = typer.Argument(..., help="Profile name to delete")
):
    """
    Delete a profile.
    
    Note: Cannot delete the currently active profile.
    """
    try:
        delete_profile(name)
        console.print(f"[green]✓ Profile '{name}' deleted successfully![/green]")
    except ConfigurationError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def generate(
    prompt: Optional[str] = typer.Option(None, "--prompt", "-p", help="Text prompt to generate video from"),
    voice: Optional[str] = typer.Option(None, "--voice", "-v", help="Voice ID to use"),
    image_model: Optional[str] = typer.Option(None, "--image-model", "-m", help="Image model ID to use"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
):
    """
    Generate an AI video from a prompt.

    Orchestrates the full pipeline:
    1. Generates a script from your prompt (Gemini).
    2. Converts script to audio (ElevenLabs).
    3. Generates visuals for each scene (Gemini).
    4. Compiles everything into a final video (FFmpeg).
    """
    from eleven_video.orchestrator import VideoPipeline

    # Interactive prompt if not provided
    if not prompt:
        console.print(Panel.fit(
            "[bold cyan]Eleven Video Generator[/bold cyan]\n"
            "Generate a video from a text topic.",
            border_style="cyan"
        ))
        prompt = Prompt.ask("[bold green]Enter your video topic/prompt[/bold green]")
    
    # Load settings (respecting profile override)
    try:
        profile_override = _profile_override_state.get("profile")
        settings = Settings(_profile_override=profile_override)
    except ConfigurationError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        raise typer.Exit(1)

    # Interactive voice selection if --voice not provided (Story 3.3)
    if voice is None:
        from eleven_video.ui.voice_selector import VoiceSelector
        adapter = ElevenLabsAdapter(settings=settings)
        try:
            selector = VoiceSelector(adapter)
            voice = selector.select_voice_interactive()
        except Exception as e:
            console.print(f"[yellow]⚠️ Voice selection unavailable: {e}[/yellow]")
            console.print("[dim]Continuing with default voice...[/dim]")
            voice = None  # Graceful degradation
        finally:
            asyncio.run(adapter.close())

    # Interactive image model selection if --image-model not provided (Story 3.4)
    if image_model is None:
        from eleven_video.ui.image_model_selector import ImageModelSelector
        gemini_adapter = GeminiAdapter(settings=settings)
        try:
            selector = ImageModelSelector(gemini_adapter)
            image_model = selector.select_model_interactive()
        except Exception as e:
            console.print(f"[yellow]⚠️ Image model selection unavailable: {e}[/yellow]")
            console.print("[dim]Continuing with default image model...[/dim]")
            image_model = None  # Graceful degradation
        finally:
            asyncio.run(gemini_adapter.close())

    # Initialize pipeline
    pipeline = VideoPipeline(
        settings=settings, 
        output_dir=output.parent if output else None
    )

    try:
        console.print(f"\n[dim]Initializing pipeline for topic:[/dim] [bold]{prompt}[/bold]\n")
        
        # Run generation (pass image_model_id - Story 3.4)
        video = pipeline.generate(prompt=prompt, voice_id=voice, image_model_id=image_model)
        
        # Success handled by pipeline.show_summary()
        
    except Exception as e:
        console.print(f"\n[red]❌ Generation Failed:[/red] {e}")
        # Debug info
        # console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()