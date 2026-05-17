from pathlib import Path

from PIL import Image

from fram.cli.interactive.previews import (
    cleanup_preview,
    prepare_preview_image,
    prepare_video_preview,
)
from fram.core.media import MediaType


def test_prepare_image_preview_uses_original_path(tmp_path) -> None:
    path = tmp_path / "image.png"
    Image.new("RGB", (10, 10), color="black").save(path)

    preview = prepare_preview_image(path, MediaType.IMAGE)

    assert preview.path == path
    assert preview.error == ""
    assert preview.is_temporary is False


def test_prepare_preview_reports_error_for_invalid_image(tmp_path) -> None:
    path = tmp_path / "broken.png"
    path.write_text("not an image")

    preview = prepare_preview_image(path, MediaType.IMAGE)

    assert preview.path == path


def test_cleanup_preview_removes_temporary_file(tmp_path) -> None:
    path = tmp_path / "preview.jpg"
    path.write_bytes(b"preview")
    preview = type("Preview", (), {"is_temporary": True, "path": path})()

    cleanup_preview(preview)

    assert not path.exists()


def test_prepare_video_preview_uses_ffmpeg(monkeypatch, tmp_path) -> None:
    source = tmp_path / "video.mp4"
    source.write_bytes(b"")
    calls: list[list[str]] = []

    def fake_run_command(args: list[str]) -> None:
        calls.append(args)
        Path(args[-1]).write_bytes(b"frame")

    monkeypatch.setattr("fram.cli.interactive.previews.run_command", fake_run_command)

    preview = prepare_video_preview(source)

    try:
        assert preview.path is not None
        assert preview.path.exists()
        assert preview.is_temporary is True
        assert calls[0][0] == "ffmpeg"
    finally:
        cleanup_preview(preview)
