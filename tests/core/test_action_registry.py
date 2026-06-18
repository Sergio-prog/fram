from fram.core.action_registry import ACTION_BY_NAME, actions_for_media, no_value_actions
from fram.core.media import MediaType


def test_actions_for_media_keeps_image_and_video_specific_actions() -> None:
    image_actions = actions_for_media(MediaType.IMAGE)
    video_actions = actions_for_media(MediaType.VIDEO)

    assert "resize" in image_actions
    assert "resize" in video_actions
    assert "cut" not in image_actions
    assert "cut" in video_actions


def test_action_registry_exposes_adapter_metadata() -> None:
    assert ACTION_BY_NAME["resize"].cli_label
    assert ACTION_BY_NAME["resize"].bot_label
    assert ACTION_BY_NAME["resize"].help_text
    assert ACTION_BY_NAME["resize"].presets
    assert "strip-metadata" in no_value_actions()
