from pathlib import Path

from fram.core.media import IMAGE_EXTENSIONS, VECTOR_EXTENSIONS, VIDEO_EXTENSIONS

MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VECTOR_EXTENSIONS | VIDEO_EXTENSIONS


def discover_media_files(root: Path) -> list[Path]:
    files = [
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS
    ]
    return sorted(files, key=lambda path: path.name.lower())

