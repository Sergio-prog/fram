from dataclasses import dataclass
from pathlib import Path

from fram.core.media import IMAGE_EXTENSIONS, VECTOR_EXTENSIONS, VIDEO_EXTENSIONS

MEDIA_EXTENSIONS = IMAGE_EXTENSIONS | VECTOR_EXTENSIONS | VIDEO_EXTENSIONS


@dataclass(frozen=True)
class BrowserEntry:
    label: str
    path: Path
    is_dir: bool
    is_media: bool


def discover_media_files(root: Path) -> list[Path]:
    files = [
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in MEDIA_EXTENSIONS
    ]
    return sorted(files, key=lambda path: path.name.lower())


def list_browser_entries(root: Path) -> list[BrowserEntry]:
    entries: list[BrowserEntry] = []
    if root.parent != root:
        entries.append(BrowserEntry("..", root.parent, is_dir=True, is_media=False))

    for path in sorted(root.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
        if path.name.startswith("."):
            continue
        if path.is_dir():
            entries.append(BrowserEntry(f"{path.name}/", path, is_dir=True, is_media=False))
            continue
        is_media = path.suffix.lower() in MEDIA_EXTENSIONS
        if is_media:
            entries.append(BrowserEntry(path.name, path, is_dir=False, is_media=True))

    return entries
