# Fram

A compact media workshop for your terminal, API, and Telegram.

Fram crops, resizes, compresses, and converts images; cuts, resizes, crops, compresses, and changes FPS for videos. The CLI, FastAPI app, and Telegram bot use the same typed processing core.

## Status

Early hobby project. The strict CLI, API, Telegram bot flow, and basic interactive TUI exist.

## Install

```bash
uv sync
```

System dependency:

```bash
ffmpeg -version
```

## CLI

Strict commands:

```bash
fram info image.jpg
fram resize image.jpg 128x128 -o image-small.jpg
fram crop image.jpg 128x128 --anchor center -o avatar.jpg
fram compress-image image.jpg --quality 80 -o compressed.webp
fram convert image.png webp -o image.webp
fram rotate image.jpg 90 -o rotated.jpg
fram flip image.jpg --horizontal -o flipped.jpg

fram cut video.mp4 --start 00:00:05 --end 00:00:12 -o clip.mp4
fram fps video.mp4 24 -o video-24fps.mp4
fram compress-video video.mp4 --crf 24 --preset medium -o smaller.mp4
fram strip-audio video.mp4 -o silent.mp4
```

Help works both ways:

```bash
fram resize --help
fram help resize
```

Interactive mode:

```bash
fram
fram image.jpg
fram video.mp4
```

Interactive preview uses terminal image protocols through `textual-image`; videos show an extracted frame.

TUI shortcuts:

- `i`: toggle detailed info
- `a`: focus actions
- `d`: drop last operation
- `Tab`: switch active cut edge
- `Left` / `Right`: move active cut edge
- `r`: run
- `q`: quit

## API

Run locally:

```bash
uvicorn fram.api.main:app --reload
```

Token auth is optional. If `FRAM_API_TOKEN` is set, requests must include:

```http
Authorization: Bearer <token>
```

Process media:

```bash
curl -F "file=@image.jpg" \
  -F 'operations=[{"name":"resize","size":"128x128","mode":"fit"}]' \
  http://localhost:8000/media/process
```

## Telegram Bot

Set `FRAM_BOT_TOKEN`, then:

```bash
python -m fram.bot.main
```

Polling is the default. Webhook mode uses `FRAM_BOT_MODE=webhook` and `FRAM_BOT_WEBHOOK_URL`.

## Tests

```bash
uv run --group dev python -m pytest
```

## Supported Media

Images:

- input: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`
- output: `jpg`, `png`, `webp`
- SVG is detected, but true SVG editing is deferred.

Videos:

- input: common FFmpeg-readable formats like `mp4`, `mov`, `mkv`, `webm`, `avi`, `gif`
- output: depends on output suffix and local FFmpeg codecs

## Docs

- [Architecture](docs/architecture.md)
- [CLI](docs/cli.md)
- [API](docs/api.md)
- [Bot](docs/bot.md)
- [Media Support](docs/media-support.md)
- [Roadmap](docs/roadmap.md)
