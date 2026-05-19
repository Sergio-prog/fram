import pytest

from fram.cli.interactive.operations import (
    actions_for,
    build_interactive_operation,
    describe_operation,
    value_presets_for,
)
from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operations import (
    CropParams,
    CutParams,
    ExtractAudioParams,
    FpsParams,
    GifParams,
    GrayscaleParams,
    ResizeMode,
    ResizeParams,
    SpeedParams,
    StripAudioParams,
    StripMetadataParams,
)


def test_actions_for_media_type() -> None:
    assert "resize" in actions_for(MediaType.IMAGE)
    assert "rotate" in actions_for(MediaType.IMAGE)
    assert "cut" not in actions_for(MediaType.IMAGE)
    assert "cut" in actions_for(MediaType.VIDEO)
    assert "extract-audio" in actions_for(MediaType.VIDEO)


def test_value_presets_for_cut_uses_slider_value() -> None:
    assert value_presets_for("cut", "00:01 00:05")[0] == "00:01 00:05"


def test_build_resize_from_tui_input() -> None:
    operation = build_interactive_operation("resize", MediaType.IMAGE, "320x240 fill")

    assert isinstance(operation.params, ResizeParams)
    assert operation.params.size.width == 320
    assert operation.params.mode == ResizeMode.FILL


def test_build_crop_from_tui_input() -> None:
    operation = build_interactive_operation("crop", MediaType.IMAGE, "100x100 top-left")

    assert isinstance(operation.params, CropParams)
    assert operation.params.anchor.value == "top-left"


def test_build_cut_from_tui_input() -> None:
    operation = build_interactive_operation("cut", MediaType.VIDEO, "5 duration 10")

    assert isinstance(operation.params, CutParams)
    assert operation.params.start_seconds == 5
    assert operation.params.duration_seconds == 10


def test_build_fps_and_strip_audio_from_tui_input() -> None:
    fps_operation = build_interactive_operation("fps", MediaType.VIDEO, "24")
    strip_operation = build_interactive_operation("strip-audio", MediaType.VIDEO, "")

    assert isinstance(fps_operation.params, FpsParams)
    assert isinstance(strip_operation.params, StripAudioParams)


def test_build_no_param_and_video_utility_operations_from_tui_input() -> None:
    strip_metadata_operation = build_interactive_operation("strip-metadata", MediaType.IMAGE, "")
    grayscale_operation = build_interactive_operation("grayscale", MediaType.VIDEO, "")
    extract_audio_operation = build_interactive_operation("extract-audio", MediaType.VIDEO, "")
    gif_operation = build_interactive_operation("gif", MediaType.VIDEO, "12 480")
    speed_operation = build_interactive_operation("speed", MediaType.VIDEO, "2")

    assert isinstance(strip_metadata_operation.params, StripMetadataParams)
    assert isinstance(grayscale_operation.params, GrayscaleParams)
    assert isinstance(extract_audio_operation.params, ExtractAudioParams)
    assert isinstance(gif_operation.params, GifParams)
    assert isinstance(speed_operation.params, SpeedParams)


def test_describe_operation() -> None:
    operation = build_interactive_operation("resize", MediaType.IMAGE, "320x240")

    assert describe_operation(operation) == "resize 320x240 mode=fit"


def test_build_interactive_operation_rejects_bad_input() -> None:
    with pytest.raises(InvalidOperation):
        build_interactive_operation("fps", MediaType.VIDEO, "fast")
