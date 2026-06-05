from dataclasses import dataclass

from textual.widgets import Static

from fram.core.media import MediaType


@dataclass(frozen=True)
class NumericSliderSpec:
    key: str
    label: str
    minimum: float
    maximum: float
    step: float
    default: float
    integer: bool = False


class NumericParamSliders(Static):
    can_focus = True

    def __init__(self) -> None:
        super().__init__(id="param-sliders")
        self.action: str | None = None
        self.specs: list[NumericSliderSpec] = []
        self.values: list[float] = []
        self.active_index = 0

    def configure(self, action: str | None, media_type: MediaType | None) -> None:
        self.action = action
        self.specs = slider_specs_for(action, media_type)
        self.values = [spec.default for spec in self.specs]
        self.active_index = 0
        self.display = bool(self.specs)
        self.refresh_display()

    def switch_active(self, direction: int = 1) -> None:
        if len(self.specs) < 2:
            return
        self.active_index = (self.active_index + direction) % len(self.specs)
        self.refresh_display()

    def move_active(self, direction: int) -> None:
        if not self.specs:
            return
        spec = self.specs[self.active_index]
        value = self.values[self.active_index] + spec.step * direction
        self.values[self.active_index] = max(spec.minimum, min(spec.maximum, value))
        self.refresh_display()

    def input_value(self) -> str:
        if self.action is None or not self.specs:
            return ""

        values = [
            format_slider_value(value, spec)
            for value, spec in zip(self.values, self.specs, strict=True)
        ]
        match self.action:
            case "adjust":
                return f"{values[0]} {values[1]}"
            case "gif":
                return f"{values[0]} {values[1]}"
            case _:
                return values[0]

    def refresh_display(self) -> None:
        if not self.specs:
            self.update("")
            return

        lines = ["Sliders: Up/Down switch, Left/Right adjust"]
        for index, (spec, value) in enumerate(zip(self.specs, self.values, strict=True)):
            marker = ">" if index == self.active_index else " "
            formatted = format_slider_value(value, spec)
            lines.append(f"{marker} {spec.label:<10} {self.bar(value, spec)} {formatted}")
        self.update("\n".join(lines))

    def bar(self, value: float, spec: NumericSliderSpec) -> str:
        width = 18
        span = spec.maximum - spec.minimum
        ratio = 0 if span == 0 else (value - spec.minimum) / span
        filled = max(0, min(width, round(width * ratio)))
        return "[" + "=" * filled + "." * (width - filled) + "]"


def slider_specs_for(
    action: str | None,
    media_type: MediaType | None,
) -> list[NumericSliderSpec]:
    match action:
        case "compress":
            if media_type == MediaType.IMAGE:
                return [NumericSliderSpec("quality", "quality", 1, 100, 1, 82, integer=True)]
            return [NumericSliderSpec("crf", "crf", 0, 51, 1, 23, integer=True)]
        case "fps":
            return [NumericSliderSpec("fps", "fps", 1, 60, 1, 24, integer=True)]
        case "blur":
            return [NumericSliderSpec("radius", "radius", 0, 20, 0.5, 2)]
        case "adjust":
            return [
                NumericSliderSpec("brightness", "brightness", 0, 2, 0.05, 1),
                NumericSliderSpec("contrast", "contrast", 0, 2, 0.05, 1),
            ]
        case "sharpen":
            return [NumericSliderSpec("factor", "factor", 0, 5, 0.25, 2)]
        case "upscale":
            return [NumericSliderSpec("factor", "factor", 1.1, 4, 0.1, 2)]
        case "rotate":
            return [NumericSliderSpec("degrees", "degrees", 0, 360, 90, 90, integer=True)]
        case "gif":
            return [
                NumericSliderSpec("fps", "fps", 1, 30, 1, 12, integer=True),
                NumericSliderSpec("width", "width", 120, 1080, 40, 480, integer=True),
            ]
        case "speed":
            return [NumericSliderSpec("factor", "factor", 0.25, 4, 0.25, 1)]
        case _:
            return []


def format_slider_value(value: float, spec: NumericSliderSpec) -> str:
    if spec.integer:
        return str(round(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")
