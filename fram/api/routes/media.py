import json
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from fram.api.auth import require_token
from fram.api.schemas import ProcessResult, operation_specs_adapter
from fram.api.settings import settings
from fram.core.errors import FramError
from fram.core.media import get_media_info
from fram.core.operations import Operation
from fram.core.output import default_output_for_operations
from fram.core.pipeline import run_pipeline

router = APIRouter(dependencies=[Depends(require_token)])
UploadedFile = Annotated[UploadFile, File()]
OperationsForm = Annotated[str, Form()]
OutputSuffixForm = Annotated[str | None, Form()]


@router.post("/media/info")
async def media_info(file: UploadedFile) -> dict[str, object]:
    input_path = await _save_upload(file)
    try:
        info = get_media_info(input_path)
    except FramError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "media_type": info.media_type.value,
        "suffix": info.suffix,
        "size_bytes": info.size_bytes,
    }


@router.post("/media/process")
@router.post("/images/process")
@router.post("/videos/process")
async def process_media(
    file: UploadedFile,
    operations: OperationsForm = "[]",
    output_suffix: OutputSuffixForm = None,
) -> ProcessResult:
    input_path = await _save_upload(file)
    try:
        specs = operation_specs_adapter.validate_python(json.loads(operations))
        typed_operations = [spec.to_operation() for spec in specs]
        output_path = _output_path(input_path, output_suffix, typed_operations)
        result = run_pipeline(input_path, typed_operations, output_path)
    except (FramError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProcessResult(output_path=result)


async def _save_upload(file: UploadFile) -> Path:
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix
    path = settings.work_dir / f"{uuid4().hex}{suffix}"
    path.write_bytes(await file.read())
    return path


def _output_path(input_path: Path, output_suffix: str | None, operations: list[Operation]) -> Path:
    suffix = output_suffix
    if suffix is None:
        return default_output_for_operations(input_path, operations)
    if suffix and not suffix.startswith("."):
        suffix = f".{suffix}"
    return input_path.with_name(f"{input_path.stem}.out{suffix}")
