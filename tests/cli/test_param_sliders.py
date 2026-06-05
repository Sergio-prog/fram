from fram.cli.interactive.param_sliders import NumericParamSliders, slider_specs_for
from fram.core.media import MediaType


def test_slider_specs_for_numeric_actions() -> None:
    image_compress = slider_specs_for("compress", MediaType.IMAGE)
    video_compress = slider_specs_for("compress", MediaType.VIDEO)

    assert image_compress[0].key == "quality"
    assert image_compress[0].default == 82
    assert video_compress[0].key == "crf"
    assert video_compress[0].default == 23
    assert [spec.key for spec in slider_specs_for("adjust", MediaType.IMAGE)] == [
        "brightness",
        "contrast",
    ]


def test_numeric_param_sliders_write_input_value() -> None:
    sliders = NumericParamSliders()
    sliders.configure("adjust", MediaType.IMAGE)

    sliders.move_active(1)
    sliders.switch_active(1)
    sliders.move_active(2)

    assert sliders.input_value() == "1.05 1.1"


def test_numeric_param_sliders_clamp_values() -> None:
    sliders = NumericParamSliders()
    sliders.configure("fps", MediaType.VIDEO)

    for _ in range(100):
        sliders.move_active(1)

    assert sliders.input_value() == "60"
