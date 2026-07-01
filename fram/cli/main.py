import sys
from pathlib import Path
from typing import Annotated

import typer

from fram import __version__
from fram.cli import commands
from fram.cli.interactive.app import run_interactive
from fram.core.errors import FramError
from fram.updates import check_for_update, install_latest_release, update_notice

COMMAND_NAMES = {
    "help",
    "info",
    "update",
    "version",
    "resize",
    "crop",
    "compress-image",
    "compress-video",
    "convert",
    "rotate",
    "flip",
    "strip-metadata",
    "blur",
    "grayscale",
    "adjust",
    "sharpen",
    "watermark",
    "upscale",
    "auto-orient",
    "background",
    "cut",
    "fps",
    "strip-audio",
    "extract-audio",
    "extract-frame",
    "gif",
    "speed",
    "reverse",
    "mute-audio",
    "thumbnail",
    "contact-sheet",
    "extract-subtitles",
    "do",
}

app = typer.Typer(
    help="Compact media editing for your terminal and agent automation.",
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
    _print_update_notice(args)
    app(args=args)


@app.command()
def version() -> None:
    typer.echo(__version__)


@app.command()
def update(
    check: Annotated[
        bool,
        typer.Option("--check", help="Only check whether an update is available."),
    ] = False,
    source: Annotated[
        str | None,
        typer.Option("--from", help="Install from a custom uv/pipx package source."),
    ] = None,
) -> None:
    try:
        if check:
            status = check_for_update(use_cache=False, timeout_seconds=5.0)
            if status.latest is None:
                typer.echo("Could not find the latest GitHub release.")
            elif status.is_available:
                typer.echo(
                    f"Fram {status.latest.version} is available "
                    f"(current {status.current_version})."
                )
                typer.echo(f"Release: {status.latest.url}")
            else:
                typer.echo(f"Fram is up to date ({status.current_version}).")
            return

        typer.echo(install_latest_release(source))
    except FramError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc


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
def blur(
    file: Path,
    radius: Annotated[float, typer.Option("--radius", "-r")] = 2.0,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.blur_file(file, radius, output))


@app.command()
def grayscale(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.grayscale_file(file, output))


@app.command()
def adjust(
    file: Path,
    brightness: Annotated[float, typer.Option("--brightness", "-b")] = 1.0,
    contrast: Annotated[float, typer.Option("--contrast", "-c")] = 1.0,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.adjust_file(file, brightness, contrast, output))


@app.command()
def sharpen(
    file: Path,
    factor: Annotated[float, typer.Option("--factor", "-f")] = 2.0,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.sharpen_file(file, factor, output))


@app.command()
def watermark(
    file: Path,
    text: Annotated[str, typer.Argument(help="Watermark text.")],
    opacity: Annotated[float, typer.Option("--opacity")] = 0.75,
    position: Annotated[str, typer.Option("--position", "-p")] = "bottom-right",
    size: Annotated[int, typer.Option("--size", "-s")] = 32,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.watermark_file(file, text, opacity, position, size, output))


@app.command()
def upscale(
    file: Path,
    factor: Annotated[float, typer.Option("--factor", "-f")] = 2.0,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.upscale_file(file, factor, output))


@app.command("auto-orient")
def auto_orient(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.auto_orient_file(file, output))


@app.command()
def background(
    file: Path,
    color: Annotated[str, typer.Argument(help="Background color, e.g. white or #ffffff.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.background_file(file, color, output))


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


@app.command("extract-audio")
def extract_audio(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.extract_audio_file(file, output))


@app.command("extract-frame")
def extract_frame(
    file: Path,
    at: Annotated[str, typer.Option("--at", "-a", help="Timestamp, e.g. 00:00:05.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.extract_frame_file(file, at, output))


@app.command()
def gif(
    file: Path,
    fps: Annotated[int, typer.Option("--fps")] = 12,
    width: Annotated[int | None, typer.Option("--width")] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.gif_file(file, fps, width, output))


@app.command()
def speed(
    file: Path,
    factor: Annotated[float, typer.Argument(help="Speed factor, e.g. 2 or 0.5.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.speed_video_file(file, factor, output))


@app.command()
def reverse(
    file: Path,
    no_audio: Annotated[bool, typer.Option("--no-audio")] = False,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.reverse_video_file(file, not no_audio, output))


@app.command("mute-audio")
def mute_audio(
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.mute_audio_file(file, output))


@app.command()
def thumbnail(
    file: Path,
    at: Annotated[str, typer.Option("--at", "-a", help="Timestamp, e.g. 00:00:05.")] = "0",
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.thumbnail_file(file, at, output))


@app.command("contact-sheet")
def contact_sheet(
    file: Path,
    columns: Annotated[int, typer.Option("--columns", "-c")] = 3,
    rows: Annotated[int, typer.Option("--rows", "-r")] = 3,
    width: Annotated[int, typer.Option("--width", "-w")] = 320,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.contact_sheet_file(file, columns, rows, width, output))


@app.command("extract-subtitles")
def extract_subtitles(
    file: Path,
    stream_index: Annotated[int, typer.Option("--stream-index", "-s")] = 0,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.extract_subtitles_file(file, stream_index, output))


@app.command("do")
def do(
    file: Path,
    steps: Annotated[
        list[str],
        typer.Argument(help='Operations, e.g. "resize 800x800" grayscale "convert webp".'),
    ],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.do_chain(file, steps, output))


def _print_result(action: object) -> None:
    try:
        result = action()
    except FramError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1) from exc
    typer.echo(result)


def _print_update_notice(args: list[str]) -> None:
    if not sys.stderr.isatty():
        return
    if not args or args[0] in {"help", "update", "version"} or "--help" in args or "-h" in args:
        return

    notice = update_notice()
    if notice:
        typer.echo(notice, err=True)
