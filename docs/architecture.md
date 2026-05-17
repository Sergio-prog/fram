# Architecture

Fram has one shared core and three app adapters.

```text
fram/core/processors  class-based image/video processors
fram/core             typed operations, media detection, pipeline dispatch
fram/cli              Typer commands and Textual interactive UI
fram/api              FastAPI routes and optional bearer auth
fram/bot              aiogram bot structure
fram/utils            reusable helpers with no product decisions
```

The core accepts `Operation` objects with dataclass params, not loose dicts. Apps translate user input into operations through `fram.core.operation_factory`.

`Pipeline` owns dispatch. `ImageProcessor` and `VideoProcessor` own operation execution.

Main rule: CLI, API, and bot must not duplicate processing logic.
