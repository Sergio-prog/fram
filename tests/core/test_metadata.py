import json

from PIL import Image

from fram.cli.commands import media_info
from fram.core.metadata import collect_media_metadata


def test_collect_image_metadata_includes_resolution_and_color(tmp_path) -> None:
    path = tmp_path / "image.png"
    Image.new("RGB", (120, 80), color="white").save(path)

    metadata = collect_media_metadata(path)

    assert metadata.value("Resolution") == "120x80"
    assert metadata.value("Color Scheme") == "RGB"
    assert metadata.value("Modified At") is not None


def test_media_info_formats_fields_line_by_line(tmp_path) -> None:
    path = tmp_path / "image.png"
    Image.new("RGB", (120, 80), color="white").save(path)

    text = media_info(path)

    assert "Resolution: 120x80" in text
    assert "Color Scheme: RGB" in text
    assert "\nModified At:" in text


def test_collect_video_metadata_uses_ffprobe(monkeypatch, tmp_path) -> None:
    path = tmp_path / "video.mp4"
    path.write_bytes(b"video")

    def fake_run_capture(args: list[str]) -> str:
        assert args[0] == "ffprobe"
        return json.dumps(
            {
                "streams": [
                    {
                        "codec_type": "video",
                        "width": 1920,
                        "height": 1080,
                        "codec_name": "h264",
                        "pix_fmt": "yuv420p",
                    }
                ],
                "format": {
                    "duration": "12.5",
                    "tags": {
                        "creation_time": "2026-01-01T00:00:00Z",
                        "artist": "Creator",
                        "keywords": "demo,fram",
                    },
                },
            }
        )

    monkeypatch.setattr("fram.core.metadata.run_capture", fake_run_capture)

    metadata = collect_media_metadata(path)

    assert metadata.value("Resolution") == "1920x1080"
    assert metadata.value("Duration") == "12.50s"
    assert metadata.value("Video Codec") == "h264"
    assert metadata.value("Creator") == "Creator"
    assert metadata.value("Keywords") == "demo,fram"

