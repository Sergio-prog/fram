from pathlib import Path

from fram.core.operation_factory import convert, extract_audio, extract_frame, gif, resize
from fram.core.output import default_output_for_operations


def test_default_output_uses_input_suffix_for_normal_operations() -> None:
    output = default_output_for_operations(Path("clip.mp4"), [resize("320x240")])

    assert output == Path("clip.fram.mp4")


def test_default_output_uses_generated_media_suffixes() -> None:
    assert default_output_for_operations(Path("clip.mp4"), [extract_frame("1")]) == Path(
        "clip.fram.png"
    )
    assert default_output_for_operations(Path("clip.mp4"), [extract_audio()]) == Path(
        "clip.fram.m4a"
    )
    assert default_output_for_operations(Path("clip.mp4"), [gif()]) == Path("clip.fram.gif")


def test_default_output_uses_convert_format_suffix() -> None:
    output = default_output_for_operations(Path("photo.png"), [convert("webp")])

    assert output == Path("photo.fram.webp")
