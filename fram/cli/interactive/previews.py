import tempfile
from dataclasses import dataclass
from pathlib import Path

from fram.core.media import MediaType
from fram.utils.process import run_command


@dataclass(frozen=True)
class PreviewImage:
    path: Path | None
    error: str = ""
    is_temporary: bool = False


def prepare_preview_image(path: Path, media_type: MediaType) -> PreviewImage:
    try:
        if media_type == MediaType.IMAGE:
            return PreviewImage(path=path)
        return prepare_video_preview(path)
    except Exception as exc:
        return PreviewImage(path=None, error=f"Preview unavailable: {exc}")


def prepare_video_preview(path: Path) -> PreviewImage:
    handle = tempfile.NamedTemporaryFile(prefix="fram-preview-", suffix=".jpg", delete=False)
    frame_path = Path(handle.name)
    handle.close()

    try:
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
    except Exception:
        frame_path.unlink(missing_ok=True)
        raise

    return PreviewImage(path=frame_path, is_temporary=True)


def cleanup_preview(preview: PreviewImage | None) -> None:
    if preview and preview.is_temporary and preview.path:
        preview.path.unlink(missing_ok=True)
