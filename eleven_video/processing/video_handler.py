"""Video compilation using moviepy/FFmpeg (Story 2.4, Story 2.7).

This module implements FFmpegVideoCompiler which compiles images and audio
into synchronized MP4 video files using moviepy (FFmpeg wrapper).
Story 2.7 adds Ken Burns-style zoom effects for dynamic video appearance.

Related files:
- eleven_video/models/domain.py: Video, Image, Audio domain models
- eleven_video/api/interfaces.py: VideoCompiler protocol
- eleven_video/exceptions/custom_errors.py: VideoProcessingError
"""
import os
import tempfile
from pathlib import Path
from typing import Callable, List, Optional

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

from eleven_video.models.domain import Audio, Image, Video
from eleven_video.exceptions.custom_errors import ValidationError, VideoProcessingError


class FFmpegVideoCompiler:
    """Compiles images and audio into synchronized MP4 video.
    
    Uses moviepy (FFmpeg wrapper) to create video files from image
    sequences and audio tracks. Output is 1920x1080 H.264/AAC MP4.
    
    Example:
        compiler = FFmpegVideoCompiler()
        video = compiler.compile_video(images, audio, Path("output.mp4"))
    """
    
    # Output specifications per architecture
    OUTPUT_RESOLUTION = (1920, 1080)
    OUTPUT_FPS = 24
    VIDEO_CODEC = "libx264"
    AUDIO_CODEC = "aac"
    # Zoom effect settings (Story 2.7)
    ZOOM_SCALE_FACTOR = 1.08  # 8% zoom (subtle, within 5-10% range)
    
    def compile_video(
        self,
        images: List[Image],
        audio: Audio,
        output_path: Path,
        progress_callback: Optional[Callable[[str], None]] = None,
        enable_zoom: bool = True
    ) -> Video:
        """Compile images and audio into synchronized video.
        
        Args:
            images: List of Image domain models to include in video.
            audio: Audio domain model for the video soundtrack.
            output_path: Path where the MP4 video will be saved.
            progress_callback: Optional callback for progress updates.
            enable_zoom: Whether to apply Ken Burns zoom effects (default True).
            
        Returns:
            Video domain model with file path, duration, and size.
            
        Raises:
            ValidationError: If images or audio are empty/invalid.
            VideoProcessingError: If FFmpeg fails or disk errors occur.
        """
        # Validation (AC6)
        self._validate_inputs(images, audio)
        
        # Use temporary directory for all temp files (AC6 - cleanup)
        with tempfile.TemporaryDirectory(prefix="eleven_video_") as temp_dir:
            try:
                # Write images and audio to temp files
                image_paths = self._write_temp_images(images, temp_dir, progress_callback)
                audio_path = self._write_temp_audio(audio, temp_dir)
                
                # Get audio duration for image timing
                audio_duration = self._get_audio_duration(audio, audio_path)
                
                # Calculate duration per image (AC3)
                duration_per_image = audio_duration / len(images)
                
                # Create video clips from images with optional zoom effects (Story 2.7)
                clips = self._create_image_clips(
                    image_paths, 
                    duration_per_image, 
                    progress_callback,
                    enable_zoom=enable_zoom
                )
                
                # Concatenate and add audio
                if progress_callback:
                    progress_callback("Compiling video...")
                
                final_clip = concatenate_videoclips(clips, method="compose")
                audio_clip = AudioFileClip(audio_path)
                final_clip = final_clip.with_audio(audio_clip)
                
                # Write output video (AC5)
                final_clip.write_videofile(
                    str(output_path),
                    codec=self.VIDEO_CODEC,
                    audio_codec=self.AUDIO_CODEC,
                    fps=self.OUTPUT_FPS,
                    logger=None  # Suppress verbose output
                )
                
                # Clean up clips
                final_clip.close()
                audio_clip.close()
                for clip in clips:
                    clip.close()
                
                # Create Video domain model (AC7)
                file_size = output_path.stat().st_size if output_path.exists() else 0
                
                return Video(
                    file_path=output_path,
                    duration_seconds=audio_duration,
                    file_size_bytes=file_size,
                    codec="h264",
                    resolution=self.OUTPUT_RESOLUTION
                )
                
            except ValidationError:
                raise
            except OSError as e:
                error_msg = str(e).lower()
                if "ffmpeg" in error_msg:
                    raise VideoProcessingError(
                        "FFmpeg required but not found. Install FFmpeg and add to PATH."
                    ) from e
                elif "permission" in error_msg:
                    raise VideoProcessingError(
                        f"Cannot write video to {output_path}: Permission denied"
                    ) from e
                else:
                    raise VideoProcessingError(f"Video processing failed: {e}") from e
            except Exception as e:
                raise VideoProcessingError(f"Video processing failed: {e}") from e
    
    def _validate_inputs(self, images: List[Image], audio: Audio) -> None:
        """Validate input parameters.
        
        Raises:
            ValidationError: If images or audio are empty/invalid.
        """
        if not images:
            raise ValidationError("Cannot compile video: no images provided")
        
        if audio is None:
            raise ValidationError("Cannot compile video: no audio provided")
        
        if not audio.data:
            raise ValidationError("Cannot compile video: audio data is empty")
    
    def _write_temp_images(
        self, 
        images: List[Image], 
        temp_dir: str,
        progress_callback: Optional[Callable[[str], None]]
    ) -> List[str]:
        """Write images to temporary files.
        
        Returns:
            List of paths to temporary image files.
        """
        paths = []
        for i, image in enumerate(images):
            ext = "png" if "png" in image.mime_type else "jpg"
            path = os.path.join(temp_dir, f"image_{i:03d}.{ext}")
            with open(path, "wb") as f:
                f.write(image.data)
            paths.append(path)
        return paths
    
    def _write_temp_audio(self, audio: Audio, temp_dir: str) -> str:
        """Write audio to temporary file.
        
        Returns:
            Path to temporary audio file.
        """
        path = os.path.join(temp_dir, "audio.mp3")
        with open(path, "wb") as f:
            f.write(audio.data)
        return path
    
    def _get_audio_duration(self, audio: Audio, audio_path: str) -> float:
        """Get audio duration in seconds.
        
        Uses audio.duration_seconds if available, otherwise reads from file.
        """
        if audio.duration_seconds is not None:
            return audio.duration_seconds
        
        # Calculate from audio file
        with AudioFileClip(audio_path) as clip:
            return clip.duration
    
    def _create_image_clips(
        self,
        image_paths: List[str],
        duration_per_image: float,
        progress_callback: Optional[Callable[[str], None]],
        enable_zoom: bool = True
    ) -> List:
        """Create video clips from images with optional zoom effects.
        
        Args:
            image_paths: Paths to image files.
            duration_per_image: Duration each image should display.
            progress_callback: Optional progress callback.
            enable_zoom: Whether to apply Ken Burns zoom effects.
            
        Returns:
            List of ImageClip objects.
        """
        clips = []
        total = len(image_paths)
        
        for i, path in enumerate(image_paths):
            if progress_callback:
                progress_callback(f"Processing image {i + 1} of {total}")
            
            try:
                # Create clip and set duration
                clip = ImageClip(path)
                clip = clip.with_duration(duration_per_image)
                
                if enable_zoom:
                    # Apply alternating zoom effects (Story 2.7)
                    # Even indices = zoom in, odd indices = zoom out
                    zoom_direction = "in" if i % 2 == 0 else "out"
                    clip = self._apply_zoom_effect(clip, zoom_direction)
                else:
                    # No zoom - just resize to output resolution
                    clip = clip.resized(newsize=self.OUTPUT_RESOLUTION)
                
                clips.append(clip)
            except (RuntimeError, ValueError, OSError, TypeError):
                # Fallback: static image on any zoom error (AC6)
                if progress_callback:
                    progress_callback(f"Warning: zoom failed for image {i + 1}, using static")
                clip = ImageClip(path)
                clip = clip.with_duration(duration_per_image)
                clip = clip.resized(newsize=self.OUTPUT_RESOLUTION)
                clips.append(clip)
        
        return clips
    
    def _apply_zoom_effect(
        self,
        clip: "ImageClip",
        zoom_direction: str = "in"
    ) -> "ImageClip":
        """Apply Ken Burns-style zoom effect to an image clip.
        
        Uses moviepy's fl() method for frame-level transformation.
        The zoom effect scales the image and center-crops to maintain
        the 1920x1080 output resolution.
        
        Args:
            clip: The base ImageClip to apply the effect to.
            zoom_direction: "in" for zoom-in (1.0 → 1.08), "out" for zoom-out (1.08 → 1.0).
            
        Returns:
            Modified clip with zoom effect applied.
        """
        from PIL import Image as PILImage
        import numpy as np
        
        # Zoom parameters (subtle 5-10% change)
        zoom_factor = self.ZOOM_SCALE_FACTOR  # 1.08
        if zoom_direction == "in":
            start_scale, end_scale = 1.0, zoom_factor
        else:
            start_scale, end_scale = zoom_factor, 1.0
        
        w, h = self.OUTPUT_RESOLUTION
        duration = clip.duration
        
        def zoom_effect(get_frame, t):
            """Apply zoom for frame at time t."""
            # Linear interpolation of scale
            progress = t / duration if duration > 0 else 0
            scale = start_scale + (end_scale - start_scale) * progress
            
            # Calculate dimensions for scaled frame
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Get frame and resize
            frame = get_frame(t)
            
            # Use PIL for high-quality resize
            img = PILImage.fromarray(frame)
            
            # For zoom-out, first upscale to max needed size to avoid quality loss
            # This ensures we never upscale from a smaller image
            max_scale = max(start_scale, end_scale)
            base_w, base_h = int(w * max_scale), int(h * max_scale)
            if img.size != (base_w, base_h):
                img = img.resize((base_w, base_h), PILImage.LANCZOS)
            
            # Now scale to current frame's target size
            img_scaled = img.resize((new_w, new_h), PILImage.LANCZOS)
            
            # Center crop to output resolution
            x_off = (new_w - w) // 2
            y_off = (new_h - h) // 2
            img_cropped = img_scaled.crop((x_off, y_off, x_off + w, y_off + h))
            
            return np.array(img_cropped)
        
        # Apply frame-level transformation
        return clip.fl(zoom_effect)

