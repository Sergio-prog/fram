from pathlib import Path

from fram.core.metadata import collect_media_metadata
from fram.core.operation_factory import (
    adjust as adjust_operation,
)
from fram.core.operation_factory import (
    auto_orient as auto_orient_operation,
)
from fram.core.operation_factory import (
    background as background_operation,
)
from fram.core.operation_factory import (
    blur as blur_operation,
)
from fram.core.operation_factory import (
    contact_sheet as contact_sheet_operation,
)
from fram.core.operation_factory import (
    convert as convert_operation,
)
from fram.core.operation_factory import (
    crop as crop_operation,
)
from fram.core.operation_factory import (
    cut as cut_operation,
)
from fram.core.operation_factory import (
    extract_audio as extract_audio_operation,
)
from fram.core.operation_factory import (
    extract_frame as extract_frame_operation,
)
from fram.core.operation_factory import (
    extract_subtitles as extract_subtitles_operation,
)
from fram.core.operation_factory import (
    flip as flip_operation,
)
from fram.core.operation_factory import (
    fps as fps_operation,
)
from fram.core.operation_factory import (
    gif as gif_operation,
)
from fram.core.operation_factory import (
    grayscale as grayscale_operation,
)
from fram.core.operation_factory import (
    image_compress,
    video_compress,
)
from fram.core.operation_factory import (
    mute_audio as mute_audio_operation,
)
from fram.core.operation_factory import (
    resize as resize_operation,
)
from fram.core.operation_factory import (
    reverse as reverse_operation,
)
from fram.core.operation_factory import (
    rotate as rotate_operation,
)
from fram.core.operation_factory import (
    sharpen as sharpen_operation,
)
from fram.core.operation_factory import (
    speed as speed_operation,
)
from fram.core.operation_factory import (
    strip_audio as strip_audio_operation,
)
from fram.core.operation_factory import (
    strip_metadata as strip_metadata_operation,
)
from fram.core.operation_factory import (
    thumbnail as thumbnail_operation,
)
from fram.core.operation_factory import (
    upscale as upscale_operation,
)
from fram.core.operation_factory import (
    watermark as watermark_operation,
)
from fram.core.output import default_output_for_operations
from fram.core.pipeline import run_pipeline
from fram.utils.files import default_output_path


def media_info(path: Path) -> str:
    return collect_media_metadata(path).as_text()


def resize_file(input_path: Path, size: str, mode: str, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [resize_operation(size, mode)], output)


def crop_file(input_path: Path, size: str, anchor: str, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [crop_operation(size, anchor)], output)


def compress_image_file(input_path: Path, quality: int, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [image_compress(quality=quality)], output)


def compress_video_file(input_path: Path, crf: int, preset: str, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [video_compress(crf=crf, preset=preset)], output)


def convert_file(input_path: Path, format_name: str, output_path: Path | None) -> Path:
    suffix = f".{format_name.lower().lstrip('.')}"
    output = output_path or default_output_path(input_path, suffix=suffix)
    return run_pipeline(input_path, [convert_operation(format_name)], output)


def rotate_file(input_path: Path, degrees: int, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [rotate_operation(degrees)], output)


def flip_file(
    input_path: Path,
    horizontal: bool,
    vertical: bool,
    output_path: Path | None,
) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [flip_operation(horizontal, vertical)], output)


def strip_metadata_file(input_path: Path, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [strip_metadata_operation()], output)


def blur_file(input_path: Path, radius: float, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [blur_operation(radius)], output)


def grayscale_file(input_path: Path, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [grayscale_operation()], output)


def adjust_file(
    input_path: Path,
    brightness: float,
    contrast: float,
    output_path: Path | None,
) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [adjust_operation(brightness, contrast)], output)


def sharpen_file(input_path: Path, factor: float, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [sharpen_operation(factor)], output)


def watermark_file(
    input_path: Path,
    text: str,
    opacity: float,
    position: str,
    size: int,
    output_path: Path | None,
) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(
        input_path,
        [watermark_operation(text, opacity=opacity, position=position, size=size)],
        output,
    )


def upscale_file(input_path: Path, factor: float, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [upscale_operation(factor)], output)


def auto_orient_file(input_path: Path, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [auto_orient_operation()], output)


def background_file(input_path: Path, color: str, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [background_operation(color)], output)


def cut_video_file(
    input_path: Path,
    start: str,
    end: str | None,
    duration: str | None,
    output_path: Path | None,
) -> Path:
    output = output_path or default_output_path(input_path)
    operation = cut_operation(start=start, end=end, duration=duration)
    return run_pipeline(input_path, [operation], output)


def fps_video_file(input_path: Path, value: int, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [fps_operation(value)], output)


def strip_audio_file(input_path: Path, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [strip_audio_operation()], output)


def extract_audio_file(input_path: Path, output_path: Path | None) -> Path:
    operation = extract_audio_operation()
    output = output_path or default_output_for_operations(input_path, [operation])
    return run_pipeline(input_path, [operation], output)


def extract_frame_file(input_path: Path, at: str, output_path: Path | None) -> Path:
    output = output_path or input_path.with_name(f"{input_path.stem}.frame.png")
    return run_pipeline(input_path, [extract_frame_operation(at)], output)


def gif_file(input_path: Path, fps: int, width: int | None, output_path: Path | None) -> Path:
    operation = gif_operation(fps, width)
    output = output_path or default_output_for_operations(input_path, [operation])
    return run_pipeline(input_path, [operation], output)


def speed_video_file(input_path: Path, factor: float, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [speed_operation(factor)], output)


def reverse_video_file(input_path: Path, include_audio: bool, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [reverse_operation(include_audio)], output)


def mute_audio_file(input_path: Path, output_path: Path | None) -> Path:
    output = output_path or default_output_path(input_path)
    return run_pipeline(input_path, [mute_audio_operation()], output)


def thumbnail_file(input_path: Path, at: str, output_path: Path | None) -> Path:
    operation = thumbnail_operation(at)
    output = output_path or default_output_for_operations(input_path, [operation])
    return run_pipeline(input_path, [operation], output)


def contact_sheet_file(
    input_path: Path,
    columns: int,
    rows: int,
    width: int,
    output_path: Path | None,
) -> Path:
    operation = contact_sheet_operation(columns, rows, width)
    output = output_path or default_output_for_operations(input_path, [operation])
    return run_pipeline(input_path, [operation], output)


def extract_subtitles_file(
    input_path: Path,
    stream_index: int,
    output_path: Path | None,
) -> Path:
    operation = extract_subtitles_operation(stream_index)
    output = output_path or default_output_for_operations(input_path, [operation])
    return run_pipeline(input_path, [operation], output)
