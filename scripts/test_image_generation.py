"""
Quick script to test real image generation with Gemini API.
Run with: uv run python scripts/test_image_generation.py
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eleven_video.api.gemini import GeminiAdapter
from eleven_video.models.domain import Script


def main():
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not set in environment")
        print("   Set it with: $env:GEMINI_API_KEY = 'your-key-here'")
        return 1
    
    print("🔑 API key found")
    
    # Create adapter
    adapter = GeminiAdapter(api_key=api_key)
    print("✅ GeminiAdapter initialized")
    
    # Create a test script
    script = Script(content="A majestic mountain landscape at golden hour with snow-capped peaks.")
    print(f"📝 Script: {script.content}")
    
    # Progress callback
    def on_progress(status: str):
        print(f"   ⏳ {status}")
    
    print("\n🎨 Generating image...")
    try:
        images = adapter.generate_images(script, progress_callback=on_progress)
        
        print(f"\n✅ Generated {len(images)} image(s)!")
        
        for i, image in enumerate(images):
            # Save image to disk
            output_path = f"output/test_image_{i+1}.png"
            os.makedirs("output", exist_ok=True)
            
            with open(output_path, "wb") as f:
                f.write(image.data)
            
            print(f"   📁 Saved: {output_path}")
            print(f"      Type: {image.mime_type}")
            print(f"      Size: {len(image.data):,} bytes")
        
        print("\n🎉 Image generation successful!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
