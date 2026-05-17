from pathlib import Path

from fram.core.errors import ProcessingFailed
from fram.utils.process import run_capture


def probe_duration_seconds(path: Path) -> float | None:
    try:
        output = run_capture(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ]
        )
    except ProcessingFailed:
        return None

    try:
        duration = float(output)
    except ValueError:
        return None
    return duration if duration > 0 else None

