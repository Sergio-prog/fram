from pathlib import Path

from fram.core.operations import ConvertParams, Operation, OperationName
from fram.utils.files import default_output_path

OPERATION_OUTPUT_SUFFIXES = {
    OperationName.EXTRACT_FRAME: ".png",
    OperationName.EXTRACT_AUDIO: ".m4a",
    OperationName.GIF: ".gif",
    OperationName.THUMBNAIL: ".png",
    OperationName.CONTACT_SHEET: ".png",
    OperationName.EXTRACT_SUBTITLES: ".srt",
}


def default_output_for_operations(input_path: Path, operations: list[Operation]) -> Path:
    suffix = None
    if operations:
        last_operation = operations[-1]
        suffix = OPERATION_OUTPUT_SUFFIXES.get(last_operation.name)
        if last_operation.name == OperationName.CONVERT:
            params = last_operation.params
            if isinstance(params, ConvertParams):
                suffix = f".{params.format.lower().lstrip('.')}"
    return default_output_path(input_path, suffix=suffix)
