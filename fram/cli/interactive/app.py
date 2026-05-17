from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, ListView, Static

from fram.cli.interactive.files import discover_media_files
from fram.cli.interactive.models import InteractiveState
from fram.cli.interactive.operations import (
    ACTION_HELP,
    ACTION_LABELS,
    actions_for,
    build_interactive_operation,
    describe_operation,
)
from fram.cli.interactive.previews import render_preview
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
    #files, #actions { width: 28; border: solid $accent; padding: 1; }
    #workspace { width: 1fr; padding: 0 1; }
    #summary, #operations, #help { padding: 0 1; }
    #preview { border: solid $accent; padding: 0 1; height: 17; }
    #params, #output { margin: 1 0; }
    Button { margin-right: 1; }
    """

    BINDINGS = [
        ("i", "toggle_details", "Info"),
        ("a", "focus_actions", "Actions"),
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
        self.selected_action: str | None = None
        self.cut_slider = CutRangeSlider()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            yield ListView(id="files")
            yield ListView(id="actions")
            with Vertical(id="workspace"):
                yield Static(id="summary")
                yield Static(id="preview")
                yield Static(id="operations")
                yield Static(id="help")
                yield self.cut_slider
                yield Input(id="params", placeholder="Select an action, then enter values")
                yield Input(id="output", placeholder="Output path, blank means *.fram.*")
                with Horizontal():
                    yield Button("Add", id="add", variant="primary")
                    yield Button("Run", id="run", variant="success")
                    yield Button("Drop last", id="drop")
        yield Footer()

    def on_mount(self) -> None:
        self._load_files()
        if self.initial_file is not None:
            self._select_file(self.initial_file)
        self._refresh()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if not isinstance(item, ChoiceItem):
            return
        if event.list_view.id == "files":
            self._select_file(Path(item.value))
            return
        if event.list_view.id == "actions":
            self.selected_action = item.value
            self.query_one("#params", Input).placeholder = ACTION_HELP[item.value]
            if item.value == "cut":
                self._sync_cut_input()
            self.query_one("#params", Input).focus()
            self._refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add":
            self._add_operation()
        elif event.button.id == "run":
            self.action_run_pipeline()
        elif event.button.id == "drop":
            self.action_drop_last()

    def action_toggle_details(self) -> None:
        self.state.show_details = not self.state.show_details
        self._refresh()

    def action_focus_actions(self) -> None:
        self.query_one("#actions", ListView).focus()

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

    def _load_files(self) -> None:
        files = discover_media_files(Path.cwd())
        file_list = self.query_one("#files", ListView)
        file_list.clear()
        for file in files:
            file_list.append(ChoiceItem(file.name, str(file)))

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
        preview = render_preview(file, media_type)
        self.state.reset_for_file(file, media_type, duration_seconds=duration, preview=preview)
        self.selected_action = None
        self._load_actions(media_type)
        self._refresh()

    def _load_actions(self, media_type: MediaType) -> None:
        action_list = self.query_one("#actions", ListView)
        action_list.clear()
        for action in actions_for(media_type):
            action_list.append(ChoiceItem(ACTION_LABELS[action], action))

    def _add_operation(self) -> None:
        if self.state.media_type is None:
            self.notify("Select a file first.", severity="warning")
            return
        if self.selected_action is None:
            self.notify("Select an action first.", severity="warning")
            return

        value = self.query_one("#params", Input).value
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
        self.query_one("#preview", Static).update(self._preview_text())
        self.query_one("#operations", Static).update(self._operations_text())
        self.query_one("#help", Static).update(self._help_text())
        self.cut_slider.update_range(self.state.cut_range, self._duration_label())

    def _summary_text(self) -> str:
        if self.state.file is None:
            return "Select a media file on the left, or restart with `fram path/to/file`."

        info = get_media_info(self.state.file)
        size_kb = info.size_bytes / 1024
        lines = [
            f"{self.state.file.name}",
            f"{info.media_type.value} {info.suffix} {size_kb:.1f} KB",
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
            return "Preview appears here after selecting media."
        return self.state.preview

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
        if self.selected_action is None:
            return "Choose an action. Shortcuts: i info, a actions, d drop, r run, q quit."
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
