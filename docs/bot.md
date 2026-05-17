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
media -> action keyboard -> params/confirm -> process -> result
```

Message copy includes the author channel link:

```text
📣 [Channel](https://t.me/there_is_no_meme)
```

Current gap: only one operation is applied per bot request. Multi-step bot pipelines can be added later.
