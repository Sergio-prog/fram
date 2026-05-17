from textual.widgets import Label, ListItem, Static

from fram.cli.interactive.models import CutRange


class ChoiceItem(ListItem):
    def __init__(self, label: str, value: str) -> None:
        self.value = value
        super().__init__(Label(label))


class CutRangeSlider(Static):
    def update_range(self, cut_range: CutRange, duration_label: str = "") -> None:
        width = 30
        start = max(0, min(width - 1, round(width * cut_range.start_percent / 100)))
        end = max(start, min(width, round(width * cut_range.end_percent / 100)))
        bar = "." * start + "=" * (end - start) + "." * (width - end)
        active = "<" if cut_range.active_edge == "start" else ">"
        self.update(
            f"cut {active} [{bar}] "
            f"{cut_range.start_percent}%..{cut_range.end_percent}% {duration_label}"
        )
