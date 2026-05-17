import tempfile
from pathlib import Path

from PIL import Image, ImageOps

from fram.core.media import MediaType
from fram.utils.process import run_command

ASCII_RAMP = " .:-=+*#%@"


def render_preview(path: Path, media_type: MediaType, width: int = 38, height: int = 14) -> str:
    try:
        if media_type == MediaType.IMAGE:
            return render_image_preview(path, width, height)
        return render_video_preview(path, width, height)
    except Exception as exc:
        return f"Preview unavailable: {exc}"


def render_image_preview(path: Path, width: int = 38, height: int = 14) -> str:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        return image_to_ascii(image, width, height)


def render_video_preview(path: Path, width: int = 38, height: int = 14) -> str:
    with tempfile.TemporaryDirectory() as tmp_dir:
        frame_path = Path(tmp_dir) / "frame.jpg"
        run_command(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "1",
                "-i",
                str(path),
                "-frames:v",
                "1",
                str(frame_path),
            ]
        )
        return render_image_preview(frame_path, width, height)


def image_to_ascii(image: Image.Image, width: int = 38, height: int = 14) -> str:
    thumbnail = ImageOps.contain(image.convert("L"), (width, height))
    canvas = Image.new("L", (width, height), color=255)
    left = (width - thumbnail.width) // 2
    top = (height - thumbnail.height) // 2
    canvas.paste(thumbnail, (left, top))

    chars = []
    for y in range(height):
        line = []
        for x in range(width):
            pixel = canvas.getpixel((x, y))
            index = min(len(ASCII_RAMP) - 1, pixel * len(ASCII_RAMP) // 256)
            line.append(ASCII_RAMP[index])
        chars.append("".join(line).rstrip())
    return "\n".join(chars)

