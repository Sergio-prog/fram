from pathlib import Path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def default_output_path(input_path: Path, suffix: str | None = None) -> Path:
    output_suffix = suffix or input_path.suffix
    return input_path.with_name(f"{input_path.stem}.fram{output_suffix}")

