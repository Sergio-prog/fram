from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

from fram.core.errors import InvalidOperation, UnsupportedFormat
from fram.core.media import VECTOR_EXTENSIONS
from fram.core.operations import (
    Anchor,
    BlurParams,
    ConvertParams,
    CropParams,
    FlipParams,
    GrayscaleParams,
    ImageCompressParams,
    Operation,
    OperationName,
    ResizeMode,
    ResizeParams,
    RotateParams,
    StripMetadataParams,
)
from fram.core.processors.base import MediaProcessor
from fram.utils.files import ensure_parent_dir

IMAGE_OUTPUT_FORMATS = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


class ImageProcessor(MediaProcessor):
    def run(self, input_path: Path, operations: list[Operation], output_path: Path) -> Path:
        if input_path.suffix.lower() in VECTOR_EXTENSIONS:
            raise UnsupportedFormat(
                "SVG rasterization/editing is planned, but not implemented in v1."
            )

        ensure_parent_dir(output_path)
        with Image.open(input_path) as source:
            image = ImageOps.exif_transpose(source)
            save_options: dict[str, object] = {}
            forced_format: str | None = None

            for operation in operations:
                image, next_format, next_options = self.apply(image, operation)
                forced_format = next_format or forced_format
                save_options.update(next_options)

            output_format = forced_format or IMAGE_OUTPUT_FORMATS.get(output_path.suffix.lower())
            if output_format is None:
                raise UnsupportedFormat(f"Unsupported image output format: {output_path.suffix}")

            if output_format == "JPEG" and image.mode in {"RGBA", "P"}:
                image = image.convert("RGB")

            image.save(output_path, format=output_format, **save_options)
            return output_path

    def apply(
        self,
        image: Image.Image,
        operation: Operation,
    ) -> tuple[Image.Image, str | None, dict[str, object]]:
        match operation.name:
            case OperationName.RESIZE:
                return self.resize(image, self.expect(operation.params, ResizeParams)), None, {}
            case OperationName.CROP:
                return self.crop(image, self.expect(operation.params, CropParams)), None, {}
            case OperationName.COMPRESS:
                params = self.expect(operation.params, ImageCompressParams)
                self.validate_quality(params.quality)
                return image, None, {"quality": params.quality, "optimize": params.optimize}
            case OperationName.CONVERT:
                params = self.expect(operation.params, ConvertParams)
                return image, self.normalize_format(params.format), {}
            case OperationName.ROTATE:
                params = self.expect(operation.params, RotateParams)
                return image.rotate(-params.degrees, expand=True), None, {}
            case OperationName.FLIP:
                return self.flip(image, self.expect(operation.params, FlipParams)), None, {}
            case OperationName.STRIP_METADATA:
                self.expect(operation.params, StripMetadataParams)
                return image.copy(), None, {}
            case OperationName.BLUR:
                params = self.expect(operation.params, BlurParams)
                return image.filter(ImageFilter.GaussianBlur(params.radius)), None, {}
            case OperationName.GRAYSCALE:
                self.expect(operation.params, GrayscaleParams)
                return ImageOps.grayscale(image), None, {}
            case _:
                raise InvalidOperation(f"Operation {operation.name} is not valid for images.")

    def resize(self, image: Image.Image, params: ResizeParams) -> Image.Image:
        size = params.size.as_tuple()
        match params.mode:
            case ResizeMode.EXACT:
                return image.resize(size)
            case ResizeMode.FIT:
                copied = image.copy()
                copied.thumbnail(size)
                return copied
            case ResizeMode.FILL:
                return ImageOps.fit(image, size)
        raise InvalidOperation(f"Unsupported resize mode: {params.mode}")

    def crop(self, image: Image.Image, params: CropParams) -> Image.Image:
        width, height = image.size
        target_width, target_height = params.size.as_tuple()
        if target_width > width or target_height > height:
            raise InvalidOperation("Crop size cannot be larger than the image.")

        left, top = self.crop_origin(width, height, target_width, target_height, params.anchor)
        return image.crop((left, top, left + target_width, top + target_height))

    def crop_origin(
        self,
        width: int,
        height: int,
        target_width: int,
        target_height: int,
        anchor: Anchor,
    ) -> tuple[int, int]:
        horizontal = {
            Anchor.LEFT: 0,
            Anchor.TOP_LEFT: 0,
            Anchor.BOTTOM_LEFT: 0,
            Anchor.RIGHT: width - target_width,
            Anchor.TOP_RIGHT: width - target_width,
            Anchor.BOTTOM_RIGHT: width - target_width,
        }.get(anchor, (width - target_width) // 2)

        vertical = {
            Anchor.TOP: 0,
            Anchor.TOP_LEFT: 0,
            Anchor.TOP_RIGHT: 0,
            Anchor.BOTTOM: height - target_height,
            Anchor.BOTTOM_LEFT: height - target_height,
            Anchor.BOTTOM_RIGHT: height - target_height,
        }.get(anchor, (height - target_height) // 2)

        return horizontal, vertical

    def flip(self, image: Image.Image, params: FlipParams) -> Image.Image:
        result = image
        if params.horizontal:
            result = ImageOps.mirror(result)
        if params.vertical:
            result = ImageOps.flip(result)
        return result

    def normalize_format(self, value: str) -> str:
        normalized = value.lower().lstrip(".")
        formats = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "webp": "WEBP"}
        if normalized not in formats:
            raise UnsupportedFormat(f"Unsupported image format: {value}")
        return formats[normalized]

    def validate_quality(self, quality: int) -> None:
        if quality < 1 or quality > 100:
            raise InvalidOperation("Image quality must be between 1 and 100.")
