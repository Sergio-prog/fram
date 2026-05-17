from fram.bot import messages


def test_channel_link_is_available_in_markdown_and_html() -> None:
    assert messages.CHANNEL_MARKDOWN == "📣 [Channel](https://t.me/there_is_no_meme)"
    assert "https://t.me/there_is_no_meme" in messages.CHANNEL_HTML


def test_welcome_mentions_fram_and_channel() -> None:
    text = messages.welcome()

    assert "Fram" in text
    assert messages.CHANNEL_HTML in text

