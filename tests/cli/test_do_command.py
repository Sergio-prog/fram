from pathlib import Path

from PIL import Image

from fram.cli.commands import do_chain


def test_do_chain_resize_and_convert(tmp_path: Path) -> None:
    input_path = tmp_path / "in.png"
    Image.new("RGB", (10, 10)).save(input_path)

    output = do_chain(input_path, ["resize 4x4", "convert webp"], None)

    assert output.exists()
    result = Image.open(output)
    assert result.format == "WEBP"
    assert result.size[0] <= 4
    assert result.size[1] <= 4
