from pathlib import Path

from PIL import Image

from fram.cli.formatting import (
    format_error,
    format_info_text,
    format_processed_path,
)


def test_format_processed_path_includes_media_summary(tmp_path: Path) -> None:
    source = tmp_path / "source.png"
    output = tmp_path / "output.png"
    Image.new("RGB", (20, 10), color="black").save(source)
    Image.new("RGB", (8, 4), color="white").save(output)

    text = format_processed_path(
        output,
        source=source,
        elapsed_seconds=0.12,
        compare_size=False,
        color=False,
    )

    assert "\u2713" in text
    assert str(output) in text
    assert "8x4" in text
    assert "0.1s" in text
    assert "\033" not in text


def test_format_processed_path_can_show_size_delta(tmp_path: Path) -> None:
    source = tmp_path / "source.bin"
    output = tmp_path / "output.bin"
    source.write_bytes(b"x" * 200)
    output.write_bytes(b"x" * 100)

    text = format_processed_path(source=source, path=output, compare_size=True, color=False)

    assert "200 B \u2192 100 B (-50%)" in text


def test_format_info_text_aligns_metadata() -> None:
    text = format_info_text("Path: image.png\nType: image", color=False)

    assert text == "Media info\n  Path  image.png\n  Type  image"


def test_format_error_supports_color() -> None:
    text = format_error("bad input", color=True)

    assert "\033[31m" in text
    assert "bad input" in text
