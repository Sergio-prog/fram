from pathlib import Path

from fram.core.operations import Operation
from fram.core.output import default_output_for_operations
from fram.core.pipeline import run_pipeline


def process_for_user(input_path: Path, operations: list[Operation]) -> Path:
    output_path = default_output_for_operations(input_path, operations)
    return run_pipeline(input_path, operations, output_path)
