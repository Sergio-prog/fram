from PIL import Image

from fram.core.operation_factory import adjust, background, sharpen, upscale, watermark
from fram.core.processors.image import ImageProcessor


def test_image_processor_applies_new_image_operations(tmp_path) -> None:
    input_path = tmp_path / "input.png"
    output_path = tmp_path / "output.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 128)).save(input_path)

    ImageProcessor().run(
        input_path,
        [
            background("white"),
            adjust(brightness=1.1, contrast=1.1),
            sharpen(2),
            upscale(2),
            watermark("FRAM", size=8),
        ],
        output_path,
    )

    with Image.open(output_path) as result:
        assert result.size == (16, 16)
        assert result.mode == "RGBA"
