from pathlib import Path

from fram.core.operations import Operation
from fram.core.pipeline import Pipeline


class FakeProcessor:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, list[Operation], Path]] = []

    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        self.calls.append((input_path, operations, output_path))
        return output_path


def test_pipeline_dispatches_images() -> None:
    image_processor = FakeProcessor()
    video_processor = FakeProcessor()
    pipeline = Pipeline(image_processor=image_processor, video_processor=video_processor)

    result = pipeline.run(Path("in.jpg"), [], Path("out.jpg"))

    assert result == Path("out.jpg")
    assert image_processor.calls == [(Path("in.jpg"), [], Path("out.jpg"))]
    assert video_processor.calls == []


def test_pipeline_dispatches_videos() -> None:
    image_processor = FakeProcessor()
    video_processor = FakeProcessor()
    pipeline = Pipeline(image_processor=image_processor, video_processor=video_processor)

    result = pipeline.run(Path("in.mp4"), [], Path("out.mp4"))

    assert result == Path("out.mp4")
    assert image_processor.calls == []
    assert video_processor.calls == [(Path("in.mp4"), [], Path("out.mp4"))]
