
import uuid
import random
from pathlib import Path
from eleven_video.models.domain import Image, Audio, Script, Video, Resolution

def create_image(data: bytes = None, mime_type: str = "image/png") -> Image:
    if data is None:
        data = f"fake_image_data_{uuid.uuid4()}".encode()
    return Image(data=data, mime_type=mime_type)

def create_audio(data: bytes = None, duration_seconds: float = 5.0) -> Audio:
    if data is None:
        data = f"fake_audio_data_{uuid.uuid4()}".encode()
    return Audio(data=data, duration_seconds=duration_seconds)

def create_script(content: str = None) -> Script:
    if content is None:
        content = f"Script content generated {uuid.uuid4()}"
    return Script(content=content)

def create_video(file_path: Path = None, duration_seconds: float = 10.0, resolution: tuple = (1920, 1080)) -> Video:
    if file_path is None:
        file_path = Path(f"output_{uuid.uuid4()}.mp4")
    return Video(
        file_path=file_path,
        duration_seconds=duration_seconds,
        file_size_bytes=1024,
        resolution=resolution
    )

def create_resolution() -> Resolution:
    """Return a random Resolution enum member."""
    return random.choice(list(Resolution))
