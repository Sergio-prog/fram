from fram.core.errors import InvalidOperation
from fram.core.operation_factories._utils import enum_value
from fram.core.operations import (
    Anchor,
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
