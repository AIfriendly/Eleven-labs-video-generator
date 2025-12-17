"""Simple test to verify output works."""
print("=" * 50)
print("TEST: Can you see this output?")
print("=" * 50)

try:
    from eleven_video.ui.progress import VideoPipelineProgress
    from eleven_video.models.domain import PipelineStage
    print("[OK] Imports successful")
    
    progress = VideoPipelineProgress()
    print("[OK] Created VideoPipelineProgress")
    
    progress.start_stage(PipelineStage.PROCESSING_SCRIPT)
    print("[OK] Started stage")
    
    progress.complete_stage(PipelineStage.PROCESSING_SCRIPT)
    print("[OK] Completed stage")
    
    print("\n" + "=" * 50)
    print("SUCCESS: Story 2.5 is working!")
    print("=" * 50)
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
