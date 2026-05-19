from dataclasses import dataclass


@dataclass(frozen=True)
class ConvertParams:
    format: str


@dataclass(frozen=True)
class StripMetadataParams:
    enabled: bool = True
