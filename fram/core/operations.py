from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from fram.utils.sizes import Size


class ResizeMode(StrEnum):
    FIT = "fit"
    FILL = "fill"
    EXACT = "exact"


class Anchor(StrEnum):
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top-left"
    TOP_RIGHT = "top-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_RIGHT = "bottom-right"


class OperationName(StrEnum):
    RESIZE = "resize"
    CROP = "crop"
    COMPRESS = "compress"
    CONVERT = "convert"
    ROTATE = "rotate"
    FLIP = "flip"
    STRIP_METADATA = "strip-metadata"
    CUT = "cut"
    FPS = "fps"
    STRIP_AUDIO = "strip-audio"
    EXTRACT_FRAME = "extract-frame"


@dataclass(frozen=True)
class ResizeParams:
    size: Size
    mode: ResizeMode = ResizeMode.FIT


@dataclass(frozen=True)
class CropParams:
    size: Size
    anchor: Anchor = Anchor.CENTER


@dataclass(frozen=True)
class ImageCompressParams:
    quality: int = 82
    optimize: bool = True


@dataclass(frozen=True)
class ConvertParams:
    format: str


@dataclass(frozen=True)
class RotateParams:
    degrees: int


@dataclass(frozen=True)
class FlipParams:
    horizontal: bool = False
    vertical: bool = False


@dataclass(frozen=True)
class StripMetadataParams:
    enabled: bool = True


@dataclass(frozen=True)
class CutParams:
    start_seconds: float
    end_seconds: float | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True)
class VideoCompressParams:
    crf: int = 23
    preset: str = "medium"


@dataclass(frozen=True)
class FpsParams:
    fps: int


@dataclass(frozen=True)
class StripAudioParams:
    enabled: bool = True


@dataclass(frozen=True)
class ExtractFrameParams:
    at_seconds: float


OperationParams: TypeAlias = (
    ResizeParams
    | CropParams
    | ImageCompressParams
    | ConvertParams
    | RotateParams
    | FlipParams
    | StripMetadataParams
    | CutParams
    | VideoCompressParams
    | FpsParams
    | StripAudioParams
    | ExtractFrameParams
)


@dataclass(frozen=True)
class Operation:
    name: OperationName
    params: OperationParams

