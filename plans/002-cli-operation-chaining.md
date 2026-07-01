# Plan 002: Add `fram do` operation chaining to the CLI

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. If anything
> in the "STOP conditions" section occurs, stop and report — do not improvise. When
> done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat 7e1a3e5..HEAD -- fram/cli/main.py fram/cli/commands.py fram/core fram/core/operation_factory.py`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it as a STOP
> condition.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: LOW (purely additive — a new command + a new core module)
- **Depends on**: none (independent of 001)
- **Category**: direction / dx
- **Planned at**: commit `7e1a3e5`, 2026-06-30

## Why this matters

The processing core already runs a **list** of operations in one pass:
`Pipeline.run(input_path, operations: list[Operation], output_path)` and both
`ImageProcessor` / `VideoProcessor` iterate over `operations`. Every adapter except the CLI
exploits this. The CLI exposes exactly **one** operation per invocation (see
`fram/cli/commands.py`: every `*_file` function calls `run_pipeline(input_path, [single_op], output)`).
So a user who wants "resize → grayscale → convert to webp" must run three commands and
manage two intermediate files, re-encoding three times. Chaining is the single highest-value
CLI gap, and the hard part (multi-op execution) is already built and tested. This plan adds a
`fram do INPUT STEP... -o OUTPUT` command that runs an ordered chain in **one** pass, and a
small core parser that turns text steps into `Operation` objects — a parser that plan 004
(recipes) will reuse.

## Current state

- `fram/core/pipeline.py` already accepts a list:
  ```python
  def run_pipeline(input_path: Path, operations: list[Operation], output_path: Path) -> Path:
      return Pipeline().run(input_path, operations, output_path)
  ```
- `fram/core/media.py` exposes `MediaType` and `detect_media_type(path) -> MediaType`
  (used by `Pipeline.processor_for`). Confirm the exact import with:
  `grep -nE "def detect_media_type|class MediaType|IMAGE|VIDEO" fram/core/media.py`
- `fram/core/operation_factory.py` re-exports operation builders: `resize, crop, convert,
  rotate, flip, strip_metadata, blur, grayscale, adjust, sharpen, watermark, upscale,
  auto_orient, background, image_compress, video_compress, cut, fps, strip_audio,
  extract_audio, extract_frame, gif, speed, reverse, mute_audio, thumbnail, contact_sheet,
  extract_subtitles`. Each returns an `Operation`.
- `fram/core/errors.py` defines `FramError` (base) and `InvalidOperation(FramError)`. The
  CLI catches `FramError` and exits 1 (`fram/cli/main.py` `_print_result`).
- **Existing text→operation grammar to mirror.** A parser with the exact behavior you need
  already exists (it will be deleted by plan 001 with the bot, so you are re-creating it in
  core, not importing it). Its shape, from `fram/bot/services/operations.py`:
  ```python
  def build_operation(action: str, media_type: MediaType, raw_value: str | None = None) -> Operation:
      value = (raw_value or "").strip()
      if action == "resize":
          return resize(_required(value, "Send a size like 128x128."))
      if action == "crop":
          return _build_crop(value)            # "128x128" or "128x128 center"
      if action == "compress":                 # image -> image_compress(quality), video -> video_compress(crf)
          ...
      if action == "flip":
          return _build_flip(value)            # horizontal | vertical | both | h | v
      ...  # one branch per action; raises InvalidOperation on bad/missing params
  ```
  with helpers `_required`, `_int_value(value, msg)`, `_float_value(value, msg)` that raise
  `InvalidOperation`. **You will copy this logic into a new core module** (Step 1) — do not
  import from `fram/bot` (it may already be deleted by plan 001).
- `fram/cli/commands.py` is where CLI command bodies live (thin wrappers over
  `run_pipeline`). `fram/cli/main.py` defines the Typer app and `@app.command()` functions
  plus `_print_result(action)` which runs the callable, catches `FramError`, echoes the
  result, and exits 1 on error.
- `fram/utils/files.py`:
  ```python
  def default_output_path(input_path: Path, suffix: str | None = None) -> Path:
      output_suffix = suffix or input_path.suffix
      return input_path.with_name(f"{input_path.stem}.fram{output_suffix}")
  ```
- `fram/core/output.py` `default_output_for_operations(input_path, operations)` picks a
  suffix from the **last** operation (e.g. convert → its format, gif → `.gif`). Use this for
  the chain's default output so a chain ending in `convert webp` defaults to `.webp`.

Conventions: no comments (clean-code style); Conventional Commits; type hints everywhere;
`Annotated[...]` Typer options as in `fram/cli/main.py`. Match them.

## The `fram do` interface (target behavior)

```
fram do INPUT STEP [STEP ...] [-o OUTPUT]
```

- `INPUT` — path to one media file.
- Each `STEP` is **one shell argument** of the form `"ACTION"` or `"ACTION VALUE"`, where
  `ACTION` is an action name from the registry and `VALUE` is the same space-separated
  parameter string the grammar above accepts. Because a step with a space must be one arg,
  the user quotes it. Examples:
  ```bash
  fram do photo.jpg "resize 800x800" grayscale "convert webp" -o thumb.webp
  fram do clip.mp4 "cut 5 10" "fps 24" "compress 26" -o short.mp4
  fram do photo.png strip-metadata auto-orient            # no -o: defaults near input
  ```
- Media type is detected once from `INPUT` (chains run on a single file; mixing image+video
  ops is rejected by the processor as today).
- Default output (no `-o`): `default_output_for_operations(INPUT, operations)` so the suffix
  follows the final operation.

## Commands you will need

| Purpose   | Command                                                       | Expected on success        |
|-----------|---------------------------------------------------------------|----------------------------|
| Tests     | `uv run --all-extras --group dev python -m pytest -q`         | all pass (89 + new)        |
| Lint      | `uv run --all-extras --group dev ruff check .`                | exit 0                     |
| CLI smoke | `uv run fram do --help`                                       | exit 0, usage prints       |
| Run one   | `uv run fram do <file> "<step>" -o <out>`                     | prints output path, file exists |

## Scope

**In scope** (create/modify only these):
- `fram/core/text_operations.py` (**create**) — the text→operation parser.
- `fram/cli/commands.py` (**modify**) — add `do_chain(...)` command body.
- `fram/cli/main.py` (**modify**) — add the `@app.command("do")` Typer command and add
  `"do"` to the `COMMAND_NAMES` set near the top. **Also fix the stale Typer app help
  string**: line ~49 reads `help="Compact media editing from terminal, API, and Telegram."`
  — change it to remove the API/Telegram reference, e.g.
  `help="Compact media editing for your terminal and agent automation."` (the bot and API
  were removed; this string is the last user-visible reference to them).
- `tests/core/test_text_operations.py` (**create**) — parser tests.
- `tests/cli/test_do_command.py` (**create**) — end-to-end chain test on a real image.

**Out of scope** (do NOT touch):
- The existing per-operation commands (`resize`, `crop`, …) — leave them exactly as they
  are; `do` is additive.
- `fram/core/pipeline.py`, the processors, the operation factories — the core already
  supports lists; do not modify it.
- `fram/api`, `fram/bot` — do not import from them (they may be deleted by plan 001).
- The interactive TUI (`fram/cli/interactive/`) — out of scope.

## Git workflow

- Branch: `advisor/002-cli-operation-chaining`
- Commit style: Conventional Commits, e.g. `feat: add fram do operation chaining`.
- Do NOT push or open a PR unless instructed.

## Steps

### Step 1: Create the core text→operation parser

Create `fram/core/text_operations.py`. It must expose:

```python
def build_operation(action: str, media_type: MediaType, raw_value: str | None = None) -> Operation: ...
def parse_chain(steps: list[str], media_type: MediaType) -> list[Operation]: ...
```

- `build_operation` re-creates the grammar described in "Current state": one branch per
  action name, using the operation builders from `fram.core.operation_factory`, raising
  `fram.core.errors.InvalidOperation` for unknown actions or bad/missing params. Cover the
  **same action set** the registry defines — read it from
  `fram/core/action_registry.py` (`ACTION_BY_NAME` keys / `ACTION_SPECS`). Note the registry
  uses the single name `compress` and resolves image vs. video by `media_type` (image →
  `image_compress(quality=...)`, video → `video_compress(crf=...)`); preserve that.
  Copy the helper functions `_required`, `_int_value`, `_float_value`, and the per-action
  `_build_*` helpers (`_build_crop`, `_build_compress`, `_build_cut`, `_build_flip`,
  `_build_gif`, `_build_adjust`, `_build_watermark`, `_build_contact_sheet`) as shown in the
  bot grammar. Do not add comments.
- `parse_chain(steps, media_type)` splits each step string into `action, value` on the
  first whitespace (`step.split(maxsplit=1)`), then returns
  `[build_operation(action, media_type, value) for ...]`. An empty `steps` list must raise
  `InvalidOperation("Provide at least one operation.")`.

**Verify**:
```
uv run python -c "from fram.core.text_operations import parse_chain, build_operation; from fram.core.media import MediaType; print([op.name for op in parse_chain(['resize 64x64','grayscale','convert webp'], MediaType.IMAGE)])"
```
→ prints a list of three operation names (resize, grayscale, convert).

### Step 2: Add the `do_chain` command body in `commands.py`

In `fram/cli/commands.py`, add:

```python
from fram.core.media import detect_media_type
from fram.core.output import default_output_for_operations
from fram.core.text_operations import parse_chain


def do_chain(input_path: Path, steps: list[str], output_path: Path | None) -> Path:
    media_type = detect_media_type(input_path)
    operations = parse_chain(steps, media_type)
    output = output_path or default_output_for_operations(input_path, operations)
    return run_pipeline(input_path, operations, output)
```

Place the imports with the other `from fram.core...` imports at the top (match the existing
import grouping). `run_pipeline` is already imported in this file.

**Verify**: `uv run python -c "from fram.cli.commands import do_chain"` → exits 0, no output.

### Step 3: Register the `do` Typer command in `main.py`

In `fram/cli/main.py`:
1. Add `"do"` to the `COMMAND_NAMES` set (so the bare-arg interactive dispatch in `main()`
   does not mistake `do` for a file path).
2. Add the command, matching the `Annotated` style used by neighbors:

```python
@app.command("do")
def do(
    file: Path,
    steps: Annotated[list[str], typer.Argument(help='Operations, e.g. "resize 800x800" grayscale "convert webp".')],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.do_chain(file, steps, output))
```

`Path`, `Annotated`, `typer`, and `commands` are already imported in `main.py`.

**Verify**:
```
uv run fram do --help
```
→ exits 0 and shows `FILE` and `STEPS...` arguments plus the `--output` option.

### Step 4: Manual end-to-end smoke on a real image

Use a checked-in test image (e.g. `media/for_test.png` — confirm it exists with `ls media`).
```
uv run fram do media/for_test.png "resize 64x64" grayscale "convert webp" -o /tmp/fram_chain.webp
```
**Verify**: command exits 0, prints `/tmp/fram_chain.webp`, and
`uv run python -c "from PIL import Image; im=Image.open('/tmp/fram_chain.webp'); print(im.size, im.format)"`
prints a size no larger than `(64, 64)` and format `WEBP`. Then delete `/tmp/fram_chain.webp`.

> If `media/for_test.png` does not exist, pick any other image under `media/` (e.g.
> `media/landscape.png`); if none exist, STOP and report.

## Test plan

Model parser tests after `tests/bot/test_operation_parsing.py` (same assertion style:
build, then assert `isinstance(op.params, XParams)` and field values). If plan 001 already
deleted that file, the **structure** to follow is still: import the builder, call it, assert
on `op.name` / `op.params`. Use `fram/core/operations.py` param types.

Create `tests/core/test_text_operations.py` covering:
- `parse_chain(["resize 64x64", "grayscale", "convert webp"], MediaType.IMAGE)` → 3 ops with
  names RESIZE, GRAYSCALE, CONVERT (use `OperationName` from `fram.core.operations`).
- `build_operation("compress", MediaType.IMAGE, "80")` → `ImageCompressParams(quality=80)`;
  `build_operation("compress", MediaType.VIDEO, "26")` → `VideoCompressParams(crf=26)`.
- `build_operation("crop", MediaType.IMAGE, "128x128 top-left")` → `CropParams` with anchor
  `top-left`.
- Error cases: `parse_chain([], MediaType.IMAGE)` raises `InvalidOperation`;
  `build_operation("fps", MediaType.VIDEO, "fast")` raises `InvalidOperation`;
  `build_operation("nonsense", MediaType.IMAGE)` raises `InvalidOperation`.

Create `tests/cli/test_do_command.py`:
- Look at an existing CLI test for the harness pattern first:
  `tests/cli/test_interactive_app.py` (how it constructs paths / uses tmp). For invoking the
  Typer command, use `typer.testing.CliRunner` against `fram.cli.main.app`, or call
  `fram.cli.commands.do_chain` directly with a `tmp_path` output and a small generated image
  (`PIL.Image.new("RGB", (10, 10)).save(tmp_path / "in.png")`). Prefer calling `do_chain`
  directly for a fast, FFmpeg-free image test.
- Case: a 2-step image chain (`["resize 4x4", "convert webp"]`) produces an output file that
  exists and opens as WEBP with size ≤ (4, 4).

Verification: `uv run --all-extras --group dev python -m pytest -q` → all pass, including the
new tests.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `fram/core/text_operations.py` exists and exports `build_operation` and `parse_chain`
- [ ] `uv run fram do --help` exits 0
- [ ] `uv run --all-extras --group dev ruff check .` exits 0
- [ ] `uv run --all-extras --group dev python -m pytest -q` passes, with the new
      `tests/core/test_text_operations.py` and `tests/cli/test_do_command.py` collected and green
- [ ] `grep -nE "fram\.(api|bot)" fram/core/text_operations.py fram/cli/commands.py` → no output
- [ ] `grep -niE "API, and Telegram|Telegram" fram/cli/main.py` → no output (stale help string fixed)
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row for 002 updated

## STOP conditions

Stop and report back (do not improvise) if:

- The action set in `fram/core/action_registry.py` differs from what the bot grammar in
  "Current state" handles, in a way you cannot reconcile (e.g. a new action with no builder).
- `Pipeline`/`run_pipeline` no longer accepts `list[Operation]` (drift).
- A 2-operation image chain fails to run in Step 4 for reasons other than a missing test
  image.
- You find yourself wanting to modify a processor or the pipeline to make chaining work —
  it should already work; if it doesn't, the assumption is wrong, so STOP.

## Maintenance notes

- Plan 004 (recipes) reuses `parse_chain` to expand a saved recipe's step list. Keep
  `parse_chain`'s signature stable (`list[str], MediaType -> list[Operation]`).
- Deferred follow-up (not in this plan): a `--json` / machine-readable result for `do`
  (output path, applied ops) to make chains agent-consumable. Worth doing after this lands;
  see `plans/README.md` "considered/deferred".
- Reviewer should scrutinize: that `do` reuses the exact builders the single-op commands use
  (no divergent parameter handling), and that error messages from `InvalidOperation`
  surface cleanly through `_print_result` (exit 1, message on stderr).
- The step grammar is space-separated within one quoted arg. If a future param needs spaces
  *and* sub-fields, revisit the grammar before extending it ad hoc.
