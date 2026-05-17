from pathlib import Path

import pytest

from fram.core.errors import UnsupportedFormat
from fram.core.media import MediaType, detect_media_type


@pytest.mark.parametrize(
    ("path", "media_type"),
    [
        ("photo.jpg", MediaType.IMAGE),
        ("photo.PNG", MediaType.IMAGE),
        ("vector.svg", MediaType.IMAGE),
        ("clip.mp4", MediaType.VIDEO),
        ("clip.WEBM", MediaType.VIDEO),
    ],
)
def test_detect_media_type(path: str, media_type: MediaType) -> None:
    assert detect_media_type(Path(path)) == media_type


def test_detect_media_type_rejects_unknown_suffix() -> None:
    with pytest.raises(UnsupportedFormat, match="Unsupported file type"):
        detect_media_type(Path("notes.txt"))

