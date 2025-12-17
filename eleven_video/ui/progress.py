"""
Progress display for video generation pipeline (Story 2.5).

Provides unified Rich-based terminal display for progress updates
across all generation stages (script, audio, images, compilation).
"""
import re
import time
from pathlib import Path
from typing import Callable, Optional, TYPE_CHECKING

from rich.console import Console
from rich.panel import Panel

from eleven_video.ui.console import console as default_console
from eleven_video.models.domain import PipelineStage, STAGE_ICONS

if TYPE_CHECKING:
    from eleven_video.models.domain import Video


class VideoPipelineProgress:
    """Unified progress display for video generation pipeline.
    
    Coordinates progress display across all generation stages using Rich
    for consistent, visually appealing terminal output.
    
    Attributes:
        console: Rich Console instance for output.
        current_stage: Current pipeline stage.
        stage_start_times: Dict mapping stages to their start timestamps.
        pipeline_start_time: Overall pipeline start time for total duration.
        total_images: Total images to generate.
        completed_images: Number of images completed.
    
    Example:
        >>> progress = VideoPipelineProgress()
        >>> progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
        >>> callback = progress.create_callback()
        >>> # Pass callback to adapters
        >>> progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)
    """
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize progress display.
        
        Args:
            console: Optional Rich Console instance. If not provided,
                    uses the default console singleton.
        """
        self.console = console or default_console
        self.current_stage: PipelineStage = PipelineStage.INITIALIZING
        self.stage_start_times: dict[PipelineStage, float] = {}
        self.pipeline_start_time: Optional[float] = None
        self.total_images: int = 0
        self.completed_images: int = 0
    
    def start_stage(self, stage: PipelineStage) -> None:
        """Start a new pipeline stage.
        
        Records the start time and displays a message with the stage icon.
        If this is the first stage, also initializes the pipeline timer.
        
        Args:
            stage: The pipeline stage to start.
        """
        self.current_stage = stage
        self.stage_start_times[stage] = time.time()
        
        # Initialize pipeline timer on first stage
        if self.pipeline_start_time is None:
            self.pipeline_start_time = time.time()
        
        icon = STAGE_ICONS.get(stage, "▶")
        stage_name = stage.value.replace("_", " ").title()
        self.console.print(f"{icon} [bold]{stage_name}[/bold]...")
    
    def complete_stage(self, stage: PipelineStage) -> None:
        """Mark a stage as complete and display elapsed time.
        
        Args:
            stage: The pipeline stage that completed.
        """
        elapsed = 0.0
        if stage in self.stage_start_times:
            elapsed = time.time() - self.stage_start_times[stage]
        
        icon = STAGE_ICONS.get(PipelineStage.COMPLETED, "✓")
        stage_name = stage.value.replace("_", " ").title()
        self.console.print(
            f"  {icon} [green]{stage_name} complete[/green] ({elapsed:.1f}s)"
        )
    
    def update_progress(self, message: str) -> None:
        """Update progress with a message.
        
        Parses messages for image progress format and displays
        appropriate progress information.
        
        Args:
            message: Progress message from adapter.
        """
        # Parse "image X of Y" format for percentage display
        image_pattern = r"(?:Generating|Processing)\s+image\s+(\d+)\s+of\s+(\d+)"
        match = re.search(image_pattern, message, re.IGNORECASE)
        
        if match:
            self.completed_images = int(match.group(1))
            self.total_images = int(match.group(2))
            percentage = (self.completed_images / self.total_images) * 100
            self.console.print(
                f"  🖼️  Image {self.completed_images}/{self.total_images} "
                f"({percentage:.0f}%)"
            )
        else:
            # Generic message display
            self.console.print(f"  → {message}")
    
    def fail_stage(self, stage: PipelineStage, error: str) -> None:
        """Display error for a failed stage.
        
        Args:
            stage: The stage that failed.
            error: Error message to display.
        """
        self.current_stage = PipelineStage.FAILED
        
        icon = STAGE_ICONS.get(PipelineStage.FAILED, "❌")
        stage_name = stage.value.replace("_", " ").title()
        
        self.console.print(Panel(
            f"[red]{icon} {stage_name} failed[/red]\n\n{error}",
            title="Pipeline Error",
            border_style="red"
        ))
    
    def show_summary(self, output_path: Path, video: "Video") -> None:
        """Display success summary with video details.
        
        Args:
            output_path: Path to the output video file.
            video: Video domain model with metadata.
        """
        self.current_stage = PipelineStage.COMPLETED
        
        total_time = 0.0
        if self.pipeline_start_time:
            total_time = time.time() - self.pipeline_start_time
        
        # Calculate file size in MB
        file_size_mb = video.file_size_bytes / (1024 * 1024)
        
        self.console.print(Panel.fit(
            f"[green]✅ Video Generated Successfully![/green]\n\n"
            f"Output: {output_path}\n"
            f"Duration: {video.duration_seconds:.1f}s\n"
            f"Size: {file_size_mb:.1f} MB\n"
            f"Total time: {total_time:.1f}s",
            title="Complete",
            border_style="green"
        ))
    
    def create_callback(self) -> Callable[[str], None]:
        """Create a callback function for adapter progress updates.
        
        Returns a closure that can be passed to adapters as the
        progress_callback parameter.
        
        Returns:
            Callable[[str], None]: Callback function for progress updates.
        
        Example:
            >>> progress = VideoPipelineProgress()
            >>> callback = progress.create_callback()
            >>> adapter.generate_script(prompt, progress_callback=callback)
        """
        return self.update_progress
