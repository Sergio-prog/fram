from pathlib import Path

from fram.core.media import MediaType, detect_media_type
from fram.core.operations import Operation
from fram.core.processors import ImageProcessor, MediaProcessor, VideoProcessor


class Pipeline:
    def __init__(
        self,
        image_processor: MediaProcessor | None = None,
        video_processor: MediaProcessor | None = None,
    ) -> None:
        self.image_processor = image_processor or ImageProcessor()
        self.video_processor = video_processor or VideoProcessor()

    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        processor = self.processor_for(input_path)
        return processor.run(input_path, operations, output_path)

    def processor_for(self, input_path: Path) -> MediaProcessor:
        media_type = detect_media_type(input_path)
        if media_type == MediaType.IMAGE:
            return self.image_processor
        return self.video_processor


def run_pipeline(input_path: Path, operations: list[Operation], output_path: Path) -> Path:
    return Pipeline().run(input_path, operations, output_path)
