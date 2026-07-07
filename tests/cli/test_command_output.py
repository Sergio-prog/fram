from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

import fram.cli.commands as commands
from fram.cli.main import app

runner = CliRunner()


COMMAND_CASES = [
    ("resize_file", ["resize", "{input}", "8x8"]),
    ("crop_file", ["crop", "{input}", "8x8"]),
    ("compress_image_file", ["compress-image", "{input}", "--quality", "80"]),
    ("compress_video_file", ["compress-video", "{input}"]),
    ("convert_file", ["convert", "{input}", "webp"]),
    ("rotate_file", ["rotate", "{input}", "90"]),
    ("flip_file", ["flip", "{input}", "--horizontal"]),
    ("strip_metadata_file", ["strip-metadata", "{input}"]),
    ("blur_file", ["blur", "{input}"]),
    ("grayscale_file", ["grayscale", "{input}"]),
    ("adjust_file", ["adjust", "{input}"]),
    ("sharpen_file", ["sharpen", "{input}"]),
    ("watermark_file", ["watermark", "{input}", "FRAM"]),
    ("upscale_file", ["upscale", "{input}"]),
    ("auto_orient_file", ["auto-orient", "{input}"]),
    ("background_file", ["background", "{input}", "white"]),
    ("cut_video_file", ["cut", "{input}", "--start", "0"]),
    ("fps_video_file", ["fps", "{input}", "24"]),
    ("strip_audio_file", ["strip-audio", "{input}"]),
    ("extract_audio_file", ["extract-audio", "{input}"]),
    ("extract_frame_file", ["extract-frame", "{input}", "--at", "0"]),
    ("gif_file", ["gif", "{input}"]),
    ("speed_video_file", ["speed", "{input}", "2"]),
    ("reverse_video_file", ["reverse", "{input}", "--no-audio"]),
    ("mute_audio_file", ["mute-audio", "{input}"]),
    ("thumbnail_file", ["thumbnail", "{input}"]),
    ("contact_sheet_file", ["contact-sheet", "{input}"]),
    ("extract_subtitles_file", ["extract-subtitles", "{input}"]),
    ("do_chain", ["do", "{input}", "resize 8x8"]),
]


@pytest.mark.parametrize(("function_name", "args"), COMMAND_CASES)
def test_processing_commands_print_formatted_success(
    function_name: str,
    args: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGB", (20, 10), color="black").save(input_path)
    Image.new("RGB", (8, 4), color="white").save(output_path)

    def fake_command(*_args: object, **_kwargs: object) -> Path:
        return output_path

    monkeypatch.setattr(commands, function_name, fake_command)

    result = runner.invoke(app, _expand_args(args, input_path))

    assert result.exit_code == 0, result.output
    assert result.output.startswith(f"\u2713 {output_path}")
    assert "8x4" in result.output


def _expand_args(args: list[str], input_path: Path) -> list[str]:
    return [str(input_path) if arg == "{input}" else arg for arg in args]
