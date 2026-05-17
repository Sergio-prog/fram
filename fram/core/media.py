from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from fram.core.errors import UnsupportedFormat


class MediaType(StrEnum):
    IMAGE = "image"
    VIDEO = "video"


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
VECTOR_EXTENSIONS = {".svg"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".gif"}


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    media_type: MediaType
    suffix: str
    size_bytes: int


def detect_media_type(path: Path) -> MediaType:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS or suffix in VECTOR_EXTENSIONS:
        return MediaType.IMAGE
    if suffix in VIDEO_EXTENSIONS:
        return MediaType.VIDEO
    raise UnsupportedFormat(f"Unsupported file type: {suffix or '<none>'}")


def get_media_info(path: Path) -> MediaInfo:
    media_type = detect_media_type(path)
    return MediaInfo(
        path=path,
        media_type=media_type,
        suffix=path.suffix.lower(),
        size_bytes=path.stat().st_size,
    )

