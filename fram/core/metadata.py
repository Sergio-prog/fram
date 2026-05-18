import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import ExifTags, Image

from fram.core.media import MediaType, detect_media_type
from fram.utils.process import run_capture

EXIF_TAGS = ExifTags.TAGS
GPS_TAGS = ExifTags.GPSTAGS


@dataclass(frozen=True)
class MetadataField:
    label: str
    value: str


@dataclass(frozen=True)
class MediaMetadata:
    fields: list[MetadataField] = field(default_factory=list)

    def value(self, label: str) -> str | None:
        for metadata_field in self.fields:
            if metadata_field.label == label:
                return metadata_field.value
        return None

    def as_text(self) -> str:
        return "\n".join(f"{field.label}: {field.value}" for field in self.fields)


def collect_media_metadata(path: Path) -> MediaMetadata:
    media_type = detect_media_type(path)
    if media_type == MediaType.IMAGE:
        return collect_image_metadata(path)
    return collect_video_metadata(path)


def collect_image_metadata(path: Path) -> MediaMetadata:
    stat = path.stat()
    fields = _base_fields(path, MediaType.IMAGE, stat.st_size)

    with Image.open(path) as image:
        exif = _named_exif(image)
        width, height = image.size
        x_resolution, y_resolution = _image_resolution(image, exif)

        fields.extend(
            [
                MetadataField("Resolution", f"{width}x{height}"),
                MetadataField("Color Scheme", image.mode),
            ]
        )
        _append_optional(fields, "Created At", _first_value(exif, "DateTimeOriginal", "DateTime"))
        _append_optional(fields, "Camera Make", exif.get("Make"))
        _append_optional(fields, "Camera Model", exif.get("Model"))
        _append_optional(fields, "Lens", exif.get("LensModel"))
        _append_optional(
            fields,
            "ISO",
            _first_value(exif, "ISOSpeedRatings", "PhotographicSensitivity"),
        )
        _append_optional(fields, "Description", _first_value(exif, "ImageDescription", "XPTitle"))
        _append_optional(fields, "Creator", _first_value(exif, "Artist", "XPAuthor"))
        _append_optional(fields, "Keywords", _first_value(exif, "XPKeywords", "Keywords"))
        _append_optional(fields, "X Resolution", x_resolution)
        _append_optional(fields, "Y Resolution", y_resolution)
        _append_optional(fields, "Geolocation", _gps_location(exif.get("GPSInfo")))

    return MediaMetadata(fields)


def collect_video_metadata(path: Path) -> MediaMetadata:
    stat = path.stat()
    fields = _base_fields(path, MediaType.VIDEO, stat.st_size)
    data = _ffprobe_json(path)
    streams = data.get("streams", [])
    format_info = data.get("format", {})
    tags = _lower_keys(format_info.get("tags", {}))

    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    width = video_stream.get("width")
    height = video_stream.get("height")
    if width and height:
        fields.append(MetadataField("Resolution", f"{width}x{height}"))

    _append_optional(fields, "Duration", _format_duration(format_info.get("duration")))
    _append_optional(fields, "Video Codec", video_stream.get("codec_name"))
    _append_optional(fields, "Pixel Format", video_stream.get("pix_fmt"))
    _append_optional(fields, "Created At", tags.get("creation_time"))
    _append_optional(fields, "Description", tags.get("description") or tags.get("comment"))
    _append_optional(fields, "Creator", tags.get("artist") or tags.get("author"))
    _append_optional(fields, "Keywords", tags.get("keywords"))

    return MediaMetadata(fields)


def _base_fields(path: Path, media_type: MediaType, size_bytes: int) -> list[MetadataField]:
    stat = path.stat()
    return [
        MetadataField("Path", str(path)),
        MetadataField("Type", media_type.value),
        MetadataField("Format", path.suffix.lower().lstrip(".") or "unknown"),
        MetadataField("File Size", _format_size(size_bytes)),
        MetadataField("Filesystem Created At", _format_timestamp(_created_timestamp(stat))),
        MetadataField("Modified At", _format_timestamp(stat.st_mtime)),
    ]


def _named_exif(image: Image.Image) -> dict[str, Any]:
    raw_exif = image.getexif()
    named: dict[str, Any] = {}
    for tag_id, value in raw_exif.items():
        name = EXIF_TAGS.get(tag_id, str(tag_id))
        if name == "GPSInfo":
            named[name] = {
                GPS_TAGS.get(gps_id, str(gps_id)): gps_value
                for gps_id, gps_value in raw_exif.get_ifd(tag_id).items()
            }
        else:
            named[name] = _decode_exif_value(value)
    return named


def _decode_exif_value(value: Any) -> Any:
    if isinstance(value, bytes):
        for encoding in ("utf-16le", "utf-8"):
            try:
                return value.decode(encoding).rstrip("\x00")
            except UnicodeDecodeError:
                continue
    return value


def _image_resolution(image: Image.Image, exif: dict[str, Any]) -> tuple[str | None, str | None]:
    x_resolution = exif.get("XResolution")
    y_resolution = exif.get("YResolution")
    if x_resolution and y_resolution:
        return str(x_resolution), str(y_resolution)

    dpi = image.info.get("dpi")
    if dpi and len(dpi) >= 2:
        return str(dpi[0]), str(dpi[1])
    return None, None


def _gps_location(gps: Any) -> str | None:
    if not isinstance(gps, dict):
        return None
    lat = _gps_coordinate(gps.get("GPSLatitude"), gps.get("GPSLatitudeRef"))
    lon = _gps_coordinate(gps.get("GPSLongitude"), gps.get("GPSLongitudeRef"))
    if lat is None or lon is None:
        return None
    return f"{lat:.6f}, {lon:.6f}"


def _gps_coordinate(value: Any, ref: Any) -> float | None:
    if not value or len(value) != 3:
        return None
    degrees, minutes, seconds = (_ratio_to_float(part) for part in value)
    coordinate = degrees + minutes / 60 + seconds / 3600
    if ref in {"S", "W"}:
        coordinate *= -1
    return coordinate


def _ratio_to_float(value: Any) -> float:
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        return float(value.numerator) / float(value.denominator)
    return float(value)


def _ffprobe_json(path: Path) -> dict[str, Any]:
    try:
        output = run_capture(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ]
        )
    except Exception:
        return {}
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}


def _first_value(values: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = values.get(key)
        if value:
            return str(value)
    return None


def _append_optional(fields: list[MetadataField], label: str, value: Any) -> None:
    if value is not None and value != "":
        fields.append(MetadataField(label, str(value)))


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / 1024 / 1024:.1f} MB"


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).isoformat(timespec="seconds")


def _created_timestamp(stat: Any) -> float:
    return getattr(stat, "st_birthtime", stat.st_ctime)


def _format_duration(value: Any) -> str | None:
    if value is None:
        return None
    try:
        seconds = float(value)
    except (TypeError, ValueError):
        return None
    return f"{seconds:.2f}s"


def _lower_keys(values: Any) -> dict[str, Any]:
    if not isinstance(values, dict):
        return {}
    return {str(key).lower(): value for key, value in values.items()}
