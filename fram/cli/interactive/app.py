from pathlib import Path

from textual import events
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
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
from fram.cli.interactive.param_sliders import NumericParamSliders
from fram.cli.interactive.previews import PreviewImage, cleanup_preview, prepare_preview_image
from fram.cli.interactive.widgets import ChoiceItem, CutRangeSlider
from fram.core.errors import FramError
from fram.core.media import MediaType, detect_media_type, get_media_info
from fram.core.metadata import collect_media_metadata
from fram.core.output import default_output_for_operations
from fram.core.pipeline import run_pipeline
from fram.core.probe import probe_duration_seconds
from fram.utils.timecodes import format_seconds


class FramInteractiveApp(App[None]):
    NO_VALUE_ACTIONS = {
        "strip-audio",
        "strip-metadata",
        "grayscale",
        "extract-audio",
        "auto-orient",
        "mute-audio",
    }

    CSS = """
    Screen { padding: 1 2; }
    #main { height: 1fr; }
    #files, #actions { width: 30; border: solid $accent; padding: 1; }
    #workspace {
        width: 1fr;
        height: 1fr;
        overflow-y: auto;
        padding: 0 1;
    }
    #preview-row { height: 20; }
    #preview-pane {
        border: solid $accent;
        height: 20;
        width: 1fr;
    }
    #summary {
        border: solid $accent;
        color: $text-muted;
        margin: 0 0 0 1;
        padding: 0 1;
        width: 38;
    }
    #operations { padding: 0 1; }
    #pipeline-toggle { margin: 1 0 0 0; width: 100%; }
    #operations {
        border-left: solid $accent;
        color: $text-muted;
        margin: 0 0 1 0;
    }
    #preset-suggestions {
        border: tall $accent;
        height: auto;
        max-height: 7;
        margin: 0 0 1 0;
    }
    #param-sliders {
        border: tall $accent;
        margin: 0 0 1 0;
        padding: 0 1;
    }
    #param-sliders:focus {
        border: tall $success;
    }
    #preview_image, #preview_text {
        padding: 0 1;
        width: auto;
        height: 100%;
    }
    .field-label {
        color: $text-muted;
        margin: 1 0 0 0;
    }
    #params, #output { margin: 0 0 1 0; }
    Button { margin-right: 1; }
    """

    BINDINGS = [
        ("i", "toggle_details", "Info"),
        ("f", "focus_files", "Files"),
        ("a", "focus_actions", "Actions"),
        ("d", "drop_last", "Drop"),
        ("left", "move_slider_left", "Value -"),
        ("right", "move_slider_right", "Value +"),
        ("up", "previous_slider", "Slider ↑"),
        ("down", "next_slider", "Slider ↓"),
        ("r", "run_pipeline", "Run"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, file: Path | None = None) -> None:
        super().__init__()
        self.state = InteractiveState()
        self.initial_file = file
        self.current_dir = Path.cwd()
        self.selected_action: str | None = None
        self.pipeline_open = False
        self.show_info = True
        self.cut_slider = CutRangeSlider()
        self.param_sliders = NumericParamSliders()
        self.current_preview: PreviewImage | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main"):
            yield ListView(id="files")
            yield ListView(id="actions")
            with VerticalScroll(id="workspace", can_focus=True):
                with Horizontal(id="preview-row"):
                    with Container(id="preview-pane"):
                        yield TerminalImage(id="preview_image")
                        yield Static(id="preview_text")
                    yield Static(id="summary")
                yield Button("Pipeline (0 operations) ▸", id="pipeline-toggle")
                yield Static(id="operations")
                yield self.cut_slider
                yield self.param_sliders
                yield Static("Value for action", classes="field-label")
                yield Input(id="params", placeholder="Custom value, then Enter")
                yield ListView(id="preset-suggestions")
                yield Static("Output", classes="field-label")
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
        if event.list_view.id == "preset-suggestions":
            self._use_preset(item.value)
            return

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run":
            await self.action_run_pipeline()
        elif event.button.id == "drop":
            self.action_drop_last()
        elif event.button.id == "pipeline-toggle":
            self.pipeline_open = not self.pipeline_open
            self._refresh()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "params":
            self._refresh_preset_suggestions(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "params":
            self._add_operation(event.value)

    def on_key(self, event: events.Key) -> None:
        if self.focused is self.param_sliders:
            if event.key == "enter":
                self._add_operation(self.query_one("#params", Input).value)
                event.stop()
                return
            if event.key in {"up", "down"}:
                self._switch_param_slider(-1 if event.key == "up" else 1)
                event.stop()
                return

        if event.key not in {"down", "up"}:
            return
        if self.focused is not self.query_one("#params", Input):
            return

        suggestions = self.query_one("#preset-suggestions", ListView)
        if not suggestions.display or not suggestions.children:
            return

        suggestions.index = 0 if event.key == "down" else len(suggestions.children) - 1
        suggestions.focus()
        event.stop()

    def action_toggle_details(self) -> None:
        self.show_info = not self.show_info
        self._refresh()

    def action_focus_files(self) -> None:
        self.query_one("#files", ListView).focus()

    def action_focus_actions(self) -> None:
        self.query_one("#actions", ListView).focus()

    def action_drop_last(self) -> None:
        if self.state.operations:
            self.state.operations.pop()
            self._refresh()

    def action_previous_slider(self) -> None:
        self._switch_slider(-1)

    def action_next_slider(self) -> None:
        self._switch_slider(1)

    def _switch_slider(self, direction: int) -> None:
        if self.selected_action == "cut":
            if direction < 0:
                self.state.cut_range.active_edge = "start"
            else:
                self.state.cut_range.active_edge = "end"
            self._sync_cut_input()
            self._refresh()
            return
        if not self.param_sliders.specs:
            return
        self._switch_param_slider(direction)

    def _switch_param_slider(self, direction: int) -> None:
        self.param_sliders.switch_active(direction)
        self._sync_param_slider_input()

    def action_move_slider_left(self) -> None:
        self._move_slider(-1)

    def action_move_slider_right(self) -> None:
        self._move_slider(1)

    async def action_run_pipeline(self) -> None:
        if self.state.file is None:
            self.notify("Select a file first.", severity="warning")
            return
        if not self.state.operations:
            self.notify("Add at least one operation.", severity="warning")
            return

        output_value = self.query_one("#output", Input).value.strip()
        output_path = (
            Path(output_value)
            if output_value
            else default_output_for_operations(self.state.file, self.state.operations)
        )

        try:
            result = run_pipeline(self.state.file, self.state.operations, output_path)
        except FramError as exc:
            self.notify(str(exc), severity="error")
            return

        self.state.output_path = result
        self.current_dir = result.parent
        await self._load_files(selected_path=result)
        self.notify(f"Saved {result}")
        self._refresh()

    async def _select_browser_item(self, item: ChoiceItem) -> None:
        path = Path(item.value)
        if item.kind == "dir":
            self.current_dir = path
            await self._load_files()
            return
        self._select_file(path)

    async def _load_files(self, selected_path: Path | None = None) -> None:
        file_list = self.query_one("#files", ListView)
        await file_list.clear()
        entries = list_browser_entries(self.current_dir)
        selected_index = None
        for index, entry in enumerate(entries):
            file_list.append(self._browser_item(entry))
            if selected_path is not None and entry.path == selected_path:
                selected_index = index
        if selected_index is not None:
            file_list.index = selected_index

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
        metadata = collect_media_metadata(file)
        cleanup_preview(self.current_preview)
        self.current_preview = prepare_preview_image(file, media_type)
        self.state.reset_for_file(
            file,
            media_type,
            duration_seconds=duration,
            resolution=metadata.value("Resolution"),
            preview_path=self.current_preview.path,
            preview_error=self.current_preview.error,
        )
        self.selected_action = None
        self.param_sliders.configure(None, self.state.media_type)
        self.query_one("#params", Input).value = ""
        self.query_one("#params", Input).placeholder = ""
        self._load_actions(media_type)
        self.query_one("#actions", ListView).focus()
        self._refresh()

    def _load_actions(self, media_type: MediaType) -> None:
        action_list = self.query_one("#actions", ListView)
        action_list.clear()
        for action in actions_for(media_type):
            action_list.append(ChoiceItem(ACTION_LABELS[action], action))
        self._refresh_preset_suggestions("")

    async def _select_action(self, action: str) -> None:
        self.selected_action = action
        if action in self.NO_VALUE_ACTIONS:
            self._add_operation("")
            return

        self.param_sliders.configure(action, self.state.media_type)
        self.query_one("#params", Input).placeholder = ACTION_HELP[action]
        if action == "cut":
            self._sync_cut_input()
        elif self.param_sliders.specs:
            self._sync_param_slider_input()
        if self.param_sliders.specs:
            self.param_sliders.focus()
        else:
            self.query_one("#params", Input).focus()
        self._refresh_preset_suggestions(self.query_one("#params", Input).value)
        self._refresh()

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
        self.selected_action = None
        self.param_sliders.configure(None, self.state.media_type)
        self.query_one("#params", Input).value = ""
        self.query_one("#params", Input).placeholder = ""
        self._refresh_preset_suggestions("")
        self.query_one("#actions", ListView).focus()
        self._refresh()

    def _move_slider(self, delta: int) -> None:
        if self.selected_action == "cut":
            self.state.cut_range.move_active(delta)
            self._sync_cut_input()
            self._refresh()
            return
        if not self.param_sliders.specs:
            return
        self.param_sliders.move_active(delta)
        self._sync_param_slider_input()

    def _sync_cut_input(self) -> None:
        value = self.state.cut_range.to_input_value(self.state.duration_seconds)
        if value:
            self.query_one("#params", Input).value = value

    def _sync_param_slider_input(self) -> None:
        value = self.param_sliders.input_value()
        if value:
            self.query_one("#params", Input).value = value
            self._refresh_preset_suggestions(value)

    def _refresh(self) -> None:
        self.query_one("#summary", Static).update(self._summary_text())
        self.query_one("#summary", Static).display = self.show_info
        self._refresh_preview()
        self.query_one("#pipeline-toggle", Button).label = self._pipeline_label()
        self.query_one("#operations", Static).update(self._operations_text())
        self.query_one("#operations", Static).display = self.pipeline_open
        self._refresh_preset_suggestions(self.query_one("#params", Input).value)
        self._refresh_cut_slider()
        self._refresh_param_sliders()

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

    def _refresh_param_sliders(self) -> None:
        self.param_sliders.display = (
            self.selected_action != "cut" and bool(self.param_sliders.specs)
        )
        if self.param_sliders.display:
            self.param_sliders.refresh_display()

    def _summary_text(self) -> str:
        if self.state.file is None:
            return f"Browse: {self.current_dir}\nUse arrows and Enter. Only media files are shown."

        info = get_media_info(self.state.file)
        size_kb = info.size_bytes / 1024
        lines = [
            f"Selected: {self.state.file.name}",
            f"{info.media_type.value} {info.suffix} {size_kb:.1f} KB",
        ]
        if self.state.resolution:
            lines.insert(2, f"resolution {self.state.resolution}")
        if self.state.output_path:
            lines.append(f"last output: {self.state.output_path}")
        if self.state.duration_seconds is not None:
            lines.append(f"duration: {format_seconds(self.state.duration_seconds)}")
        return "\n".join(lines)

    def _preview_text(self) -> str:
        if self.state.file is None:
            return "Preview appears after selecting media."
        return self.state.preview_error or "Preview unavailable."

    def _operations_text(self) -> str:
        if not self.state.operations:
            return "No operations yet."
        lines = [
            f"{index}. {describe_operation(operation)}"
            for index, operation in enumerate(self.state.operations, start=1)
        ]
        return "\n".join(lines)

    def _pipeline_label(self) -> str:
        count = len(self.state.operations)
        marker = "▾" if self.pipeline_open else "▸"
        noun = "operation" if count == 1 else "operations"
        return f"Pipeline ({count} {noun}) {marker}"

    def _preset_values(self, query: str = "") -> list[str]:
        if self.selected_action is None:
            return []
        if self.selected_action != "cut" and self.param_sliders.specs:
            return []

        slider_value = self.state.cut_range.to_input_value(self.state.duration_seconds)
        values = value_presets_for(self.selected_action, slider_value)
        return [
            value
            for value in values
            if value != "slider range" and query.lower() in value.lower()
        ]

    def _refresh_preset_suggestions(self, query: str) -> None:
        suggestions = self.query_one("#preset-suggestions", ListView)
        suggestions.clear()
        values = self._preset_values(query)
        suggestions.display = bool(values)
        for value in values:
            suggestions.append(ChoiceItem(value, value, kind="preset"))

    def _use_preset(self, value: str) -> None:
        params = self.query_one("#params", Input)
        if value == "apply":
            self._add_operation("")
            return
        params.value = value
        params.focus()

    def _duration_label(self) -> str:
        if self.state.duration_seconds is None:
            return ""
        return f"({format_seconds(self.state.duration_seconds)})"


def run_interactive(file: Path | None = None) -> None:
    FramInteractiveApp(file=file).run()
