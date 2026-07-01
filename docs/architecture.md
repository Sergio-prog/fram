# Architecture

Fram has one shared core and one app adapter.

```text
fram/core/processors  class-based image/video processors
fram/core             typed operations, media detection, pipeline dispatch
fram/cli              Typer commands and Textual interactive UI
fram/utils            reusable helpers with no product decisions
```

The core accepts `Operation` objects with dataclass params, not loose dicts. The CLI translates user input into operations through `fram.core.operation_factory`.

`Pipeline` owns dispatch. `ImageProcessor` and `VideoProcessor` own operation execution.

Main rule: the CLI must not duplicate processing logic.
