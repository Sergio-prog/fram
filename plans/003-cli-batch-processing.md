# Plan 003: Add batch / glob processing to the CLI

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. If anything
> in the "STOP conditions" section occurs, stop and report — do not improvise. When
> done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat e13d2c4..HEAD -- fram/cli/main.py fram/cli/commands.py fram/utils/files.py fram/core`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it as a STOP
> condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW-MED (new command; must define output-naming and partial-failure rules clearly)
- **Depends on**: 002 (soft — **now MET**; `parse_chain` is on `main`)
- **Category**: direction / dx
- **Planned at**: commit `e13d2c4`, 2026-06-30 (rebased 2026-07-01 after 001+002 merged)

## Why this matters

Every CLI command takes exactly one `file: Path` (see `fram/cli/main.py` — all ~30
commands). There is no way to process a folder or a set of files in one invocation: a user
re-encoding a photo shoot must loop in their shell, and shell globbing does not cover
recursive walks, is awkward on Windows, and gives no per-file output-naming control or
summary. For a tool branded "a compact media workshop" — and increasingly aimed at
agent/automation use — batch is the workflow people reach for first. This plan adds a
`fram batch` command that applies one operation (or, when plan 002 has landed, a `do`-style
chain) to many inputs, writing each output to a destination directory with a templated name,
and reporting a per-file summary with a meaningful exit code.

## Current state

- `fram/cli/commands.py` — every `*_file(input_path, ..., output_path)` returns the output
  `Path`. `do_chain(input_path, steps, output_path)` exists **iff** plan 002 has landed
  (`grep -n "def do_chain" fram/cli/commands.py`). All of them ultimately call
  `run_pipeline(input_path, operations, output)`.
- `fram/core/text_operations.py` — exists **iff** plan 002 landed. Exposes
  `parse_chain(steps: list[str], media_type) -> list[Operation]` and
  `build_operation(action, media_type, raw_value)`. Confirm with `ls fram/core/text_operations.py`.
- `fram/core/media.py` — `detect_media_type(path) -> MediaType`, `MediaType.{IMAGE,VIDEO}`.
  Also check whether it exposes a "is this a supported media file" predicate or a set of
  known extensions (`grep -nE "EXTENSION|SUFFIX|def detect_media_type|VECTOR" fram/core/media.py`);
  you need to skip non-media files when walking a directory.
- `fram/utils/files.py`:
  ```python
  def default_output_path(input_path: Path, suffix: str | None = None) -> Path:
      output_suffix = suffix or input_path.suffix
      return input_path.with_name(f"{input_path.stem}.fram{output_suffix}")
  ```
- `fram/cli/main.py` — Typer app; `_print_result(action)` runs a callable, catches
  `FramError`, echoes the result, exits 1 on error. `COMMAND_NAMES` set lists every command
  name (used by `main()` to distinguish a command from a file path passed to interactive
  mode) — you must add `"batch"` to it.
- `fram/core/errors.py` — `FramError` base, `InvalidOperation`. The processors raise
  `FramError` subclasses on bad input.

Conventions: no comments; Conventional Commits; `Annotated[...]` Typer options; type hints.

## The `fram batch` interface (target behavior)

```
fram batch SOURCE... --op "ACTION VALUE" [--op "ACTION VALUE" ...] \
           --out-dir DIR [--recursive] [--on-error skip|stop] [--dry-run]
```

- `SOURCE...` — one or more files and/or directories. Directories are scanned for media
  files (top level only, unless `--recursive`). Non-media files are skipped (with a noted
  count). Globs may also be pre-expanded by the shell; both work.
- `--op` (repeatable) — each value is one chain step in the same grammar plan 002 defines
  (`"resize 800x800"`, `grayscale`, `"convert webp"`). The ordered list of `--op` values is
  the chain applied to every input. **At least one `--op` is required.**
- `--out-dir DIR` — required. Each input's output is written to `DIR / <templated name>`.
  The default template is the same `{stem}.fram{suffix}` rule as `default_output_path`, but
  placed under `DIR` instead of next to the input. `DIR` is created if missing.
- `--recursive` — recurse into subdirectories when a SOURCE is a directory.
- `--on-error skip|stop` (default `skip`) — on a per-file failure, either continue to the
  next file (collect the error) or abort immediately.
- `--dry-run` — list the inputs that would be processed and their planned output paths;
  process nothing.
- **Exit code**: 0 if every processed file succeeded; 1 if any file failed (even under
  `skip`), so scripts/agents can detect partial failure. A summary line is always printed:
  `Processed N, failed M, skipped K (non-media).`

Each input's media type is detected individually (`detect_media_type`), so a batch can mix
images and videos as long as each operation is valid for that file's type; a file whose
operation is invalid for its type fails that file (skip or stop per `--on-error`).

## Commands you will need

| Purpose   | Command                                                       | Expected on success         |
|-----------|---------------------------------------------------------------|-----------------------------|
| Tests     | `uv run --all-extras --group dev python -m pytest -q`         | all pass (prev + new)       |
| Lint      | `uv run --all-extras --group dev ruff check .`                | exit 0                      |
| CLI smoke | `uv run fram batch --help`                                    | exit 0, usage prints        |

## Scope

**In scope** (create/modify only these):
- `fram/cli/batch.py` (**create**) — input collection + per-file run loop + summary result.
- `fram/cli/main.py` (**modify**) — add `@app.command("batch")` and add `"batch"` to
  `COMMAND_NAMES`.
- `tests/cli/test_batch.py` (**create**).

**Out of scope** (do NOT touch):
- Existing single-file commands — `batch` is additive.
- The processors / pipeline / operation factories.
- `fram/utils/files.py` — reuse `default_output_path`; do not change its contract.
- `fram/api`, `fram/bot` — do not import (may be deleted by plan 001).

## Soft dependency on plan 002

> **Reconcile note (2026-07-01):** plan 002 is **merged to `main`** — `fram/core/text_operations.py`
> with `parse_chain` exists. Step 1 will resolve to `USE_CORE_PARSER`; the "not landed"
> fallback below is now dead and you should not need it. It is kept only as a safety net if a
> drift check shows the file missing.

`batch` needs to turn `--op` strings into operations. If plan 002 has landed,
`fram/core/text_operations.parse_chain` already does exactly this — **import and use it**.

If plan 002 has **not** landed (`fram/core/text_operations.py` absent), do **one** of:
- **Preferred**: implement plan 002 first, then return here.
- If you must proceed without 002, create a minimal `parse_chain` equivalent inside
  `fram/cli/batch.py` using the operation builders from `fram.core.operation_factory`
  (same grammar: split each `--op` on first whitespace into action + value). Mark this in
  your status note so it can be de-duplicated once 002 lands.

Decide which path applies in Step 1 and record it.

## Git workflow

- Branch: `advisor/003-cli-batch-processing`
- Commit style: Conventional Commits, e.g. `feat: add fram batch processing`.
- Do NOT push or open a PR unless instructed.

## Steps

### Step 1: Determine the parser source (002 landed or not)

```
ls fram/core/text_operations.py 2>/dev/null && echo "USE_CORE_PARSER" || echo "NO_CORE_PARSER"
```
Record the result. If `NO_CORE_PARSER`, re-read "Soft dependency on plan 002" and choose a
path before continuing.

### Step 2: Implement input collection in `fram/cli/batch.py`

Create `fram/cli/batch.py` with a function that expands SOURCEs into a deterministic, sorted
list of media files:

```python
def collect_inputs(sources: list[Path], recursive: bool) -> tuple[list[Path], int]:
    ...  # returns (media_files_sorted, skipped_non_media_count)
```

Rules:
- A SOURCE that is a file → include it if it is a media file (use `detect_media_type`; treat
  a file that raises/`None` as non-media and count it as skipped), else count skipped.
- A SOURCE that is a directory → iterate `path.rglob("*")` if `recursive` else `path.iterdir()`;
  include media files, count non-media as skipped, ignore subdirectories.
- A SOURCE that does not exist → raise `InvalidOperation(f"No such path: {source}")`.
- Sort the final list (`sorted(set(...))`) for deterministic output ordering.

> If `detect_media_type` raises on a non-media file instead of returning a sentinel, wrap
> the call in try/except `FramError` and treat an exception as "non-media, skip-count".

**Verify**: `uv run python -c "from fram.cli.batch import collect_inputs; print(collect_inputs([__import__('pathlib').Path('media')], False))"`
→ prints a tuple `(list_of_media_paths, skipped_int)` with the images under `media/`.

### Step 3: Implement the batch run loop + summary

In `fram/cli/batch.py` add:

```python
@dataclass
class BatchResult:
    processed: list[Path]
    failed: list[tuple[Path, str]]
    skipped: int

def run_batch(
    sources: list[Path],
    op_steps: list[str],
    out_dir: Path,
    recursive: bool,
    on_error: str,            # "skip" | "stop"
    dry_run: bool,
) -> BatchResult: ...
```

Behavior:
- `collect_inputs(...)` → inputs + skipped.
- If `not op_steps`: raise `InvalidOperation("Provide at least one --op.")`.
- For each input: `media_type = detect_media_type(input)`;
  `operations = parse_chain(op_steps, media_type)`;
  `output = out_dir / default_output_path(input, suffix=<from default_output_for_operations>).name`
  — i.e. compute the default-named output but relocate it under `out_dir`. Use
  `fram.core.output.default_output_for_operations(input, operations)` to get the right
  suffix, then take `.name` and join to `out_dir`.
- `dry_run`: collect planned `(input -> output)` pairs, process nothing, return a result with
  empty failed/processed but printable plan (echo the pairs in the command wrapper).
- Real run: `out_dir.mkdir(parents=True, exist_ok=True)`; call `run_pipeline(input,
  operations, output)`; on success append to `processed`; on `FramError` as `exc`, record
  `(input, str(exc))` in `failed` and, if `on_error == "stop"`, break.
- Return `BatchResult`.

**Verify**: unit-exercise via Step 5 tests.

### Step 4: Register the `batch` Typer command

In `fram/cli/main.py` add `"batch"` to `COMMAND_NAMES`, then:

```python
@app.command("batch")
def batch(
    sources: Annotated[list[Path], typer.Argument(help="Files and/or directories.")],
    op: Annotated[list[str], typer.Option("--op", help='Chain step, e.g. "resize 800x800". Repeatable.')],
    out_dir: Annotated[Path, typer.Option("--out-dir", help="Destination directory.")],
    recursive: Annotated[bool, typer.Option("--recursive", "-R")] = False,
    on_error: Annotated[str, typer.Option("--on-error", help="skip | stop")] = "skip",
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    ...
```

The body should call `run_batch(...)`, print the per-file plan (dry-run) or the summary
line `Processed N, failed M, skipped K (non-media).`, list each failed file with its error
on stderr, and `raise typer.Exit(1)` if `failed` is non-empty (or wrap in the existing
`FramError` handling for the `InvalidOperation` raised on bad args). Import `commands`/`batch`
helpers as needed; `typer`, `Annotated`, `Path` already imported.

**Verify**: `uv run fram batch --help` → exits 0 and shows `SOURCES...`, `--op`, `--out-dir`,
`--recursive`, `--on-error`, `--dry-run`.

### Step 5: Manual smoke

```
uv run fram batch media --op "resize 32x32" --op "convert webp" --out-dir /tmp/fram_batch --dry-run
uv run fram batch media --op "resize 32x32" --op "convert webp" --out-dir /tmp/fram_batch
ls /tmp/fram_batch
```
**Verify**: dry-run lists planned outputs and writes nothing; the real run creates
`/tmp/fram_batch` with one `.webp` per image under `media/`, prints a summary line, and exits
0 (assuming all images succeed). Clean up `/tmp/fram_batch` afterward.

> `media/` contains both source images and already-processed `*.fram.png` files; processing
> them all is fine for a smoke test. If any file legitimately fails (e.g. an unsupported
> format), confirm the exit code is 1 and the failure is listed — that is correct behavior,
> not a bug.

## Test plan

Create `tests/cli/test_batch.py`. Use `tmp_path` and generate small images with PIL
(`PIL.Image.new("RGB", (8, 8)).save(tmp_path / "a.png")`), so tests need no FFmpeg and no
fixtures. Model harness/setup on `tests/cli/test_interactive_app.py`.

Cover:
- **Happy path**: two generated images in `tmp_path`, `run_batch([tmp_path], ["resize 4x4",
  "convert webp"], out_dir, recursive=False, on_error="skip", dry_run=False)` →
  `len(processed) == 2`, `failed == []`, both outputs exist under `out_dir` and open as WEBP.
- **Skip non-media**: add a `tmp_path / "notes.txt"` → result `skipped == 1`, processed only
  the images.
- **Recursive**: an image in `tmp_path / "sub"` is found only when `recursive=True`.
- **Empty ops**: `run_batch(..., op_steps=[], ...)` raises `InvalidOperation`.
- **on_error stop vs skip**: include one input that fails its operation (e.g. an op invalid
  for that media type) and assert `stop` halts early while `skip` continues and the final
  exit indicator (non-empty `failed`) is set.
- **dry_run**: writes no files (`out_dir` empty or absent) and reports the planned pairs.

Verification: `uv run --all-extras --group dev python -m pytest -q tests/cli/test_batch.py`
→ all new tests pass; then the full suite passes.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `fram/cli/batch.py` exists with `collect_inputs` and `run_batch`
- [ ] `uv run fram batch --help` exits 0
- [ ] `uv run --all-extras --group dev ruff check .` exits 0
- [ ] `uv run --all-extras --group dev python -m pytest -q` passes incl. `tests/cli/test_batch.py`
- [ ] A batch with one failing file exits 1 and prints the failure (verified by a test)
- [ ] `grep -nE "fram\.(api|bot)" fram/cli/batch.py` → no output
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row for 003 updated

## STOP conditions

Stop and report back (do not improvise) if:

- `detect_media_type` cannot be used to classify/skip arbitrary files and there is no
  extension set or predicate to fall back on (you need *some* reliable way to skip non-media).
- Plan 002 is not landed and you are not authorized to either land it first or inline a
  minimal parser (re-read the soft-dependency section; if still blocked, report).
- The default-output naming (`default_output_path` / `default_output_for_operations`)
  produces collisions for distinct inputs that map to the same output name under `--out-dir`
  — if you detect a real collision risk in tests, STOP and report so a naming rule
  (e.g. preserve relative subpath) can be decided rather than silently overwriting.

## Maintenance notes

- Output naming intentionally flattens into `--out-dir`. If recursive batches over nested
  trees need to preserve structure, that is a deliberate follow-up (mirror the relative
  path under `--out-dir`) — call it out in review rather than bolting it on.
- Once plan 002's `parse_chain` is the single source of truth, ensure any temporary inline
  parser added under the soft-dependency path is removed (de-dup).
- Agent-usage angle: the non-zero exit on partial failure plus the machine-greppable summary
  line are deliberate so an orchestrating agent can detect failures. Keep the summary format
  stable; consider a `--json` summary as a future enhancement (tracked in `plans/README.md`).
- Reviewer should scrutinize: deterministic ordering of inputs, that `--out-dir` is created
  exactly once, and that `--on-error stop` truly stops before processing further files.
