from pathlib import Path

from fram.core.operations import Operation
from fram.core.pipeline import run_pipeline
from fram.utils.files import default_output_path


def process_for_user(input_path: Path, operations: list[Operation]) -> Path:
    return run_pipeline(input_path, operations, default_output_path(input_path))
