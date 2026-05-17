from pathlib import Path
from uuid import uuid4

from aiogram import Bot
from aiogram.types import Message

from fram.bot.config import settings
from fram.core.errors import UnsupportedFormat
from fram.core.media import MediaType, detect_media_type

IMAGE_SUFFIX_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

VIDEO_SUFFIX_BY_MIME = {
    "video/mp4": ".mp4",
    "video/quicktime": ".mov",
    "video/webm": ".webm",
}


class DownloadedMedia:
    def __init__(self, path: Path, media_type: MediaType, filename: str) -> None:
        self.path = path
        self.media_type = media_type
        self.filename = filename


async def download_media(message: Message, bot: Bot) -> DownloadedMedia:
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    bot_dir = settings.work_dir / "bot"
    bot_dir.mkdir(parents=True, exist_ok=True)

    downloadable: object
    filename: str
    suffix: str

    if message.document:
        downloadable = message.document
        filename = message.document.file_name or "media"
        suffix = Path(filename).suffix or IMAGE_SUFFIX_BY_MIME.get(
            message.document.mime_type or "",
            "",
        )
    elif message.video:
        downloadable = message.video
        filename = message.video.file_name or "video.mp4"
        suffix = Path(filename).suffix or VIDEO_SUFFIX_BY_MIME.get(
            message.video.mime_type or "",
            ".mp4",
        )
    elif message.photo:
        downloadable = message.photo[-1]
        filename = "photo.jpg"
        suffix = ".jpg"
    else:
        raise UnsupportedFormat("No supported media found.")

    path = bot_dir / f"{uuid4().hex}{suffix.lower()}"
    await bot.download(downloadable, destination=path)
    return DownloadedMedia(path=path, media_type=detect_media_type(path), filename=filename)


def cleanup_paths(*paths: Path | None) -> None:
    for path in paths:
        if path and path.exists():
            path.unlink(missing_ok=True)
