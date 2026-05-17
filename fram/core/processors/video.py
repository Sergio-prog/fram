from pathlib import Path

from fram.core.errors import InvalidOperation
from fram.core.operations import (
    ConvertParams,
    CropParams,
    CutParams,
    ExtractFrameParams,
    FpsParams,
    Operation,
    OperationName,
    ResizeParams,
    StripAudioParams,
    VideoCompressParams,
)
from fram.core.processors.base import MediaProcessor
from fram.utils.files import ensure_parent_dir
from fram.utils.process import run_command


class VideoProcessor(MediaProcessor):
    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        ensure_parent_dir(output_path)
        args = ["ffmpeg", "-y"]
        filters: list[str] = []
        output_args: list[str] = []
        input_args: list[str] = []

        for operation in operations:
            self.apply(operation, input_args, filters, output_args)

        args.extend(input_args)
        args.extend(["-i", str(input_path)])
        if filters:
            args.extend(["-vf", ",".join(filters)])
        args.extend(output_args)
        args.append(str(output_path))

        run_command(args)
        return output_path

    def apply(
        self,
        operation: Operation,
        input_args: list[str],
        filters: list[str],
        output_args: list[str],
    ) -> None:
        match operation.name:
            case OperationName.CUT:
                params = self.expect(operation.params, CutParams)
                input_args.extend(["-ss", str(params.start_seconds)])
                if params.end_seconds is not None:
                    output_args.extend(["-to", str(params.end_seconds)])
                if params.duration_seconds is not None:
                    output_args.extend(["-t", str(params.duration_seconds)])
            case OperationName.RESIZE:
                params = self.expect(operation.params, ResizeParams)
                filters.append(f"scale={params.size.width}:{params.size.height}")
            case OperationName.CROP:
                params = self.expect(operation.params, CropParams)
                filters.append(f"crop={params.size.width}:{params.size.height}")
            case OperationName.FPS:
                params = self.expect(operation.params, FpsParams)
                if params.fps <= 0:
                    raise InvalidOperation("FPS must be greater than zero.")
                filters.append(f"fps={params.fps}")
            case OperationName.COMPRESS:
                params = self.expect(operation.params, VideoCompressParams)
                if params.crf < 0 or params.crf > 51:
                    raise InvalidOperation("CRF must be between 0 and 51.")
                output_args.extend(["-crf", str(params.crf), "-preset", params.preset])
            case OperationName.CONVERT:
                self.expect(operation.params, ConvertParams)
            case OperationName.STRIP_AUDIO:
                self.expect(operation.params, StripAudioParams)
                output_args.append("-an")
            case OperationName.EXTRACT_FRAME:
                params = self.expect(operation.params, ExtractFrameParams)
                input_args.extend(["-ss", str(params.at_seconds)])
                output_args.extend(["-frames:v", "1"])
            case _:
                raise InvalidOperation(f"Operation {operation.name} is not valid for videos.")

