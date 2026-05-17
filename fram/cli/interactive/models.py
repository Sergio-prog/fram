from dataclasses import dataclass, field
from pathlib import Path

from fram.core.media import MediaType
from fram.core.operations import Operation
from fram.utils.timecodes import format_seconds


@dataclass
class CutRange:
    start_percent: int = 10
    end_percent: int = 85
    active_edge: str = "start"

    def switch_edge(self) -> None:
        self.active_edge = "end" if self.active_edge == "start" else "start"

    def move_active(self, delta: int) -> None:
        if self.active_edge == "start":
            self.start_percent = max(0, min(self.start_percent + delta, self.end_percent - 1))
            return
        self.end_percent = min(100, max(self.end_percent + delta, self.start_percent + 1))

    def to_input_value(self, duration_seconds: float | None) -> str:
        if duration_seconds is None:
            return ""
        start = duration_seconds * self.start_percent / 100
        end = duration_seconds * self.end_percent / 100
        return f"{format_seconds(start)} {format_seconds(end)}"


@dataclass
class InteractiveState:
    file: Path | None = None
    media_type: MediaType | None = None
    operations: list[Operation] = field(default_factory=list)
    show_details: bool = False
    output_path: Path | None = None
    duration_seconds: float | None = None
    cut_range: CutRange = field(default_factory=CutRange)
    preview_path: Path | None = None
    preview_error: str = ""

    def reset_for_file(
        self,
        file: Path,
        media_type: MediaType,
        duration_seconds: float | None = None,
        preview_path: Path | None = None,
        preview_error: str = "",
    ) -> None:
        self.file = file
        self.media_type = media_type
        self.operations.clear()
        self.output_path = None
        self.duration_seconds = duration_seconds
        self.cut_range = CutRange()
        self.preview_path = preview_path
        self.preview_error = preview_error
