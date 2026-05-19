from dataclasses import dataclass


@dataclass(frozen=True)
class CutParams:
    start_seconds: float
    end_seconds: float | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True)
class VideoCompressParams:
    crf: int = 23
    preset: str = "medium"


@dataclass(frozen=True)
class FpsParams:
    fps: int


@dataclass(frozen=True)
class StripAudioParams:
    enabled: bool = True


@dataclass(frozen=True)
class ExtractAudioParams:
    enabled: bool = True


@dataclass(frozen=True)
class ExtractFrameParams:
    at_seconds: float


@dataclass(frozen=True)
class GifParams:
    fps: int = 12
    width: int | None = None


@dataclass(frozen=True)
class SpeedParams:
    factor: float


@dataclass(frozen=True)
class ReverseParams:
    include_audio: bool = True
