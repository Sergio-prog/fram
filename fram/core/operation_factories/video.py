from fram.core.errors import InvalidOperation
from fram.core.operations import (
    ContactSheetParams,
    CutParams,
    ExtractAudioParams,
    ExtractFrameParams,
    ExtractSubtitlesParams,
    FpsParams,
    GifParams,
    MuteAudioParams,
    Operation,
    OperationName,
    ReverseParams,
    SpeedParams,
    StripAudioParams,
    ThumbnailParams,
    VideoCompressParams,
)
from fram.utils.timecodes import parse_timecode


def video_compress(crf: int = 23, preset: str = "medium") -> Operation:
    return Operation(
        name=OperationName.COMPRESS,
        params=VideoCompressParams(crf=crf, preset=preset),
    )


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


def extract_audio() -> Operation:
    return Operation(name=OperationName.EXTRACT_AUDIO, params=ExtractAudioParams())


def extract_frame(at: str) -> Operation:
    return Operation(
        name=OperationName.EXTRACT_FRAME,
        params=ExtractFrameParams(at_seconds=parse_timecode(at)),
    )


def gif(fps_value: int = 12, width: int | None = None) -> Operation:
    if fps_value <= 0:
        raise InvalidOperation("GIF FPS must be greater than zero.")
    if width is not None and width <= 0:
        raise InvalidOperation("GIF width must be greater than zero.")
    return Operation(name=OperationName.GIF, params=GifParams(fps=fps_value, width=width))


def speed(factor: float) -> Operation:
    if factor <= 0:
        raise InvalidOperation("Speed factor must be greater than zero.")
    return Operation(name=OperationName.SPEED, params=SpeedParams(factor=factor))


def reverse(include_audio: bool = True) -> Operation:
    return Operation(name=OperationName.REVERSE, params=ReverseParams(include_audio=include_audio))


def mute_audio() -> Operation:
    return Operation(name=OperationName.MUTE_AUDIO, params=MuteAudioParams())


def thumbnail(at: str = "0") -> Operation:
    return Operation(
        name=OperationName.THUMBNAIL,
        params=ThumbnailParams(at_seconds=parse_timecode(at)),
    )


def contact_sheet(columns: int = 3, rows: int = 3, width: int = 320) -> Operation:
    if columns <= 0 or rows <= 0:
        raise InvalidOperation("Contact sheet columns and rows must be greater than zero.")
    if width <= 0:
        raise InvalidOperation("Contact sheet width must be greater than zero.")
    return Operation(
        name=OperationName.CONTACT_SHEET,
        params=ContactSheetParams(columns=columns, rows=rows, width=width),
    )


def extract_subtitles(stream_index: int = 0) -> Operation:
    if stream_index < 0:
        raise InvalidOperation("Subtitle stream index must be zero or greater.")
    return Operation(
        name=OperationName.EXTRACT_SUBTITLES,
        params=ExtractSubtitlesParams(stream_index=stream_index),
    )
