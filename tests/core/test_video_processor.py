from pathlib import Path

from fram.core.operation_factory import (
    blur,
    contact_sheet,
    extract_audio,
    extract_subtitles,
    flip,
    gif,
    grayscale,
    mute_audio,
    reverse,
    rotate,
    speed,
    strip_metadata,
    thumbnail,
)
from fram.core.processors.video import VideoProcessor


def test_video_processor_builds_filters_and_output_args(monkeypatch, tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_run_command(args: list[str]) -> None:
        calls.append(args)

    monkeypatch.setattr("fram.core.processors.video.run_command", fake_run_command)

    output = tmp_path / "out.mp4"
    VideoProcessor().run(
        Path("in.mp4"),
        [
            strip_metadata(),
            blur(2),
            grayscale(),
            rotate(90),
            flip(horizontal=True),
            speed(2),
            reverse(include_audio=False),
            mute_audio(),
        ],
        output,
    )

    args = calls[0]
    assert args[:4] == ["ffmpeg", "-y", "-i", "in.mp4"]
    assert "boxblur=2:1,hue=s=0,transpose=1,hflip,setpts=PTS/2,reverse" in args
    assert "atempo=2,volume=0" in args
    assert "-map_metadata" in args
    assert str(output) == args[-1]


def test_video_processor_builds_generated_media_commands(monkeypatch, tmp_path) -> None:
    calls: list[list[str]] = []

    def fake_run_command(args: list[str]) -> None:
        calls.append(args)

    monkeypatch.setattr("fram.core.processors.video.run_command", fake_run_command)

    VideoProcessor().run(Path("in.mp4"), [extract_audio()], tmp_path / "audio.m4a")
    VideoProcessor().run(Path("in.mp4"), [gif(12, 480)], tmp_path / "out.gif")
    VideoProcessor().run(Path("in.mp4"), [thumbnail("5")], tmp_path / "thumb.png")
    VideoProcessor().run(Path("in.mp4"), [contact_sheet(3, 3, 320)], tmp_path / "sheet.png")
    VideoProcessor().run(Path("in.mp4"), [extract_subtitles()], tmp_path / "subs.srt")

    assert "-vn" in calls[0]
    assert "-an" in calls[1]
    assert "fps=12,scale=480:-1:flags=lanczos" in calls[1]
    assert "-frames:v" in calls[2]
    assert "select='not(mod(n\\,9))',scale=320:-1:flags=lanczos,tile=3x3" in calls[3]
    assert ["-map", "0:s:0"] == calls[4][-3:-1]
