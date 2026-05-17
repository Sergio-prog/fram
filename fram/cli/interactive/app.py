from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, ListView, Static
from textual_image.widget import Image as TerminalImage

from fram.cli.interactive.files import BrowserEntry, list_browser_entries
from fram.cli.interactive.models import InteractiveState
from fram.cli.interactive.operations import (
    ACTION_HELP,
    ACTION_LABELS,
    actions_for,
    build_interactive_operation,
    describe_operation,
    value_presets_for,
)
from fram.cli.interactive.previews import PreviewImage, cleanup_preview, prepare_preview_image
from fram.cli.interactive.widgets import ChoiceItem, CutRangeSlider
from fram.core.errors import FramError
from fram.core.media import MediaType, detect_media_type, get_media_info
from fram.core.pipeline import run_pipeline
from fram.core.probe import probe_duration_seconds
from fram.utils.files import default_output_path
from fram.utils.timecodes import format_seconds


class FramInteractiveApp(App[None]):
    CSS = """
    Screen { padding: 1 2; }
    #main { height: 1fr; }
    #files, #actions, #values { width: 27; border: solid $accent; padding: 1; }
    #workspace { width: 1fr; padding: 0 1; }
    #summary, #operations, #help { padding: 0 1; }
    #preview_image, #preview_text { border: solid $accent; padding: 0 1; height: 17; }
    #params, #output { margin: 1 0; }
    Button { margin-right: 1; }
    """

    BINDINGS = [
        ("i", "toggle_details", "Info"),
        ("f", "focus_files", "Files"),
        ("a", "focus_actions", "Actions"),
        ("v", "focus_values", "Values"),
        ("d", "drop_last", "Drop"),
        ("tab", "switch_cut_edge", "Edge"),
        ("left", "move_cut_left", "Cut -"),
        ("right", "move_cut_right", "Cut +"),
        ("r", "run_pipeline", "Run"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, file: Path | None = None) -> None:
        super().__init__()
        self.state = InteractiveState()
        self.initial_file = file
        self.current_dir = Path.cwd()
        self.browser_locked = False
        self.selected_action: str | None = None
        self.cut_slider = CutRangeSlider()
        self.current_preview: PreviewImage | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            yield ListView(id="files")
            yield ListView(id="actions")
            yield ListView(id="values")
            with Vertical(id="workspace"):
                yield Static(id="summary")
                yield TerminalImage(id="preview_image")
                yield Static(id="preview_text")
                yield Static(id="operations")
                yield Static(id="help")
                yield self.cut_slider
                yield Input(id="params", placeholder="Custom value, then Enter")
                yield Input(id="output", placeholder="Output path, blank means *.fram.*")
                with Horizontal():
                    yield Button("Run", id="run", variant="success")
                    yield Button("Drop last", id="drop")
        yield Footer()

    async def on_mount(self) -> None:
        await self._load_files()
        if self.initial_file is not None:
            self._select_file(self.initial_file)
        else:
            self.query_one("#files", ListView).focus()
        self._refresh()

    def on_unmount(self) -> None:
        cleanup_preview(self.current_preview)

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, ChoiceItem):
            return
        if event.list_view.id == "files":
            await self._select_browser_item(item)
            return
        if event.list_view.id == "actions":
            await self._select_action(item.value)
            return
        if event.list_view.id == "values":
            self._add_operation(item.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            self.action_run_pipeline()
        elif event.button.id == "drop":
            self.action_drop_last()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "params":
            self._add_operation(event.value)

    def action_toggle_details(self) -> None:
        self.state.show_details = not self.state.show_details
        self._refresh()

    def action_focus_files(self) -> None:
        if not self.browser_locked:
            self.query_one("#files", ListView).focus()

    def action_focus_actions(self) -> None:
        self.query_one("#actions", ListView).focus()

    def action_focus_values(self) -> None:
        self.query_one("#values", ListView).focus()

    def action_drop_last(self) -> None:
        if self.state.operations:
            self.state.operations.pop()
            self._refresh()

    def action_switch_cut_edge(self) -> None:
        if self.selected_action != "cut":
            return
        self.state.cut_range.switch_edge()
        self._sync_cut_input()
        self._refresh()

    def action_move_cut_left(self) -> None:
        self._move_cut(-1)

    def action_move_cut_right(self) -> None:
        self._move_cut(1)

    def action_run_pipeline(self) -> None:
        if self.state.file is None:
            self.notify("Select a file first.", severity="warning")
            return
        if not self.state.operations:
            self.notify("Add at least one operation.", severity="warning")
            return

        output_value = self.query_one("#output", Input).value.strip()
        output_path = Path(output_value) if output_value else default_output_path(self.state.file)

        try:
            result = run_pipeline(self.state.file, self.state.operations, output_path)
        except FramError as exc:
            self.notify(str(exc), severity="error")
            return

        self.state.output_path = result
        self.notify(f"Saved {result}")
        self._refresh()

    async def _select_browser_item(self, item: ChoiceItem) -> None:
        if self.browser_locked:
            return
        path = Path(item.value)
        if item.kind == "dir":
            self.current_dir = path
            await self._load_files()
            return
        self._select_file(path)

    async def _load_files(self) -> None:
        file_list = self.query_one("#files", ListView)
        await file_list.clear()
        entries = list_browser_entries(self.current_dir)
        for entry in entries:
            file_list.append(self._browser_item(entry))

    def _browser_item(self, entry: BrowserEntry) -> ChoiceItem:
        prefix = "▸ " if entry.is_dir else "  "
        kind = "dir" if entry.is_dir else "file"
        return ChoiceItem(prefix + entry.label, str(entry.path), kind=kind)

    def _select_file(self, file: Path) -> None:
        if not file.exists():
            self.notify(f"File does not exist: {file}", severity="error")
            return

        try:
            media_type = detect_media_type(file)
        except FramError as exc:
            self.notify(str(exc), severity="error")
            return

        duration = probe_duration_seconds(file) if media_type == MediaType.VIDEO else None
        cleanup_preview(self.current_preview)
        self.current_preview = prepare_preview_image(file, media_type)
        self.state.reset_for_file(
            file,
            media_type,
            duration_seconds=duration,
            preview_path=self.current_preview.path,
            preview_error=self.current_preview.error,
        )
        self.browser_locked = True
        self.selected_action = None
        self._load_actions(media_type)
        self.query_one("#actions", ListView).focus()
        self._refresh()

    def _load_actions(self, media_type: MediaType) -> None:
        action_list = self.query_one("#actions", ListView)
        action_list.clear()
        for action in actions_for(media_type):
            action_list.append(ChoiceItem(ACTION_LABELS[action], action))
        self.query_one("#values", ListView).clear()

    async def _select_action(self, action: str) -> None:
        self.selected_action = action
        self.query_one("#params", Input).placeholder = ACTION_HELP[action]
        if action == "cut":
            self._sync_cut_input()
        await self._load_values(action)
        self.query_one("#values", ListView).focus()
        self._refresh()

    async def _load_values(self, action: str) -> None:
        value_list = self.query_one("#values", ListView)
        await value_list.clear()
        slider_value = self.state.cut_range.to_input_value(self.state.duration_seconds)
        for value in value_presets_for(action, slider_value):
            value_list.append(ChoiceItem(value, "" if value == "slider range" else value))

    def _add_operation(self, raw_value: str) -> None:
        if self.state.media_type is None:
            self.notify("Select a file first.", severity="warning")
            return
        if self.selected_action is None:
            self.notify("Select an action first.", severity="warning")
            return

        value = raw_value or self.query_one("#params", Input).value
        try:
            operation = build_interactive_operation(
                self.selected_action,
                self.state.media_type,
                value,
            )
        except FramError as exc:
            self.notify(str(exc), severity="error")
            return

        self.state.operations.append(operation)
        self.query_one("#params", Input).value = ""
        self._refresh()

    def _move_cut(self, delta: int) -> None:
        if self.selected_action != "cut":
            return
        self.state.cut_range.move_active(delta)
        self._sync_cut_input()
        self._refresh()

    def _sync_cut_input(self) -> None:
        value = self.state.cut_range.to_input_value(self.state.duration_seconds)
        if value:
            self.query_one("#params", Input).value = value

    def _refresh(self) -> None:
        self.query_one("#summary", Static).update(self._summary_text())
        self._refresh_preview()
        self.query_one("#operations", Static).update(self._operations_text())
        self.query_one("#help", Static).update(self._help_text())
        self._refresh_cut_slider()

    def _refresh_preview(self) -> None:
        image = self.query_one("#preview_image", TerminalImage)
        text = self.query_one("#preview_text", Static)
        if self.state.preview_path:
            image.image = self.state.preview_path
            image.display = True
            text.display = False
            return

        image.image = None
        image.display = False
        text.display = True
        text.update(self._preview_text())

    def _refresh_cut_slider(self) -> None:
        is_cut = self.selected_action == "cut"
        self.cut_slider.display = is_cut
        if is_cut:
            self.cut_slider.update_range(self.state.cut_range, self._duration_label())

    def _summary_text(self) -> str:
        if self.state.file is None:
            return f"Browse: {self.current_dir}\nUse arrows and Enter. Only media files are shown."

        info = get_media_info(self.state.file)
        size_kb = info.size_bytes / 1024
        lines = [
            f"Selected: {self.state.file.name}",
            f"{info.media_type.value} {info.suffix} {size_kb:.1f} KB",
            "File browser locked. Choose actions/values.",
        ]
        if self.state.output_path:
            lines.append(f"last output: {self.state.output_path}")
        if self.state.show_details:
            lines.append(f"path: {self.state.file}")
            if self.state.duration_seconds is not None:
                lines.append(f"duration: {format_seconds(self.state.duration_seconds)}")
        return "\n".join(lines)

    def _preview_text(self) -> str:
        if self.state.file is None:
            return "Preview appears after selecting media."
        return self.state.preview_error or "Preview unavailable."

    def _operations_text(self) -> str:
        if not self.state.operations:
            return "Pipeline: no operations yet."
        lines = ["Pipeline:"]
        lines.extend(
            f"{index}. {describe_operation(operation)}"
            for index, operation in enumerate(self.state.operations, start=1)
        )
        return "\n".join(lines)

    def _help_text(self) -> str:
        if self.state.file is None:
            return "Browse with arrows and Enter. Direct file mode: `fram image.png`."
        if self.selected_action is None:
            return "Pick action, then pick value. Custom params can be typed below."
        if self.selected_action == "cut":
            return (
                f"{self.selected_action}: {ACTION_HELP[self.selected_action]}. "
                "Tab switches edge; left/right moves it."
            )
        return f"{self.selected_action}: {ACTION_HELP[self.selected_action]}"

    def _duration_label(self) -> str:
        if self.state.duration_seconds is None:
            return ""
        return f"({format_seconds(self.state.duration_seconds)})"


def run_interactive(file: Path | None = None) -> None:
    FramInteractiveApp(file=file).run()
