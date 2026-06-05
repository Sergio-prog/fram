from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from fram.core.operation_models.image import (
    AdjustParams,
    AutoOrientParams,
    BackgroundParams,
    BlurParams,
    CropParams,
    FlipParams,
    GrayscaleParams,
    ImageCompressParams,
    ResizeParams,
    RotateParams,
    SharpenParams,
    UpscaleParams,
    WatermarkParams,
)
from fram.core.operation_models.shared import ConvertParams, StripMetadataParams
from fram.core.operation_models.video import (
    ContactSheetParams,
    CutParams,
    ExtractAudioParams,
    ExtractFrameParams,
    ExtractSubtitlesParams,
    FpsParams,
    GifParams,
    MuteAudioParams,
    ReverseParams,
    SpeedParams,
    StripAudioParams,
    ThumbnailParams,
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
    ADJUST = "adjust"
    SHARPEN = "sharpen"
    WATERMARK = "watermark"
    UPSCALE = "upscale"
    AUTO_ORIENT = "auto-orient"
    BACKGROUND = "background"
    CUT = "cut"
    FPS = "fps"
    STRIP_AUDIO = "strip-audio"
    EXTRACT_AUDIO = "extract-audio"
    EXTRACT_FRAME = "extract-frame"
    GIF = "gif"
    SPEED = "speed"
    REVERSE = "reverse"
    MUTE_AUDIO = "mute-audio"
    THUMBNAIL = "thumbnail"
    CONTACT_SHEET = "contact-sheet"
    EXTRACT_SUBTITLES = "extract-subtitles"


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
    | AdjustParams
    | SharpenParams
    | WatermarkParams
    | UpscaleParams
    | AutoOrientParams
    | BackgroundParams
    | CutParams
    | VideoCompressParams
    | FpsParams
    | StripAudioParams
    | ExtractAudioParams
    | ExtractFrameParams
    | GifParams
    | SpeedParams
    | ReverseParams
    | MuteAudioParams
    | ThumbnailParams
    | ContactSheetParams
    | ExtractSubtitlesParams
)


@dataclass(frozen=True)
class Operation:
    name: OperationName
    params: OperationParams
