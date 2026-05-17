from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, Field, TypeAdapter

from fram.core.operation_factory import (
    convert,
    crop,
    cut,
    extract_frame,
    flip,
    fps,
    image_compress,
    resize,
    strip_audio,
    video_compress,
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


class ExtractFrameSpec(BaseModel):
    name: Literal["extract-frame"]
    at: str

    def to_operation(self) -> Operation:
        return extract_frame(self.at)


OperationSpec = Annotated[
    ResizeSpec
    | CropSpec
    | ImageCompressSpec
    | VideoCompressSpec
    | ConvertSpec
    | FlipSpec
    | CutSpec
    | FpsSpec
    | StripAudioSpec
    | ExtractFrameSpec,
    Field(discriminator="name"),
]

operation_specs_adapter = TypeAdapter(list[OperationSpec])


class ProcessResult(BaseModel):
    output_path: Path

