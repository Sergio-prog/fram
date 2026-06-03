# 🖼️ Fram

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CLI: Typer](https://img.shields.io/badge/CLI-Typer-111827)](https://typer.tiangolo.com/)
[![Media: FFmpeg](https://img.shields.io/badge/media-FFmpeg-007808?logo=ffmpeg&logoColor=white)](https://ffmpeg.org/)

A compact media workshop for your terminal, API, and Telegram.

Fram crops, resizes, compresses, and converts images; cuts, resizes, crops, compresses, changes FPS, strips audio, extracts frames, and makes GIFs from videos. The CLI, FastAPI app, and Telegram bot use the same typed processing core.

> Early hobby project. The strict CLI is the main focus right now; the API, Telegram bot flow, and basic interactive TUI also exist.

## Highlights

- Scriptable CLI commands for image and video edits.
- Interactive terminal UI for quick manual workflows.
- Shared core used by CLI, API, and Telegram bot.
- FFmpeg-backed video processing with Pillow-backed image operations.
- Small codebase intended to stay hackable.

## Install

Fram requires Python 3.11+ and FFmpeg. For manual global installs, use either `uv` or `pipx`.

```bash
ffmpeg -version
uv --version
pipx --version
```

Install with the script:

```bash
curl -LsSf https://fram.serhiifotex.dev/install.sh | sh
```

Homebrew support is planned through a tap, which will install FFmpeg automatically:

```bash
brew tap Sergio-prog/fram
brew install fram
```

Manual install with `uv tool`:

```bash
uv tool install git+https://github.com/Sergio-prog/fram.git
```

Manual install with `pipx`:

```bash
pipx install git+https://github.com/Sergio-prog/fram.git
```

After the first PyPI release, the manual commands become:

```bash
uv tool install fram
pipx install fram
```

From a local checkout:

```bash
scripts/install.sh
uv tool install .
pipx install .
```

For development:

```bash
uv --version
uv sync --all-extras
uv run fram --help
```

## Quick Start

```bash
fram info image.jpg
fram resize image.jpg 128x128 -o image-small.jpg
fram convert image.png webp -o image.webp

fram cut video.mp4 --start 00:00:05 --end 00:00:12 -o clip.mp4
fram gif video.mp4 --fps 12 --width 480 -o clip.gif
fram strip-audio video.mp4 -o silent.mp4
```

Help works both ways:

```bash
fram resize --help
fram help resize
```

## CLI Commands

### Images

```bash
fram resize image.jpg 128x128 -o image-small.jpg
fram crop image.jpg 128x128 --anchor center -o avatar.jpg
fram compress-image image.jpg --quality 80 -o compressed.webp
fram convert image.png webp -o image.webp
fram rotate image.jpg 90 -o rotated.jpg
fram flip image.jpg --horizontal -o flipped.jpg
fram strip-metadata image.jpg -o clean.jpg
fram blur image.jpg --radius 2 -o blurred.jpg
fram grayscale image.jpg -o gray.jpg
```

### Videos

```bash
fram cut video.mp4 --start 00:00:05 --end 00:00:12 -o clip.mp4
fram cut video.mp4 --start 5 --duration 10 -o clip.mp4
fram fps video.mp4 24 -o video-24fps.mp4
fram compress-video video.mp4 --crf 24 --preset medium -o smaller.mp4
fram strip-audio video.mp4 -o silent.mp4
fram extract-audio video.mp4 -o audio.m4a
fram extract-frame video.mp4 --at 00:00:05 -o frame.png
fram gif video.mp4 --fps 12 --width 480 -o clip.gif
fram speed video.mp4 2 -o fast.mp4
fram reverse video.mp4 --no-audio -o reversed.mp4
fram grayscale video.mp4 -o gray.mp4
```

## Interactive Mode

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

Install the API extra when running from a checkout:

```bash
uv sync --extra api
```

Run locally:

```bash
uv run uvicorn fram.api.main:app --reload
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

Install the bot extra when running from a checkout:

```bash
uv sync --extra bot
```

Set `FRAM_BOT_TOKEN`, then:

```bash
uv run python -m fram.bot.main
```

Polling is the default. Webhook mode uses `FRAM_BOT_MODE=webhook` and `FRAM_BOT_WEBHOOK_URL`.

## Supported Media

Images:

- input: `jpg`, `jpeg`, `png`, `webp`, `bmp`, `tif`, `tiff`
- output: `jpg`, `png`, `webp`
- SVG is detected, but true SVG editing is deferred.

Videos:

- input: common FFmpeg-readable formats like `mp4`, `mov`, `mkv`, `webm`, `avi`, `gif`
- output: depends on output suffix and local FFmpeg codecs

## Development

```bash
uv sync --all-extras
uv run --all-extras --group dev python -m pytest
uv run --all-extras --group dev ruff check .
```

Docs:

- [Architecture](docs/architecture.md)
- [CLI](docs/cli.md)
- [API](docs/api.md)
- [Bot](docs/bot.md)
- [Media Support](docs/media-support.md)
- [Roadmap](docs/roadmap.md)
- [Releasing](docs/releasing.md)

## License

MIT. See [LICENSE](LICENSE).
