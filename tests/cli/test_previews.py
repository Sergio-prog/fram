from PIL import Image

from fram.cli.interactive.previews import image_to_ascii, render_image_preview


def test_image_to_ascii_uses_requested_dimensions() -> None:
    image = Image.new("RGB", (10, 10), color="white")

    preview = image_to_ascii(image, width=8, height=4)

    lines = preview.splitlines()
    assert len(lines) == 4
    assert all(len(line) <= 8 for line in lines)


def test_render_image_preview(tmp_path) -> None:
    path = tmp_path / "image.png"
    Image.new("RGB", (10, 10), color="black").save(path)

    preview = render_image_preview(path, width=8, height=4)

    assert len(preview.splitlines()) == 4
