from fram.core.errors import InvalidOperation
from fram.core.operation_factories._utils import enum_value
from fram.core.operations import (
    AdjustParams,
    Anchor,
    AutoOrientParams,
    BackgroundParams,
    BlurParams,
    CropParams,
    FlipParams,
    GrayscaleParams,
    ImageCompressParams,
    Operation,
    OperationName,
    ResizeMode,
    ResizeParams,
    RotateParams,
    SharpenParams,
    UpscaleParams,
    WatermarkParams,
)
from fram.utils.sizes import parse_size


def resize(size: str, mode: str = "fit") -> Operation:
    return Operation(
        name=OperationName.RESIZE,
        params=ResizeParams(size=parse_size(size), mode=enum_value(ResizeMode, mode)),
    )


def crop(size: str, anchor: str = "center") -> Operation:
    return Operation(
        name=OperationName.CROP,
        params=CropParams(size=parse_size(size), anchor=enum_value(Anchor, anchor)),
    )


def image_compress(quality: int = 82, optimize: bool = True) -> Operation:
    return Operation(
        name=OperationName.COMPRESS,
        params=ImageCompressParams(quality=quality, optimize=optimize),
    )


def rotate(degrees: int) -> Operation:
    return Operation(name=OperationName.ROTATE, params=RotateParams(degrees=degrees))


def flip(horizontal: bool = False, vertical: bool = False) -> Operation:
    if not horizontal and not vertical:
        raise InvalidOperation("Choose horizontal, vertical, or both for flip.")
    return Operation(
        name=OperationName.FLIP,
        params=FlipParams(horizontal=horizontal, vertical=vertical),
    )


def blur(radius: float = 2.0) -> Operation:
    if radius < 0:
        raise InvalidOperation("Blur radius must be zero or greater.")
    return Operation(name=OperationName.BLUR, params=BlurParams(radius=radius))


def grayscale() -> Operation:
    return Operation(name=OperationName.GRAYSCALE, params=GrayscaleParams())


def adjust(brightness: float = 1.0, contrast: float = 1.0) -> Operation:
    if brightness < 0:
        raise InvalidOperation("Brightness must be zero or greater.")
    if contrast < 0:
        raise InvalidOperation("Contrast must be zero or greater.")
    return Operation(
        name=OperationName.ADJUST,
        params=AdjustParams(brightness=brightness, contrast=contrast),
    )


def sharpen(factor: float = 2.0) -> Operation:
    if factor < 0:
        raise InvalidOperation("Sharpen factor must be zero or greater.")
    return Operation(name=OperationName.SHARPEN, params=SharpenParams(factor=factor))


def watermark(
    text: str,
    opacity: float = 0.75,
    position: str = "bottom-right",
    size: int = 32,
) -> Operation:
    if not text:
        raise InvalidOperation("Watermark text cannot be empty.")
    if opacity < 0 or opacity > 1:
        raise InvalidOperation("Watermark opacity must be between 0 and 1.")
    if size <= 0:
        raise InvalidOperation("Watermark size must be greater than zero.")
    return Operation(
        name=OperationName.WATERMARK,
        params=WatermarkParams(
            text=text,
            opacity=opacity,
            position=enum_value(Anchor, position),
            size=size,
        ),
    )


def upscale(factor: float = 2.0) -> Operation:
    if factor <= 1:
        raise InvalidOperation("Upscale factor must be greater than 1.")
    return Operation(name=OperationName.UPSCALE, params=UpscaleParams(factor=factor))


def auto_orient() -> Operation:
    return Operation(name=OperationName.AUTO_ORIENT, params=AutoOrientParams())


def background(color: str = "white") -> Operation:
    if not color:
        raise InvalidOperation("Background color cannot be empty.")
    return Operation(name=OperationName.BACKGROUND, params=BackgroundParams(color=color))
