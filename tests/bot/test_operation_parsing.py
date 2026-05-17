import pytest

from fram.bot.services.operations import build_operation
from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operations import (
    CropParams,
    CutParams,
    FpsParams,
    ImageCompressParams,
    OperationName,
    ResizeParams,
    StripAudioParams,
    VideoCompressParams,
)


def test_build_resize_operation_from_bot_input() -> None:
    operation = build_operation("resize", MediaType.IMAGE, "128x128")

    assert operation.name == OperationName.RESIZE
    assert isinstance(operation.params, ResizeParams)
    assert operation.params.size.width == 128


def test_build_crop_operation_with_anchor_from_bot_input() -> None:
    operation = build_operation("crop", MediaType.IMAGE, "128x128 top-left")

    assert isinstance(operation.params, CropParams)
    assert operation.params.anchor.value == "top-left"


def test_build_image_compress_operation_from_bot_input() -> None:
    operation = build_operation("compress", MediaType.IMAGE, "82")

    assert isinstance(operation.params, ImageCompressParams)
    assert operation.params.quality == 82


def test_build_video_compress_operation_from_bot_input() -> None:
    operation = build_operation("compress", MediaType.VIDEO, "23")

    assert isinstance(operation.params, VideoCompressParams)
    assert operation.params.crf == 23


def test_build_cut_operation_from_bot_input() -> None:
    operation = build_operation("cut", MediaType.VIDEO, "00:00:05 00:00:12")

    assert isinstance(operation.params, CutParams)
    assert operation.params.start_seconds == 5
    assert operation.params.end_seconds == 12


def test_build_fps_operation_from_bot_input() -> None:
    operation = build_operation("fps", MediaType.VIDEO, "24")

    assert isinstance(operation.params, FpsParams)
    assert operation.params.fps == 24


def test_build_strip_audio_operation_without_params() -> None:
    operation = build_operation("strip-audio", MediaType.VIDEO)

    assert isinstance(operation.params, StripAudioParams)


def test_build_operation_rejects_bad_input() -> None:
    with pytest.raises(InvalidOperation):
        build_operation("fps", MediaType.VIDEO, "fast")
