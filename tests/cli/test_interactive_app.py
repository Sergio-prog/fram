import asyncio
from pathlib import Path

from textual.widgets import Input, ListView

import fram.cli.interactive.app as interactive_app
from fram.cli.interactive.app import FramInteractiveApp
from fram.cli.interactive.widgets import ChoiceItem
from fram.core.media import MediaType
from fram.core.operation_factory import resize


def test_interactive_app_mounts() -> None:
    asyncio.run(_mount_app())


async def _mount_app() -> None:
    app = FramInteractiveApp()

    async with app.run_test():
        pass


def test_pipeline_run_refreshes_file_browser(tmp_path, monkeypatch) -> None:
    asyncio.run(_run_pipeline_and_check_files(tmp_path, monkeypatch))


async def _run_pipeline_and_check_files(tmp_path, monkeypatch) -> None:
    input_path = tmp_path / "image.png"
    output_path = tmp_path / "image-small.png"
    input_path.write_bytes(b"input")

    def fake_run_pipeline(source: Path, operations, destination: Path) -> Path:
        assert source == input_path
        assert destination == output_path
        assert operations
        output_path.write_bytes(b"output")
        return output_path

    monkeypatch.setattr(interactive_app, "run_pipeline", fake_run_pipeline)

    app = FramInteractiveApp()
    async with app.run_test():
        app.current_dir = tmp_path
        await app._load_files()
        app.state.file = input_path
        app.state.media_type = MediaType.IMAGE
        app.state.operations.append(resize("10x10"))
        app.query_one("#output", Input).value = str(output_path)

        await app.action_run_pipeline()

        file_list = app.query_one("#files", ListView)
        values = [
            Path(item.value).name
            for item in file_list.children
            if isinstance(item, ChoiceItem)
        ]
        assert "image-small.png" in values
        assert file_list.index == values.index("image-small.png")


def test_adjust_slider_updates_params_input() -> None:
    asyncio.run(_select_adjust_and_move_sliders())


async def _select_adjust_and_move_sliders() -> None:
    app = FramInteractiveApp()
    async with app.run_test() as pilot:
        app.state.media_type = MediaType.IMAGE

        await app._select_action("adjust")
        await pilot.pause()
        assert app.focused is app.param_sliders
        assert app.query_one("#preset-suggestions", ListView).display is False

        app.action_move_slider_right()
        app.action_next_slider()
        app.action_move_slider_right()

        assert app.query_one("#params", Input).value == "1.05 1.05"
