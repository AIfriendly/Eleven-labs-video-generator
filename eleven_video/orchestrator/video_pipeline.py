from pathlib import Path
from typing import Optional
import datetime

from eleven_video.config import Settings
from eleven_video.api.gemini import GeminiAdapter
from eleven_video.api.elevenlabs import ElevenLabsAdapter
from eleven_video.processing.video_handler import FFmpegVideoCompiler
from eleven_video.ui.progress import VideoPipelineProgress
from eleven_video.models.domain import Video, PipelineStage

class VideoPipeline:
    """Orchestrates end-to-end video generation."""
    
    def __init__(
        self, 
        settings: Settings,
        output_dir: Optional[Path] = None,
        progress: Optional[VideoPipelineProgress] = None
    ):
        self.settings = settings
        self.output_dir = output_dir or Path(self.settings.project_root) / "output"
        self.progress = progress or VideoPipelineProgress()
        # Lazy init placeholders
        self._gemini: Optional[GeminiAdapter] = None
        self._elevenlabs: Optional[ElevenLabsAdapter] = None
        self._compiler: Optional[FFmpegVideoCompiler] = None

    def _init_adapters(self):
        """Lazy initialization with settings."""
        if not self._gemini:
            self._gemini = GeminiAdapter(settings=self.settings)
        if not self._elevenlabs:
            self._elevenlabs = ElevenLabsAdapter(settings=self.settings)
        if not self._compiler:
            self._compiler = FFmpegVideoCompiler()

    def generate(self, prompt: str, voice_id: Optional[str] = None, image_model_id: Optional[str] = None) -> Video:
        """Run full pipeline.
        
        Args:
            prompt: Text topic.
            voice_id: Optional ElevenLabs voice ID.
            image_model_id: Optional Gemini image model ID (Story 3.4).
        """
        self._init_adapters()
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        callback = self.progress.create_callback()
        
        try:
            # 1. Script
            self.progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
            script = self._gemini.generate_script(prompt, progress_callback=callback)
            self.progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)

            # 2. Audio (Pass voice_id)
            self.progress.start_stage(PipelineStage.PROCESSING_AUDIO)
            audio = self._elevenlabs.generate_speech(
                text=script.content, 
                voice_id=voice_id,
                progress_callback=callback
            )
            self.progress.complete_stage(PipelineStage.PROCESSING_AUDIO)

            # 3. Images (Pass image_model_id - Story 3.4)
            self.progress.start_stage(PipelineStage.PROCESSING_IMAGES)
            images = self._gemini.generate_images(script, progress_callback=callback, model_id=image_model_id)
            self.progress.complete_stage(PipelineStage.PROCESSING_IMAGES)

            # 4. Compile
            self.progress.start_stage(PipelineStage.COMPILING_VIDEO)
            output_path = self._generate_output_path()
            video = self._compiler.compile_video(images, audio, output_path, progress_callback=callback)
            self.progress.complete_stage(PipelineStage.COMPILING_VIDEO)

            self.progress.show_summary(output_path, video)
            return video

        except Exception as e:
            self.progress.fail_stage(self.progress.current_stage, str(e))
            raise

    def _generate_output_path(self) -> Path:
        """Generate a unique output path based on timestamp."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"video_{timestamp}.mp4"
