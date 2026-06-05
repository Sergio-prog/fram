from dataclasses import dataclass, field
from pathlib import Path

from fram.core.errors import InvalidOperation
from fram.core.operations import (
    BlurParams,
    ContactSheetParams,
    ConvertParams,
    CropParams,
    CutParams,
    ExtractAudioParams,
    ExtractFrameParams,
    ExtractSubtitlesParams,
    FlipParams,
    FpsParams,
    GifParams,
    GrayscaleParams,
    MuteAudioParams,
    Operation,
    OperationName,
    ResizeParams,
    ReverseParams,
    RotateParams,
    SpeedParams,
    StripAudioParams,
    StripMetadataParams,
    ThumbnailParams,
    VideoCompressParams,
)
from fram.core.processors.base import MediaProcessor
from fram.utils.files import ensure_parent_dir
from fram.utils.process import run_command


@dataclass
class VideoCommandPlan:
    input_args: list[str] = field(default_factory=list)
    video_filters: list[str] = field(default_factory=list)
    audio_filters: list[str] = field(default_factory=list)
    output_args: list[str] = field(default_factory=list)
    disable_video: bool = False
    disable_audio: bool = False

    def to_args(self, input_path: Path, output_path: Path) -> list[str]:
        args = ["ffmpeg", "-y", *self.input_args, "-i", str(input_path)]
        if self.video_filters and not self.disable_video:
            args.extend(["-vf", ",".join(self.video_filters)])
        if self.audio_filters and not self.disable_audio:
            args.extend(["-af", ",".join(self.audio_filters)])
        if self.disable_video:
            args.append("-vn")
        if self.disable_audio:
            args.append("-an")
        args.extend(self.output_args)
        args.append(str(output_path))
        return args


class VideoProcessor(MediaProcessor):
    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        ensure_parent_dir(output_path)
        plan = VideoCommandPlan()

        for operation in operations:
            self.apply(operation, plan)

        run_command(plan.to_args(input_path, output_path))
        return output_path

    def apply(
        self,
        operation: Operation,
        plan: VideoCommandPlan,
    ) -> None:
        match operation.name:
            case OperationName.CUT:
                params = self.expect(operation.params, CutParams)
                plan.input_args.extend(["-ss", str(params.start_seconds)])
                if params.end_seconds is not None:
                    plan.output_args.extend(["-to", str(params.end_seconds)])
                if params.duration_seconds is not None:
                    plan.output_args.extend(["-t", str(params.duration_seconds)])
            case OperationName.RESIZE:
                params = self.expect(operation.params, ResizeParams)
                plan.video_filters.append(f"scale={params.size.width}:{params.size.height}")
            case OperationName.CROP:
                params = self.expect(operation.params, CropParams)
                plan.video_filters.append(f"crop={params.size.width}:{params.size.height}")
            case OperationName.FPS:
                params = self.expect(operation.params, FpsParams)
                if params.fps <= 0:
                    raise InvalidOperation("FPS must be greater than zero.")
                plan.video_filters.append(f"fps={params.fps}")
            case OperationName.COMPRESS:
                params = self.expect(operation.params, VideoCompressParams)
                if params.crf < 0 or params.crf > 51:
                    raise InvalidOperation("CRF must be between 0 and 51.")
                plan.output_args.extend(["-crf", str(params.crf), "-preset", params.preset])
            case OperationName.CONVERT:
                self.expect(operation.params, ConvertParams)
            case OperationName.STRIP_METADATA:
                self.expect(operation.params, StripMetadataParams)
                plan.output_args.extend(["-map_metadata", "-1", "-map_chapters", "-1"])
            case OperationName.BLUR:
                params = self.expect(operation.params, BlurParams)
                plan.video_filters.append(f"boxblur={params.radius:g}:1")
            case OperationName.GRAYSCALE:
                self.expect(operation.params, GrayscaleParams)
                plan.video_filters.append("hue=s=0")
            case OperationName.ROTATE:
                params = self.expect(operation.params, RotateParams)
                plan.video_filters.append(self.rotate_filter(params.degrees))
            case OperationName.FLIP:
                params = self.expect(operation.params, FlipParams)
                if params.horizontal:
                    plan.video_filters.append("hflip")
                if params.vertical:
                    plan.video_filters.append("vflip")
            case OperationName.STRIP_AUDIO:
                self.expect(operation.params, StripAudioParams)
                plan.disable_audio = True
            case OperationName.MUTE_AUDIO:
                self.expect(operation.params, MuteAudioParams)
                plan.audio_filters.append("volume=0")
            case OperationName.EXTRACT_AUDIO:
                self.expect(operation.params, ExtractAudioParams)
                plan.disable_video = True
            case OperationName.EXTRACT_FRAME:
                params = self.expect(operation.params, ExtractFrameParams)
                plan.input_args.extend(["-ss", str(params.at_seconds)])
                plan.output_args.extend(["-frames:v", "1"])
            case OperationName.THUMBNAIL:
                params = self.expect(operation.params, ThumbnailParams)
                plan.input_args.extend(["-ss", str(params.at_seconds)])
                plan.output_args.extend(["-frames:v", "1"])
                plan.disable_audio = True
            case OperationName.CONTACT_SHEET:
                params = self.expect(operation.params, ContactSheetParams)
                frame_count = params.columns * params.rows
                plan.video_filters.extend(
                    [
                        f"select='not(mod(n\\,{frame_count}))'",
                        f"scale={params.width}:-1:flags=lanczos",
                        f"tile={params.columns}x{params.rows}",
                    ]
                )
                plan.output_args.extend(["-frames:v", "1"])
                plan.disable_audio = True
            case OperationName.EXTRACT_SUBTITLES:
                params = self.expect(operation.params, ExtractSubtitlesParams)
                plan.output_args.extend(["-map", f"0:s:{params.stream_index}"])
                plan.disable_video = True
                plan.disable_audio = True
            case OperationName.GIF:
                params = self.expect(operation.params, GifParams)
                if params.fps <= 0:
                    raise InvalidOperation("GIF FPS must be greater than zero.")
                plan.video_filters.append(f"fps={params.fps}")
                if params.width is not None:
                    if params.width <= 0:
                        raise InvalidOperation("GIF width must be greater than zero.")
                    plan.video_filters.append(f"scale={params.width}:-1:flags=lanczos")
                plan.disable_audio = True
                plan.output_args.extend(["-loop", "0"])
            case OperationName.SPEED:
                params = self.expect(operation.params, SpeedParams)
                if params.factor <= 0:
                    raise InvalidOperation("Speed factor must be greater than zero.")
                plan.video_filters.append(f"setpts=PTS/{params.factor:g}")
                plan.audio_filters.extend(self.atempo_filters(params.factor))
            case OperationName.REVERSE:
                params = self.expect(operation.params, ReverseParams)
                plan.video_filters.append("reverse")
                if params.include_audio:
                    plan.audio_filters.append("areverse")
            case _:
                raise InvalidOperation(f"Operation {operation.name} is not valid for videos.")

    def atempo_filters(self, factor: float) -> list[str]:
        filters: list[str] = []
        remaining = factor
        while remaining > 2:
            filters.append("atempo=2")
            remaining /= 2
        while remaining < 0.5:
            filters.append("atempo=0.5")
            remaining /= 0.5
        filters.append(f"atempo={remaining:g}")
        return filters

    def rotate_filter(self, degrees: int) -> str:
        normalized = degrees % 360
        if normalized == 0:
            return "null"
        if normalized == 90:
            return "transpose=1"
        if normalized == 180:
            return "hflip,vflip"
        if normalized == 270:
            return "transpose=2"
        radians = f"{degrees:g}*PI/180"
        return f"rotate={radians}:ow=rotw({radians}):oh=roth({radians})"
