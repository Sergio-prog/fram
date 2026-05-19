from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from fram.core.operation_models.image import (
    BlurParams,
    CropParams,
    FlipParams,
    GrayscaleParams,
    ImageCompressParams,
    ResizeParams,
    RotateParams,
)
from fram.core.operation_models.shared import ConvertParams, StripMetadataParams
from fram.core.operation_models.video import (
    CutParams,
    ExtractAudioParams,
    ExtractFrameParams,
    FpsParams,
    GifParams,
    ReverseParams,
    SpeedParams,
    StripAudioParams,
    VideoCompressParams,
)


class OperationName(StrEnum):
    RESIZE = "resize"
    CROP = "crop"
    COMPRESS = "compress"
    CONVERT = "convert"
    ROTATE = "rotate"
    FLIP = "flip"
    STRIP_METADATA = "strip-metadata"
    BLUR = "blur"
    GRAYSCALE = "grayscale"
    CUT = "cut"
    FPS = "fps"
    STRIP_AUDIO = "strip-audio"
    EXTRACT_AUDIO = "extract-audio"
    EXTRACT_FRAME = "extract-frame"
    GIF = "gif"
    SPEED = "speed"
    REVERSE = "reverse"


OperationParams: TypeAlias = (
    ResizeParams
    | CropParams
    | ImageCompressParams
    | ConvertParams
    | RotateParams
    | FlipParams
    | StripMetadataParams
    | BlurParams
    | GrayscaleParams
    | CutParams
    | VideoCompressParams
    | FpsParams
    | StripAudioParams
    | ExtractAudioParams
    | ExtractFrameParams
    | GifParams
    | SpeedParams
    | ReverseParams
)


@dataclass(frozen=True)
class Operation:
    name: OperationName
    params: OperationParams
