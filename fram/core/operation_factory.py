from enum import Enum
from typing import TypeVar

from fram.core.errors import InvalidOperation
from fram.core.operations import (
    Anchor,
    ConvertParams,
    CropParams,
    CutParams,
    ExtractFrameParams,
    FlipParams,
    FpsParams,
    ImageCompressParams,
    Operation,
    OperationName,
    ResizeMode,
    ResizeParams,
    RotateParams,
    StripAudioParams,
    StripMetadataParams,
    VideoCompressParams,
)
from fram.utils.sizes import parse_size
from fram.utils.timecodes import parse_timecode

EnumT = TypeVar("EnumT", bound=Enum)


def resize(size: str, mode: str = "fit") -> Operation:
    return Operation(
        name=OperationName.RESIZE,
        params=ResizeParams(size=parse_size(size), mode=_enum_value(ResizeMode, mode)),
    )


def crop(size: str, anchor: str = "center") -> Operation:
    return Operation(
        name=OperationName.CROP,
        params=CropParams(size=parse_size(size), anchor=_enum_value(Anchor, anchor)),
    )


def image_compress(quality: int = 82, optimize: bool = True) -> Operation:
    return Operation(
        name=OperationName.COMPRESS,
        params=ImageCompressParams(quality=quality, optimize=optimize),
    )


def video_compress(crf: int = 23, preset: str = "medium") -> Operation:
    return Operation(
        name=OperationName.COMPRESS,
        params=VideoCompressParams(crf=crf, preset=preset),
    )


def convert(format_name: str) -> Operation:
    return Operation(name=OperationName.CONVERT, params=ConvertParams(format=format_name))


def rotate(degrees: int) -> Operation:
    return Operation(name=OperationName.ROTATE, params=RotateParams(degrees=degrees))


def flip(horizontal: bool = False, vertical: bool = False) -> Operation:
    if not horizontal and not vertical:
        raise InvalidOperation("Choose horizontal, vertical, or both for flip.")
    return Operation(
        name=OperationName.FLIP,
        params=FlipParams(horizontal=horizontal, vertical=vertical),
    )


def strip_metadata() -> Operation:
    return Operation(name=OperationName.STRIP_METADATA, params=StripMetadataParams())


def cut(start: str, end: str | None = None, duration: str | None = None) -> Operation:
    if end is not None and duration is not None:
        raise InvalidOperation("Use either end or duration, not both.")

    return Operation(
        name=OperationName.CUT,
        params=CutParams(
            start_seconds=parse_timecode(start),
            end_seconds=parse_timecode(end) if end else None,
            duration_seconds=parse_timecode(duration) if duration else None,
        ),
    )


def fps(value: int) -> Operation:
    return Operation(name=OperationName.FPS, params=FpsParams(fps=value))


def strip_audio() -> Operation:
    return Operation(name=OperationName.STRIP_AUDIO, params=StripAudioParams())


def extract_frame(at: str) -> Operation:
    return Operation(
        name=OperationName.EXTRACT_FRAME,
        params=ExtractFrameParams(at_seconds=parse_timecode(at)),
    )


def _enum_value(enum_type: type[EnumT], value: str) -> EnumT:
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise InvalidOperation(f"Invalid value '{value}'. Allowed: {allowed}.") from exc
