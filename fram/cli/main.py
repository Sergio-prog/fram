import sys
from pathlib import Path
from typing import Annotated

import typer

from fram.cli import commands
from fram.cli.interactive.app import run_interactive
from fram.core.errors import FramError

COMMAND_NAMES = {
    "help",
    "info",
    "resize",
    "crop",
    "compress-image",
    "compress-video",
    "convert",
    "rotate",
    "flip",
    "strip-metadata",
    "cut",
    "fps",
    "strip-audio",
    "extract-frame",
}

app = typer.Typer(
    help="Compact media editing from terminal, API, and Telegram.",
)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        run_interactive()
        return
    if args[0] == "help":
        app(args=[*args[1:], "--help"] if len(args) > 1 else ["--help"])
        return
    if len(args) == 1 and not args[0].startswith("-") and args[0] not in COMMAND_NAMES:
        run_interactive(Path(args[0]))
        return
    app(args=args)


@app.command()
def info(file: Path) -> None:
    _print_result(lambda: commands.media_info(file))


@app.command()
def resize(
    file: Path,
    size: Annotated[str, typer.Argument(help="Target size, for example 128x128.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    mode: Annotated[str, typer.Option("--mode", "-m")] = "fit",
) -> None:
    _print_result(lambda: commands.resize_file(file, size, mode, output))


@app.command()
def crop(
    file: Path,
    size: Annotated[str, typer.Argument(help="Crop size, for example 128x128.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    anchor: Annotated[str, typer.Option("--anchor", "-a")] = "center",
) -> None:
    _print_result(lambda: commands.crop_file(file, size, anchor, output))


@app.command("compress-image")
def compress_image(
    file: Path,
    quality: Annotated[int, typer.Option("--quality", "-q")] = 82,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.compress_image_file(file, quality, output))


@app.command("compress-video")
def compress_video(
    file: Path,
    crf: Annotated[int, typer.Option("--crf")] = 23,
    preset: Annotated[str, typer.Option("--preset")] = "medium",
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.compress_video_file(file, crf, preset, output))


@app.command()
def convert(
    file: Path,
    format_name: Annotated[str, typer.Argument(help="Output format, e.g. jpg, png, webp.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.convert_file(file, format_name, output))


@app.command()
def rotate(
    file: Path,
    degrees: Annotated[int, typer.Argument(help="Clockwise rotation degrees.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.rotate_file(file, degrees, output))


@app.command()
def flip(
    file: Path,
    horizontal: Annotated[bool, typer.Option("--horizontal", "-x")] = False,
    vertical: Annotated[bool, typer.Option("--vertical", "-y")] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.flip_file(file, horizontal, vertical, output))


@app.command("strip-metadata")
def strip_metadata(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.strip_metadata_file(file, output))


@app.command()
def cut(
    file: Path,
    start: Annotated[str, typer.Option("--start", "-s")],
    end: Annotated[str | None, typer.Option("--end", "-e")] = None,
    duration: Annotated[str | None, typer.Option("--duration", "-d")] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.cut_video_file(file, start, end, duration, output))


@app.command()
def fps(
    file: Path,
    value: Annotated[int, typer.Argument(help="Target frames per second.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.fps_video_file(file, value, output))


@app.command("strip-audio")
def strip_audio(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.strip_audio_file(file, output))


@app.command("extract-frame")
def extract_frame(
    file: Path,
    at: Annotated[str, typer.Option("--at", "-a", help="Timestamp, e.g. 00:00:05.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.extract_frame_file(file, at, output))


def _print_result(action: object) -> None:
    try:
        result = action()
    except FramError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(result)
