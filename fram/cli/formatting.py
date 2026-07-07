import os
import sys
from pathlib import Path
from typing import TextIO

from fram.core.metadata import collect_media_metadata

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
WARM = "\033[38;5;223m"

CHECK = "\u2713"
ARROW = "\u2192"
DOT = " \u00b7 "


def should_color(stream: TextIO = sys.stdout) -> bool:
    return "NO_COLOR" not in os.environ and stream.isatty()


def format_processed_path(
    path: Path,
    *,
    source: Path | None = None,
    elapsed_seconds: float | None = None,
    compare_size: bool = False,
    color: bool = False,
) -> str:
    head = f"{_paint(CHECK, GREEN, color)} {_paint(_display_path(path), BOLD + WARM, color)}"
    parts = _media_parts(path)

    if compare_size and source and source.exists() and path.exists():
        parts.append(_size_change(source.stat().st_size, path.stat().st_size, color=color))
    elif path.exists():
        parts.append(_format_size(path.stat().st_size))

    if elapsed_seconds is not None:
        parts.append(f"{elapsed_seconds:.1f}s")

    if parts:
        return f"{head}{DOT}{DOT.join(parts)}"
    return head


def format_info_text(text: str, *, color: bool = False) -> str:
    rows = [line.split(": ", 1) for line in text.splitlines() if ": " in line]
    if not rows:
        return text

    width = max(len(label) for label, _ in rows)
    lines = [_paint("Media info", BOLD + WARM, color)]
    for label, value in rows:
        padded = label.ljust(width)
        lines.append(f"  {_paint(padded, DIM, color)}  {value}")
    return "\n".join(lines)


def format_error(message: object, *, color: bool = False) -> str:
    return f"{_paint('error:', RED + BOLD, color)} {message}"


def format_warning(message: object, *, color: bool = False) -> str:
    return f"{_paint('warning:', YELLOW + BOLD, color)} {message}"


def _media_parts(path: Path) -> list[str]:
    if not path.exists():
        return []

    try:
        metadata = collect_media_metadata(path)
    except Exception:
        return []

    parts = []
    resolution = metadata.value("Resolution")
    duration = metadata.value("Duration")
    if resolution:
        parts.append(resolution)
    if duration:
        parts.append(duration)
    return parts


def _size_change(before: int, after: int, *, color: bool) -> str:
    if before <= 0:
        return _format_size(after)

    delta = (after - before) / before
    sign = "+" if delta >= 0 else ""
    before_text = _format_size(before)
    after_text = _paint(_format_size(after), WARM, color)
    arrow = _paint(ARROW, BLUE, color)
    return f"{before_text} {arrow} {after_text} ({sign}{delta:.0%})"


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.1f} MB"


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def _paint(text: str, style: str, color: bool) -> str:
    if not color:
        return text
    return f"{style}{text}{RESET}"
