import logging
from pathlib import Path
from typing import Optional
import datetime

from eleven_video.config import Settings
from eleven_video.api.gemini import GeminiAdapter
from eleven_video.api.elevenlabs import ElevenLabsAdapter
from eleven_video.processing.video_handler import FFmpegVideoCompiler
from eleven_video.ui.progress import VideoPipelineProgress
from eleven_video.models.domain import Video, PipelineStage, Resolution
from eleven_video.monitoring.usage import UsageMonitor
from eleven_video.ui.usage_panel import UsageDisplay

logger = logging.getLogger(__name__)


class VideoPipeline:
    """Orchestrates end-to-end video generation."""
    
    def __init__(
        self, 
        settings: Settings,
        output_dir: Optional[Path] = None,
        progress: Optional[VideoPipelineProgress] = None,
        show_usage: bool = True
    ):
        self.settings = settings
        self.output_dir = output_dir or Path(self.settings.project_root) / "output"
        self.progress = progress or VideoPipelineProgress()
        self.show_usage = show_usage
        # Lazy init placeholders
        self._gemini: Optional[GeminiAdapter] = None
        self._elevenlabs: Optional[ElevenLabsAdapter] = None
        self._compiler: Optional[FFmpegVideoCompiler] = None
        self._usage_display: Optional[UsageDisplay] = None

    def _init_adapters(self):
        """Lazy initialization with settings."""
        if not self._gemini:
            self._gemini = GeminiAdapter(settings=self.settings)
        if not self._elevenlabs:
            self._elevenlabs = ElevenLabsAdapter(settings=self.settings)
        if not self._compiler:
            self._compiler = FFmpegVideoCompiler()

    def _init_usage_monitoring(self) -> None:
        """Initialize usage monitoring for the session (Story 5.1)."""
        # Reset monitor for fresh session
        monitor = UsageMonitor.get_instance()
        monitor.reset()
        
        # Initialize display if enabled
        if self.show_usage:
            self._usage_display = UsageDisplay(update_interval=5.0)


    def _start_usage_display(self) -> None:
        """Start live usage display (Story 5.1 - AC1, AC2).
        
        Note: Due to conflicts between Rich.Live and console.print(),
        we use a stage-based approach instead of continuous live updates.
        """
        if self._usage_display and self.show_usage:
            # Print initial header
            from eleven_video.ui.console import console
            console.print("\n[bold blue]📊 API Usage Tracking Enabled[/bold blue]")

    def _print_usage_update(self) -> None:
        """Print current usage summary after each stage (Story 5.1 - AC3).
        
        Shows running totals of tokens, characters, and estimated cost.
        """
        if not self.show_usage:
            return
            
        monitor = UsageMonitor.get_instance()
        summary = monitor.get_summary()
        
        if summary.get("events_count", 0) > 0:
            from eleven_video.ui.console import console
            
            # Build compact usage line
            parts = []
            for service, details in summary.get("by_service", {}).items():
                metrics = details.get("metrics", {})
                for metric, value in metrics.items():
                    if value > 0:
                        if value >= 1_000_000:
                            formatted = f"{value/1_000_000:.1f}M"
                        elif value >= 1_000:
                            formatted = f"{value/1_000:.0f}K"
                        else:
                            formatted = str(value)
                        parts.append(f"{metric.replace('_', ' ')}: {formatted}")
            
            total_cost = summary.get("total_cost", 0)
            usage_str = " | ".join(parts) if parts else "tracking..."
            console.print(f"  [dim]💰 Usage: {usage_str} → ${total_cost:.4f}[/dim]")

    def _stop_usage_display(self) -> None:
        """Stop live usage display and show final summary (Story 5.1 - AC6)."""
        if self._usage_display:
            self._usage_display.stop_live_update()
        
        # Print final usage summary to console (visible to user)
        self._print_final_usage_summary()
        
        # Log detailed summary (AC6)
        self._log_usage_summary()

    def _print_final_usage_summary(self) -> None:
        """Print visible final usage summary panel (Story 5.1 - AC6)."""
        if not self.show_usage:
            return
            
        monitor = UsageMonitor.get_instance()
        summary = monitor.get_summary()
        
        if summary.get("events_count", 0) > 0:
            try:
                # Reuse UsageDisplay for consistent formatting (Story 5.3 fix)
                display = self._usage_display or UsageDisplay()
                display.render_once()
            except Exception as e:
                logger.error(f"Failed to display usage summary: {e}")

    def _log_usage_summary(self) -> None:
        """Log final usage summary at session end (Story 5.1 - AC6)."""
        monitor = UsageMonitor.get_instance()
        summary = monitor.get_summary()
        
        if summary.get("events_count", 0) > 0:
            logger.debug("=== Session Usage Summary ===")
            logger.debug(f"Total Estimated Cost: ${summary.get('total_cost', 0):.2f}")
            
            for service, details in summary.get("by_service", {}).items():
                metrics = details.get("metrics", {})
                cost = details.get("cost", 0)
                logger.debug(f"  {service}: {metrics} (${cost:.4f})")
            
            logger.debug(f"Total Events: {summary.get('events_count', 0)}")

    def generate(self, prompt: str, voice_id: Optional[str] = None, image_model_id: Optional[str] = None, gemini_model_id: Optional[str] = None, duration_minutes: Optional[int] = None, resolution: Optional[Resolution] = None) -> Video:
        """Run full pipeline.
        
        Args:
            prompt: Text topic.
            voice_id: Optional ElevenLabs voice ID.
            image_model_id: Optional Gemini image model ID (Story 3.4).
            gemini_model_id: Optional Gemini text model ID for script (Story 3.5).
            duration_minutes: Optional video duration in minutes (Story 3.6).
            resolution: Optional output resolution (Story 3.8).
        """
        self._init_adapters()
        # Initialize usage monitoring (Story 5.1)
        self._init_usage_monitoring()
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        callback = self.progress.create_callback()
        
        # Start live usage display (Story 5.1 - AC1)
        self._start_usage_display()
        
        try:
            # 1. Script (Pass gemini_model_id - Story 3.5, duration - Story 3.6)
            self.progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
            script = self._gemini.generate_script(prompt, progress_callback=callback, model_id=gemini_model_id, duration_minutes=duration_minutes)
            self.progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)
            self._print_usage_update()  # Story 5.1 - show running usage

            # 2. Audio (Pass voice_id)
            self.progress.start_stage(PipelineStage.PROCESSING_AUDIO)
            audio = self._elevenlabs.generate_speech(
                text=script.content, 
                voice_id=voice_id,
                progress_callback=callback
            )
            self.progress.complete_stage(PipelineStage.PROCESSING_AUDIO)
            self._print_usage_update()  # Story 5.1 - show running usage

            # 3. Images (Pass image_model_id - Story 3.4, calculate count - Story 3.6)
            self.progress.start_stage(PipelineStage.PROCESSING_IMAGES)
            
            # Calculate target image count (15 images/min default)
            target_image_count = duration_minutes * 15 if duration_minutes else None
            
            images = self._gemini.generate_images(script, progress_callback=callback, model_id=image_model_id, target_image_count=target_image_count)
            self.progress.complete_stage(PipelineStage.PROCESSING_IMAGES)
            self._print_usage_update()  # Story 5.1 - show running usage

            # 4. Compile
            self.progress.start_stage(PipelineStage.COMPILING_VIDEO)
            output_path = self._generate_output_path()
            video = self._compiler.compile_video(images, audio, output_path, progress_callback=callback, resolution=resolution)
            self.progress.complete_stage(PipelineStage.COMPILING_VIDEO)

            # Stop usage display and log summary (Story 5.1 - AC6)
            self._stop_usage_display()
            
            self.progress.show_summary(output_path, video)
            return video

        except Exception as e:
            # Stop usage display on error too
            self._stop_usage_display()
            self.progress.fail_stage(self.progress.current_stage, str(e))
            raise

    def _generate_output_path(self) -> Path:
        """Generate a unique output path based on timestamp."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"video_{timestamp}.mp4"
