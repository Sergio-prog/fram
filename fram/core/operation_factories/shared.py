from fram.core.operations import ConvertParams, Operation, OperationName, StripMetadataParams


def convert(format_name: str) -> Operation:
    return Operation(name=OperationName.CONVERT, params=ConvertParams(format=format_name))


def strip_metadata() -> Operation:
    return Operation(name=OperationName.STRIP_METADATA, params=StripMetadataParams())
