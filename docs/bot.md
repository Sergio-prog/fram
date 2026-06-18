# Telegram Bot

Bot framework: aiogram 3.

Structure:

```text
fram/bot/main.py
fram/bot/handlers/
fram/bot/keyboards/
fram/bot/states/
fram/bot/services/
```

Modes:

- polling by default
- webhook when `FRAM_BOT_MODE=webhook`

The bot downloads media to `FRAM_WORK_DIR/bot`, builds typed operations from user choices, calls the core pipeline, sends the result as a document, then cleans temp files.

Supported flow:

```text
media -> action keyboard -> params/confirm -> add more or run -> result
```

Message copy includes the author channel link:

```text
📣 [Channel](https://t.me/there_is_no_meme)
```

The bot can collect multiple operations for one media file before running the shared pipeline.

The bot exposes the same core operation family where a short text prompt can represent params.
Generated outputs such as extracted frames, extracted audio, converted files, and GIFs choose a matching
default file suffix.
