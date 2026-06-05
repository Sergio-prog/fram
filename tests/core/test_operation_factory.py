import pytest

from fram.core.errors import InvalidOperation
from fram.core.operation_factory import (
    adjust,
    background,
    blur,
    contact_sheet,
    crop,
    cut,
    flip,
    fps,
    gif,
    grayscale,
    resize,
    reverse,
    sharpen,
    speed,
    strip_metadata,
    thumbnail,
    upscale,
    watermark,
)
from fram.core.operations import (
    AdjustParams,
    Anchor,
    BackgroundParams,
    ContactSheetParams,
    CropParams,
    CutParams,
    FlipParams,
    FpsParams,
    OperationName,
    ResizeMode,
    ResizeParams,
    SharpenParams,
    StripMetadataParams,
    ThumbnailParams,
    UpscaleParams,
    WatermarkParams,
)


def test_resize_builds_typed_operation() -> None:
    operation = resize("320x240", mode="fill")

    assert operation.name == OperationName.RESIZE
    assert isinstance(operation.params, ResizeParams)
    assert operation.params.size.width == 320
    assert operation.params.size.height == 240
    assert operation.params.mode == ResizeMode.FILL


def test_crop_builds_typed_operation() -> None:
    operation = crop("128x128", anchor="top-left")

    assert operation.name == OperationName.CROP
    assert isinstance(operation.params, CropParams)
    assert operation.params.anchor == Anchor.TOP_LEFT


def test_cut_accepts_end_or_duration_but_not_both() -> None:
    operation = cut(start="00:05", end="00:10")

    assert operation.name == OperationName.CUT
    assert isinstance(operation.params, CutParams)
    assert operation.params.start_seconds == 5
    assert operation.params.end_seconds == 10
    assert operation.params.duration_seconds is None

    with pytest.raises(InvalidOperation, match="either end or duration"):
        cut(start="1", end="2", duration="3")


def test_flip_requires_direction() -> None:
    with pytest.raises(InvalidOperation, match="Choose horizontal"):
        flip()

    operation = flip(horizontal=True)
    assert isinstance(operation.params, FlipParams)
    assert operation.params.horizontal is True
    assert operation.params.vertical is False


def test_fps_builds_typed_operation_without_validating_processing_rules() -> None:
    operation = fps(24)

    assert operation.name == OperationName.FPS
    assert isinstance(operation.params, FpsParams)
    assert operation.params.fps == 24


def test_invalid_enum_values_are_user_facing_errors() -> None:
    with pytest.raises(InvalidOperation, match="Allowed"):
        resize("100x100", mode="stretch")


def test_strip_metadata_uses_image_metadata_params() -> None:
    operation = strip_metadata()

    assert operation.name == OperationName.STRIP_METADATA
    assert isinstance(operation.params, StripMetadataParams)


def test_visual_effect_operations_build_typed_params() -> None:
    assert blur(3).name == OperationName.BLUR
    assert grayscale().name == OperationName.GRAYSCALE

    adjust_operation = adjust(1.1, 1.2)
    watermark_operation = watermark("FRAM", position="bottom-right")

    assert isinstance(adjust_operation.params, AdjustParams)
    assert isinstance(sharpen(2).params, SharpenParams)
    assert isinstance(watermark_operation.params, WatermarkParams)
    assert watermark_operation.params.position == Anchor.BOTTOM_RIGHT
    assert isinstance(upscale(2).params, UpscaleParams)
    assert isinstance(background("white").params, BackgroundParams)


def test_video_utility_operations_build_typed_params() -> None:
    assert gif(fps_value=12, width=480).name == OperationName.GIF
    assert speed(2).name == OperationName.SPEED
    assert reverse().name == OperationName.REVERSE
    assert isinstance(thumbnail("5").params, ThumbnailParams)
    assert isinstance(contact_sheet(3, 3, 320).params, ContactSheetParams)

    with pytest.raises(InvalidOperation, match="greater than zero"):
        speed(0)
