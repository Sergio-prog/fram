import pytest

from fram.core.errors import InvalidOperation
from fram.core.media import MediaType
from fram.core.operations import (
    CropParams,
    ImageCompressParams,
    OperationName,
    VideoCompressParams,
)
from fram.core.text_operations import build_operation, parse_chain


def test_parse_chain_returns_operations_in_order() -> None:
    operations = parse_chain(["resize 64x64", "grayscale", "convert webp"], MediaType.IMAGE)

    assert len(operations) == 3
    assert operations[0].name == OperationName.RESIZE
    assert operations[1].name == OperationName.GRAYSCALE
    assert operations[2].name == OperationName.CONVERT


def test_build_operation_compress_image() -> None:
    operation = build_operation("compress", MediaType.IMAGE, "80")

    assert isinstance(operation.params, ImageCompressParams)
    assert operation.params.quality == 80


def test_build_operation_compress_video() -> None:
    operation = build_operation("compress", MediaType.VIDEO, "26")

    assert isinstance(operation.params, VideoCompressParams)
    assert operation.params.crf == 26


def test_build_operation_crop_with_anchor() -> None:
    operation = build_operation("crop", MediaType.IMAGE, "128x128 top-left")

    assert isinstance(operation.params, CropParams)
    assert operation.params.anchor.value == "top-left"


def test_parse_chain_empty_raises() -> None:
    with pytest.raises(InvalidOperation):
        parse_chain([], MediaType.IMAGE)


def test_build_operation_fps_invalid_raises() -> None:
    with pytest.raises(InvalidOperation):
        build_operation("fps", MediaType.VIDEO, "fast")


def test_build_operation_unknown_action_raises() -> None:
    with pytest.raises(InvalidOperation):
        build_operation("nonsense", MediaType.IMAGE)
