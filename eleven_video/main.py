import typer
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
import asyncio
import json
import os


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
    Run interactive setup wizard.
    
    Configures API keys (saved to .env) and default preferences
    (saved to config.json in user config dir).
    """
    console.print(Panel.fit("Eleven Video Setup", style="bold blue"))
    
    # Show config location immediately (Fixes Review Issue #3)
    config_dir = get_config_path().parent
    console.print(f"[dim]Configuration will be saved to: {config_dir}[/dim]\n")

    # Check for existing .env
    if os.path.exists(".env"):
        console.print(Panel(
            "[yellow]⚠️  Existing .env file detected.[/yellow]\n\n"
            "This setup wizard will [bold]NOT[/bold] modify your .env file.\n"
            "Please ensure your API keys are correctly set in your .env file or environment variables.",
            border_style="yellow",
            title=".env Detected"
        ))
        console.print()

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
    console.print("[bold]Configure Default Preferences[/bold]\n")
    
    # 1. Default voice ID (Story 3.7)
    current_voice = existing_config.get("default_voice", "")
    display_voice = current_voice if current_voice else "none"
    default_voice = Prompt.ask(
        f"Default voice ID [{display_voice}]",
        default=current_voice if current_voice else ""
    )
    
    # 2. Default image model (Story 3.7)
    current_image_model = existing_config.get("default_image_model", "")
    display_image_model = current_image_model if current_image_model else "gemini-2.0-flash-preview-image-generation"
    default_image_model = Prompt.ask(
        f"Default image model [{display_image_model}]",
        default=current_image_model if current_image_model else "gemini-2.0-flash-preview-image-generation"
    )
    
    # 3. Default Gemini text model (Story 3.7)
    current_gemini_model = existing_config.get("default_gemini_model", "")
    display_gemini_model = current_gemini_model if current_gemini_model else "gemini-2.5-flash"
    default_gemini_model = Prompt.ask(
        f"Default Gemini model [{display_gemini_model}]",
        default=current_gemini_model if current_gemini_model else "gemini-2.5-flash"
    )
    
    # 4. Default duration in minutes (Story 3.7 - updated from seconds)
    current_duration_minutes = existing_config.get("default_duration_minutes", 5)
    duration_str = Prompt.ask(
        f"Default video duration in minutes (3, 5, or 10) [{current_duration_minutes}]",
        default=str(current_duration_minutes),
        choices=["3", "5", "10"]
    )
    default_duration_minutes = int(duration_str)
    
    # 5. Default output format (existing)
    current_format = existing_config.get("output_format", "mp4")
    output_format = Prompt.ask(
        f"Default output format",
        default=current_format,
        choices=["mp4", "mov", "avi", "webm"]
    )
    
    # Build new config with all Story 3.7 fields
    new_config = {
        "default_voice": default_voice or "",
        "default_image_model": default_image_model,
        "default_gemini_model": default_gemini_model,
        "default_duration_minutes": default_duration_minutes,
        "output_format": output_format,
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
        # Story 5.4: Also fetch quota info
        quota = await adapter.get_quota_info()
        await adapter.close()
        return {
            "service_name": adapter.service_name,
            "health": health,
            "usage": usage,
            "quota": quota
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
        
        # Story 5.4: Display quota information using QuotaDisplay
        from eleven_video.ui.quota_display import QuotaDisplay
        quotas = [svc["quota"] for svc in services if svc.get("quota")]
        if quotas:
            console.print()  # Add spacing
            quota_display = QuotaDisplay(quotas)
            console.print(quota_display)


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
    gemini_model: Optional[str] = typer.Option(None, "--gemini-model", help="Gemini text model ID to use (no short option due to -g conflict)"),
    duration: Optional[int] = typer.Option(None, "--duration", "-d", help="Target video duration in minutes"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    resolution: Optional[str] = typer.Option(None, "--resolution", "-r", help="Output resolution (1080p, 720p, portrait, square)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Force all interactive prompts even with defaults configured"),
):
    """
    Generate an AI video from a prompt.

    Orchestrates the full pipeline:
    1. Generates a script from your prompt (Gemini).
    2. Converts script to audio (ElevenLabs).
    3. Generates visuals for each scene (Gemini).
    4. Compiles everything into a final video (FFmpeg).
    
    Use --interactive / -i to force interactive prompts even when defaults are configured.
    """
    from eleven_video.orchestrator import VideoPipeline

    # VALIDATION (Story 3.6 - Task 6.2)
    if duration is not None and duration not in [3, 5, 10]:
        console.print(f"[red]Invalid duration: {duration}. Must be 3, 5, or 10 minutes.[/red]")
        raise typer.Exit(1)

    # Story 3.7: Load config defaults for priority hierarchy
    config = load_config()
    default_voice = config.get("default_voice")
    default_image_model = config.get("default_image_model")
    default_gemini_model = config.get("default_gemini_model")
    default_duration_minutes = config.get("default_duration_minutes")
    
    # Treat empty strings as None (not configured)
    if default_voice and not default_voice.strip():
        default_voice = None
    if default_image_model and not default_image_model.strip():
        default_image_model = None
    if default_gemini_model and not default_gemini_model.strip():
        default_gemini_model = None
    
    # Check if we're in a TTY (can show interactive prompts)
    is_tty = console.is_terminal
    
    # Story 3.7: Apply priority hierarchy
    # Priority: CLI flags > config defaults > interactive prompts
    # If -i flag is set, force interactive even if defaults exist
    
    # Voice priority
    if voice is None:
        if default_voice and not interactive:
            voice = default_voice
            console.print(f"[dim]Using default voice: {voice}[/dim]")
        # else: will trigger interactive selection below
    
    # Image model priority
    if image_model is None:
        if default_image_model and not interactive:
            image_model = default_image_model
            console.print(f"[dim]Using default image model: {image_model}[/dim]")
    
    # Gemini model priority
    if gemini_model is None:
        if default_gemini_model and not interactive:
            gemini_model = default_gemini_model
            console.print(f"[dim]Using default Gemini model: {gemini_model}[/dim]")
    
    # Duration priority
    if duration is None:
        if default_duration_minutes and not interactive:
            duration = default_duration_minutes
            console.print(f"[dim]Using default duration: {duration} minutes[/dim]")

    # Interactive prompt if not provided
    if not prompt:
        console.print(Panel.fit(
            "[bold cyan]Eleven Video Generator[/bold cyan]\n"
            "Generate a video from a text topic.",
            border_style="cyan"
        ))
        
        # Interactive Duration Selection (Story 3.6)
        # Only if still None and we're in a TTY
        if duration is None and is_tty:
            from eleven_video.ui.duration_selector import DurationSelector
            try:
                selector = DurationSelector()
                duration = selector.select_duration_interactive()
            except Exception as e:
                console.print(f"[yellow]⚠️ Duration selection error: {e}[/yellow]")
        elif duration is None and not is_tty:
            # R-004: Non-TTY fallback
            duration = 5  # Hardcoded fallback
            console.print("[dim]Non-interactive mode: using 5 minute default[/dim]")
        
        prompt = Prompt.ask("[bold green]Enter your video topic/prompt[/bold green]")
    
    # Load settings (respecting profile override)
    try:
        profile_override = _profile_override_state.get("profile")
        settings = Settings(_profile_override=profile_override)
    except ConfigurationError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        raise typer.Exit(1)

    # Interactive voice selection if still None and in TTY (Story 3.3)
    if voice is None:
        if is_tty:
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
        else:
            # R-004: Non-TTY - voice remains None (pipeline will use its default)
            console.print("[dim]Non-interactive mode: using default voice[/dim]")

    # Interactive Gemini model selection if still None and in TTY (Story 3.5)
    if gemini_model is None:
        if is_tty:
            from eleven_video.ui.gemini_model_selector import GeminiModelSelector
            gemini_adapter = GeminiAdapter(settings=settings)
            try:
                selector = GeminiModelSelector(gemini_adapter)
                gemini_model = selector.select_model_interactive()
            except Exception as e:
                console.print(f"[yellow]⚠️ Gemini model selection unavailable: {e}[/yellow]")
                console.print("[dim]Continuing with default Gemini model...[/dim]")
                gemini_model = None  # Graceful degradation
            finally:
                asyncio.run(gemini_adapter.close())
        else:
            # R-004: Non-TTY fallback
            console.print("[dim]Non-interactive mode: using default Gemini model[/dim]")

    # Interactive image model selection if still None and in TTY (Story 3.4)
    if image_model is None:
        if is_tty:
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
        else:
            console.print("[dim]Non-interactive mode: using default image model[/dim]")

    # Resolution selection (Story 3.8)
    from eleven_video.models.domain import Resolution
    selected_resolution = None
    
    if resolution:
        # 1. CLI Flag
        try:
            res_key = resolution.lower().strip()
            # Handle aliases
            if "1080" in res_key: res_key = "1080p"
            elif "720" in res_key: res_key = "720p"
            
            resolution_map = {
                "1080p": Resolution.HD_1080P,
                "720p": Resolution.HD_720P,
                "portrait": Resolution.PORTRAIT,
                "square": Resolution.SQUARE
            }
            
            if res_key not in resolution_map:
                raise KeyError(res_key)
            selected_resolution = resolution_map[res_key]
            console.print(f"[dim]Using resolution: {selected_resolution.value['label']}[/dim]")
        except KeyError:
            console.print(f"[red]Invalid resolution: {resolution}. Options: 1080p, 720p, portrait, square[/red]")
            raise typer.Exit(1)
            
    # 2. Interactive Selection (if no flag)
    if selected_resolution is None:
        if is_tty:
            from eleven_video.ui.resolution_selector import ResolutionSelector
            selector = ResolutionSelector()
            # Interactive prompt defaults to 1080p inside selector if skipped
            selected_resolution = selector.select_resolution(interactive=True)
        else:
            # Non-TTY fallback
            selected_resolution = Resolution.HD_1080P
            console.print("[dim]Non-interactive mode: using default 1080p resolution[/dim]")

    # Initialize pipeline
    pipeline = VideoPipeline(
        settings=settings, 
        output_dir=output.parent if output else None
    )

    try:
        console.print(f"\n[dim]Initializing pipeline for topic:[/dim] [bold]{prompt}[/bold]\n")
        
        # Run generation (pass model IDs - Story 3.4, 3.5)
        video = pipeline.generate(
            prompt=prompt, 
            voice_id=voice, 
            image_model_id=image_model,
            gemini_model_id=gemini_model,
            duration_minutes=duration,
            resolution=selected_resolution
        )
        
        # Success handled by pipeline.show_summary()
        
    except Exception as e:
        console.print(f"\n[red]❌ Generation Failed:[/red] {e}")
        # Debug info
        # console.print_exception()
        raise typer.Exit(1)


if __name__ == "__main__":
    app()