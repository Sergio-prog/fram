from dataclasses import dataclass
from enum import StrEnum

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
class RotateParams:
    degrees: int


@dataclass(frozen=True)
class FlipParams:
    horizontal: bool = False
    vertical: bool = False


@dataclass(frozen=True)
class BlurParams:
    radius: float = 2.0


@dataclass(frozen=True)
class GrayscaleParams:
    enabled: bool = True
