from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from fram.core.operation_factory import (
    adjust,
    auto_orient,
    background,
    blur,
    contact_sheet,
    convert,
    crop,
    cut,
    extract_audio,
    extract_frame,
    extract_subtitles,
    flip,
    fps,
    gif,
    grayscale,
    image_compress,
    mute_audio,
    resize,
    reverse,
    rotate,
    sharpen,
    speed,
    strip_audio,
    strip_metadata,
    thumbnail,
    upscale,
    video_compress,
    watermark,
)
from fram.core.operations import Operation


class ResizeSpec(BaseModel):
    name: Literal["resize"]
    size: str
    mode: str = "fit"

    def to_operation(self) -> Operation:
        return resize(self.size, self.mode)


class CropSpec(BaseModel):
    name: Literal["crop"]
    size: str
    anchor: str = "center"

    def to_operation(self) -> Operation:
        return crop(self.size, self.anchor)


class ImageCompressSpec(BaseModel):
    name: Literal["compress-image"]
    quality: int = 82
    optimize: bool = True

    def to_operation(self) -> Operation:
        return image_compress(self.quality, self.optimize)


class VideoCompressSpec(BaseModel):
    name: Literal["compress-video"]
    crf: int = 23
    preset: str = "medium"

    def to_operation(self) -> Operation:
        return video_compress(self.crf, self.preset)


class ConvertSpec(BaseModel):
    name: Literal["convert"]
    format: str

    def to_operation(self) -> Operation:
        return convert(self.format)


class FlipSpec(BaseModel):
    name: Literal["flip"]
    horizontal: bool = False
    vertical: bool = False

    def to_operation(self) -> Operation:
        return flip(self.horizontal, self.vertical)


class RotateSpec(BaseModel):
    name: Literal["rotate"]
    degrees: int

    def to_operation(self) -> Operation:
        return rotate(self.degrees)


class StripMetadataSpec(BaseModel):
    name: Literal["strip-metadata"]

    def to_operation(self) -> Operation:
        return strip_metadata()


class BlurSpec(BaseModel):
    name: Literal["blur"]
    radius: float = 2.0

    def to_operation(self) -> Operation:
        return blur(self.radius)


class GrayscaleSpec(BaseModel):
    name: Literal["grayscale"]

    def to_operation(self) -> Operation:
        return grayscale()


class AdjustSpec(BaseModel):
    name: Literal["adjust"]
    brightness: float = 1.0
    contrast: float = 1.0

    def to_operation(self) -> Operation:
        return adjust(self.brightness, self.contrast)


class SharpenSpec(BaseModel):
    name: Literal["sharpen"]
    factor: float = 2.0

    def to_operation(self) -> Operation:
        return sharpen(self.factor)


class WatermarkSpec(BaseModel):
    name: Literal["watermark"]
    text: str
    opacity: float = 0.75
    position: str = "bottom-right"
    size: int = 32

    def to_operation(self) -> Operation:
        return watermark(self.text, self.opacity, self.position, self.size)


class UpscaleSpec(BaseModel):
    name: Literal["upscale"]
    factor: float = 2.0

    def to_operation(self) -> Operation:
        return upscale(self.factor)


class AutoOrientSpec(BaseModel):
    name: Literal["auto-orient"]

    def to_operation(self) -> Operation:
        return auto_orient()


class BackgroundSpec(BaseModel):
    name: Literal["background"]
    color: str = "white"

    def to_operation(self) -> Operation:
        return background(self.color)


class CutSpec(BaseModel):
    name: Literal["cut"]
    start: str
    end: str | None = None
    duration: str | None = None

    def to_operation(self) -> Operation:
        return cut(self.start, self.end, self.duration)


class FpsSpec(BaseModel):
    name: Literal["fps"]
    fps: int

    def to_operation(self) -> Operation:
        return fps(self.fps)


class StripAudioSpec(BaseModel):
    name: Literal["strip-audio"]

    def to_operation(self) -> Operation:
        return strip_audio()


class ExtractAudioSpec(BaseModel):
    name: Literal["extract-audio"]

    def to_operation(self) -> Operation:
        return extract_audio()


class ExtractFrameSpec(BaseModel):
    name: Literal["extract-frame"]
    at: str

    def to_operation(self) -> Operation:
        return extract_frame(self.at)


class GifSpec(BaseModel):
    name: Literal["gif"]
    fps: int = 12
    width: int | None = None

    def to_operation(self) -> Operation:
        return gif(self.fps, self.width)


class SpeedSpec(BaseModel):
    name: Literal["speed"]
    factor: float

    def to_operation(self) -> Operation:
        return speed(self.factor)


class ReverseSpec(BaseModel):
    name: Literal["reverse"]
    include_audio: bool = True

    def to_operation(self) -> Operation:
        return reverse(self.include_audio)


class MuteAudioSpec(BaseModel):
    name: Literal["mute-audio"]

    def to_operation(self) -> Operation:
        return mute_audio()


class ThumbnailSpec(BaseModel):
    name: Literal["thumbnail"]
    at: str = "0"

    def to_operation(self) -> Operation:
        return thumbnail(self.at)


class ContactSheetSpec(BaseModel):
    name: Literal["contact-sheet"]
    columns: int = 3
    rows: int = 3
    width: int = 320

    def to_operation(self) -> Operation:
        return contact_sheet(self.columns, self.rows, self.width)


class ExtractSubtitlesSpec(BaseModel):
    name: Literal["extract-subtitles"]
    stream_index: int = 0

    def to_operation(self) -> Operation:
        return extract_subtitles(self.stream_index)


OperationSpec = Annotated[
    ResizeSpec
    | CropSpec
    | ImageCompressSpec
    | VideoCompressSpec
    | ConvertSpec
    | FlipSpec
    | RotateSpec
    | StripMetadataSpec
    | BlurSpec
    | GrayscaleSpec
    | AdjustSpec
    | SharpenSpec
    | WatermarkSpec
    | UpscaleSpec
    | AutoOrientSpec
    | BackgroundSpec
    | CutSpec
    | FpsSpec
    | StripAudioSpec
    | ExtractAudioSpec
    | ExtractFrameSpec
    | GifSpec
    | SpeedSpec
    | ReverseSpec
    | MuteAudioSpec
    | ThumbnailSpec
    | ContactSheetSpec
    | ExtractSubtitlesSpec,
    Field(discriminator="name"),
]

operation_specs_adapter = TypeAdapter(list[OperationSpec])


class ProcessResult(BaseModel):
    output_path: Path
