"""Demo that writes output to file for visibility."""
import sys
from pathlib import Path

# Write to file
output_file = Path("demo_output.txt")
output_file.write_text("")  # Clear

def log(msg):
    print(msg)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=" * 60)
log("Story 2.5: Progress Updates Demo")
log("=" * 60)

try:
    from eleven_video.ui.progress import VideoPipelineProgress
    from eleven_video.models.domain import PipelineStage, Video
    import time
    
    log("\n[1] Creating progress tracker...")
    progress = VideoPipelineProgress()
    
    log("[2] Starting PROCESSING_SCRIPT stage...")
    progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
    time.sleep(0.3)
    progress.update_progress("Generating script from prompt...")
    time.sleep(0.3)
    progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)
    log("    OK - Script stage completed")
    
    log("[3] Starting PROCESSING_IMAGES stage...")
    progress.start_stage(PipelineStage.PROCESSING_IMAGES)
    for i in range(1, 4):
        progress.update_progress(f"Generating image {i} of 3")
        time.sleep(0.2)
    progress.complete_stage(PipelineStage.PROCESSING_IMAGES)
    log("    OK - Images stage completed")
    
    log("[4] Showing summary...")
    video = Video(
        file_path=Path("output/test.mp4"),
        duration_seconds=10.0,
        file_size_bytes=5_000_000,
        codec="h264",
        resolution=(1920, 1080)
    )
    progress.show_summary(Path("output/test.mp4"), video)
    
    log("\n" + "=" * 60)
    log("SUCCESS: Story 2.5 is working correctly!")
    log("=" * 60)
    
except Exception as e:
    log(f"\nERROR: {type(e).__name__}: {e}")
    import traceback
    log(traceback.format_exc())
