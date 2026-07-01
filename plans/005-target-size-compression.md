# Plan 005: Add target-file-size compression (`fram fit-size`)

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. If anything
> in the "STOP conditions" section occurs, stop and report — do not improvise. When
> done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat e13d2c4..HEAD -- fram/cli/main.py fram/cli/commands.py fram/core fram/utils/sizes.py`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it as a STOP
> condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: MED (image half is robust; video half does an FFmpeg bitrate encode — verify on a real clip)
- **Depends on**: none
- **Category**: direction
- **Planned at**: commit `e13d2c4`, 2026-06-30 (rebased 2026-07-01 after 001+002 merged)

## Why this matters

`compress-image` and `compress-video` take a fixed quality/CRF (`fram/cli/main.py` lines
~131–146): the user must guess a number and re-run until the file is small enough. The common
real-world need is the inverse — "make this fit under 2 MB" for Discord, email, an upload
limit, or an agent that must satisfy a size budget. This is on the project roadmap
(`docs/roadmap.md` "Next": *Add target-file-size compression*). This plan adds
`fram fit-size INPUT --max-size SIZE -o OUTPUT` that searches compression settings until the
output is at or under the requested size (or reports the smallest it could achieve).

## Current state

- Image compression flows through `image_compress(quality=...)` →
  `OperationName.COMPRESS` in `fram/core/processors/image.py`:
  ```python
  case OperationName.COMPRESS:
      params = self.expect(operation.params, ImageCompressParams)
      self.validate_quality(params.quality)          # 1..100
      return image, None, {"quality": params.quality, "optimize": params.optimize}
  ```
  i.e. quality is a Pillow save option; lower quality ⇒ smaller file. Re-running the
  pipeline with different quality values is cheap (in-memory Pillow encode).
- Video compression flows through `video_compress(crf=..., preset=...)` →
  `OperationName.COMPRESS` in `fram/core/processors/video.py`:
  ```python
  case OperationName.COMPRESS:
      params = self.expect(operation.params, VideoCompressParams)
      if params.crf < 0 or params.crf > 51: raise InvalidOperation(...)
      plan.output_args.extend(["-crf", str(params.crf), "-preset", params.preset])
  ```
  CRF is quality-targeted, **not** size-targeted; you cannot hit an exact size with CRF in one
  shot. For a size target, the reliable FFmpeg approach is a **target average bitrate** derived
  from the clip duration: `bitrate ≈ target_bytes * 8 / duration_seconds`, minus an audio
  allowance.
- `fram/core/probe.py` already gives duration:
  ```python
  def probe_duration_seconds(path: Path) -> float | None: ...
  ```
- `fram/core/pipeline.py` `run_pipeline(input, operations, output)` returns the output `Path`.
  `fram/cli/commands.py` holds command bodies; `fram/cli/main.py` holds Typer commands and
  `_print_result`. `fram/core/errors.py` has `FramError` / `InvalidOperation` /
  `ProcessingFailed`.
- `fram/utils/sizes.py` **already defines** `parse_size(value: str) -> Size` — but that parses
  **image dimensions** (`"128x128"` → a `Size` with width/height), **not** file sizes in bytes.
  ⚠️ Do **not** reuse or overload it, and do **not** name your new function `parse_size` — that
  would collide. Your byte-size parser must be a **new, differently-named** function:
  `parse_byte_size(text: str) -> int`. (This was verified at reconcile time on `e13d2c4`.)
- `fram/utils/process.py` has `run_command(args)` (used by `VideoProcessor`) and `run_capture`
  (used by `probe.py`).

Conventions: no comments; Conventional Commits; type hints; `Annotated[...]` Typer options.

## Interface (target)

```
fram fit-size INPUT --max-size SIZE [-o OUTPUT] [--min-quality N]
```

- `INPUT` — one image or video.
- `--max-size SIZE` — human size string: `2MB`, `1.5MB`, `500KB`, `750000` (bytes). Required.
- `-o OUTPUT` — output path; defaults like the other commands
  (`default_output_path(INPUT)`), keeping the input's container/format.
- `--min-quality N` (images only, default e.g. 20) — floor for the quality search so output
  never degrades below this; if even `N` exceeds the budget, write the `N`-quality result and
  report that the target could not be met.

Behavior contract:
- On success: output ≤ `--max-size`; print the output path and the achieved size + setting,
  e.g. `out.jpg (1.8 MB at quality 64)`.
- On "couldn't hit target": still writes the smallest result found, prints a clear warning,
  and exits **1** so scripts/agents detect the miss. (Decide this is the contract; keep it.)

## Algorithm

**Images** — binary search on Pillow quality:
1. `lo, hi = min_quality, 95`. Track `best` = smallest output that is ≤ target (None if none).
2. Each probe: run `run_pipeline(input, [image_compress(quality=mid)], tmp_out)`, measure
   `tmp_out.stat().st_size`.
   - if size ≤ target: record as `best`, search higher quality (`lo = mid + 1`) to maximize
     quality while staying under budget.
   - else: search lower (`hi = mid - 1`).
3. If `best` found, re-encode (or copy) at `best.quality` to the real OUTPUT; else encode at
   `min_quality` to OUTPUT and flag "target not met".
   Bound the loop to ≤ ~8 iterations (binary search over ≤100 values converges well within
   that). Use a temp file in the same dir / system temp for probes; clean it up.

**Video** — single target-bitrate encode from duration:
1. `duration = probe_duration_seconds(input)`; if `None`, raise
   `InvalidOperation("Cannot determine video duration for size targeting.")`.
2. `target_bits = target_bytes * 8`. Reserve an audio budget (e.g. assume 128 kbps audio:
   `audio_bits = 128_000 * duration`); `video_bits = max(target_bits - audio_bits, target_bits * 0.5)`
   to avoid a non-positive video budget on tiny targets.
3. `video_bitrate = int(video_bits / duration)` (bits per second). Build an FFmpeg encode that
   constrains average bitrate:
   `-b:v <video_bitrate> -maxrate <~1.5x> -bufsize <~2x> -preset medium` (and a sane audio
   bitrate `-b:a 128k`). This is one encode (not a multi-pass loop). Implement it as a new
   small helper rather than overloading the CRF `COMPRESS` path.
4. Measure output size. If it still exceeds target by more than a small margin (e.g. >5%),
   that's a "target not met" → warn + exit 1 (do not loop re-encoding video; one encode is the
   scope here).

> Two-pass video encoding would hit the target more precisely but doubles encode time and adds
> a passlog file to manage. It is intentionally **out of scope**; the single-pass average
> bitrate is "good enough, stays close." Note this in the maintenance section.

## Implementation placement

To keep the core clean and avoid a new core `Operation` type, implement the search/bitrate
logic at the **command layer**:

- Image search: pure orchestration over the existing `image_compress` operation +
  `run_pipeline` + `stat()`. Put it in `fram/cli/commands.py` (or a new
  `fram/cli/fit_size.py` if it grows past ~40 lines — prefer a new module).
- Video bitrate encode: it needs FFmpeg args the current `VideoProcessor` does not expose
  (`-b:v`, `-maxrate`, `-bufsize`, `-b:a`). Add a focused helper that builds and runs that
  FFmpeg command via `fram.utils.process.run_command`, mirroring how `VideoProcessor` builds
  args (`["ffmpeg", "-y", "-i", input, ..., output]`). Keep it in the same new
  `fram/cli/fit_size.py`. Do **not** add a generic bitrate operation to the core in this plan.

## Commands you will need

| Purpose   | Command                                                       | Expected on success    |
|-----------|---------------------------------------------------------------|------------------------|
| Tests     | `uv run --all-extras --group dev python -m pytest -q`         | all pass (prev + new)  |
| Lint      | `uv run --all-extras --group dev ruff check .`                | exit 0                 |
| CLI smoke | `uv run fram fit-size --help`                                 | exit 0, usage prints   |
| ffprobe   | `ffprobe -version`                                            | exit 0 (needed for video) |

## Scope

**In scope** (create/modify only these):
- `fram/cli/fit_size.py` (**create**) — size parsing reuse, image binary search, video bitrate
  encode, a single `fit_size(input_path, max_size, output_path, min_quality)` entry point.
- `fram/utils/sizes.py` (**modify**) — add a **new** `parse_byte_size(text: str) -> int`
  (bytes). Do not touch the existing `parse_size(value) -> Size` (image dimensions).
- `fram/cli/main.py` (**modify**) — add `@app.command("fit-size")` and `"fit-size"` to
  `COMMAND_NAMES`.
- `tests/cli/test_fit_size.py` (**create**).
- `tests/utils/test_sizes.py` (**modify**) — add `parse_byte_size` tests alongside the
  existing `parse_size` (dimensions) tests.
- `docs/cli.md` and `docs/roadmap.md` (**modify**) — document the command; move the roadmap
  bullet from "Next" to done/remove it.

**Out of scope** (do NOT touch):
- The core processors' existing `COMPRESS` cases, `image_compress`/`video_compress` factories,
  pipeline — reuse, don't modify.
- Two-pass video encoding (explicitly deferred).
- `fram/api`, `fram/bot` (may be deleted by plan 001).

## Git workflow

- Branch: `advisor/005-target-size-compression`
- Commit style: Conventional Commits, e.g. `feat: add target-file-size compression`.
- Do NOT push or open a PR unless instructed.

## Steps

### Step 1: Size parsing

Read `fram/utils/sizes.py` first. It **already** has `parse_size(value) -> Size` for image
**dimensions** — leave it alone. Add a separate function:

```python
def parse_byte_size(text: str) -> int: ...   # "2MB"->2_000_000, "1.5MB", "500KB", "750000"; raises InvalidOperation on junk
```

Use decimal units (KB=1000, MB=1_000_000) — that matches how upload limits are usually
phrased; document this choice. Accept optional `B`/`KB`/`MB`/`GB` (case-insensitive), and a
bare integer = bytes. Raise `InvalidOperation` on unparseable input.

**Verify**:
```
uv run python -c "from fram.utils.sizes import parse_byte_size; print(parse_byte_size('2MB'), parse_byte_size('500KB'), parse_byte_size('750000'))"
```
→ `2000000 500000 750000`.

### Step 2: Image binary search

In `fram/cli/fit_size.py`, implement the image branch per "Algorithm → Images" using
`image_compress` (import from `fram.core.operation_factory`), `run_pipeline`
(`fram.core.pipeline`), and a temp probe file. Return the chosen quality and whether the
target was met.

**Verify** via Step 5 tests (deterministic with a generated noisy image).

### Step 3: Video bitrate encode

In `fram/cli/fit_size.py`, implement the video branch per "Algorithm → Video": probe duration,
compute bitrate, build and run the FFmpeg command via `run_command`. Raise `InvalidOperation`
when duration is unknown.

**Verify** via Step 6 manual smoke (needs a real video).

### Step 4: Wire the `fit-size` command

Add the entry point `fit_size(input_path, max_size, output_path, min_quality)` that detects
media type (`detect_media_type`) and dispatches to the image or video branch, writes OUTPUT
(default `default_output_path(input)`), and returns a human result string like
`"out.jpg (1.8 MB at quality 64)"` or a "target not met" variant. In `fram/cli/main.py` add
`"fit-size"` to `COMMAND_NAMES` and:

```python
@app.command("fit-size")
def fit_size(
    file: Path,
    max_size: Annotated[str, typer.Option("--max-size", help="e.g. 2MB, 500KB.")],
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
    min_quality: Annotated[int, typer.Option("--min-quality", help="Image quality floor.")] = 20,
) -> None:
    ...
```

For the "target not met" exit-1 contract, the command body cannot use the plain
`_print_result` (which always echoes then exits 0). Either return a `(message, met: bool)`
from the entry point and have the command echo + `raise typer.Exit(1)` when `not met`, or
raise a dedicated path. Keep `FramError` → exit 1 behavior for bad input.

**Verify**: `uv run fram fit-size --help` exits 0, shows `--max-size`, `--output`,
`--min-quality`.

### Step 5: Image end-to-end smoke

Generate a noisy image (compresses non-trivially), then target a small size:
```
uv run python -c "from PIL import Image; import os; from random import Random; r=Random(0); im=Image.new('RGB',(400,400)); im.putdata([(r.randrange(256),r.randrange(256),r.randrange(256)) for _ in range(400*400)]); im.save('/tmp/fram_noise.jpg', quality=95)"
uv run fram fit-size /tmp/fram_noise.jpg --max-size 30KB -o /tmp/fram_fit.jpg
uv run python -c "import os; print(os.path.getsize('/tmp/fram_fit.jpg'))"
rm -f /tmp/fram_noise.jpg /tmp/fram_fit.jpg
```
**Verify**: command exits 0 and the printed/measured output size is ≤ 30000 bytes. (Random
RGB is near-incompressible; if 30KB is unmet, the command should still write a file and exit 1
— that is also a valid observation of correct behavior. Pick a target you can satisfy for the
exit-0 path, e.g. raise to 60KB, to confirm the success path.)

> Do not assert exact sizes in automated tests — encoders vary across platforms. Assert the
> **inequality** (output ≤ target) on the success path.

### Step 6: Video end-to-end smoke (requires a real clip)

If a short test video exists in the repo (`ls media | grep -iE "\.(mp4|mov|mkv|webm)$"`), use
it; otherwise generate one:
```
ffmpeg -y -f lavfi -i testsrc=duration=3:size=320x240:rate=15 -pix_fmt yuv420p /tmp/fram_clip.mp4
uv run fram fit-size /tmp/fram_clip.mp4 --max-size 200KB -o /tmp/fram_clip_small.mp4
uv run python -c "import os; print(os.path.getsize('/tmp/fram_clip_small.mp4'))"
rm -f /tmp/fram_clip.mp4 /tmp/fram_clip_small.mp4
```
**Verify**: command exits 0 and the output size is in the neighborhood of the target (single
pass — expect it close to / under 200KB; if it overshoots by >5% the command warns and exits
1, which is the defined contract). If `ffmpeg`/`ffprobe` are unavailable, SKIP this step and
note it.

## Test plan

- `tests/utils/test_sizes.py` (`parse_byte_size`): `2MB`→2_000_000, `1.5MB`,
  `500KB`/`500kb`, bare `750000`, and `InvalidOperation` on `"abc"`/`""`. Model on existing
  cases in that file (do not disturb the existing `parse_size` dimension tests).
- `tests/cli/test_fit_size.py` (image only — FFmpeg-free, deterministic):
  - Generate a 200×200 random-noise JPEG in `tmp_path`. Call the image entry point /
    `fit_size(...)` with a target that is satisfiable (e.g. derive: first encode at quality 20,
    take that size + slack as the target) and assert the output exists and
    `output.stat().st_size <= target`.
  - Target met returns a result indicating success; an impossibly small target (e.g. 1 byte)
    returns the "not met" indicator and still writes a file at `min_quality`.
  - **Do not** put video in the automated suite (keep tests FFmpeg-free and fast); video is
    covered by the Step 6 manual smoke. Mention this gap in the maintenance notes.

Verification: `uv run --all-extras --group dev python -m pytest -q` → all pass incl. new tests.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `uv run fram fit-size --help` exits 0
- [ ] Image: on a satisfiable target the output file size ≤ target (verified by a test)
- [ ] Image: on an impossible target a file is still written and the command exits 1
- [ ] `uv run --all-extras --group dev ruff check .` exits 0
- [ ] `uv run --all-extras --group dev python -m pytest -q` passes incl. new tests
- [ ] No new core `Operation` type added (`git diff --stat` shows no change to
      `fram/core/operations.py` / `operation_models/` / processors)
- [ ] `grep -nE "fram\.(api|bot)" fram/cli/fit_size.py` → no output
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row for 005 updated

## STOP conditions

Stop and report back (do not improvise) if:

- The existing `fram/utils/sizes.py` `parse_size(value) -> Size` has changed shape from what
  this plan describes, or you cannot add `parse_byte_size` without disturbing it — report
  rather than silently changing behavior. (Never rename or repurpose the existing `parse_size`.)
- The image binary search does not converge within ~8 iterations (suggests the encode size is
  not monotonic in quality on this platform — surface it).
- Video duration cannot be probed (`probe_duration_seconds` returns `None`) for a normal clip
  in Step 6 — that breaks the size math; report.
- You find yourself needing to add two-pass encoding or a new core operation to make video
  work — both are explicitly out of scope; STOP and report so scope can be re-decided.

## Maintenance notes

- **Decimal vs binary units**: this plan uses decimal MB/KB (1 MB = 1,000,000 B). If users
  expect binary (MiB), that is a one-line change in `parse_byte_size` plus doc update — flag in
  review.
- **Video precision**: single-pass average bitrate is approximate. If exact-size video becomes
  important, the upgrade path is two-pass encoding (manage a passlog file, two `run_command`
  calls); deliberately deferred here.
- **Test coverage gap**: video `fit-size` is only manually smoke-tested (to keep the suite
  FFmpeg-free). A reviewer/maintainer should run Step 6 by hand when touching the video branch.
- Agent-usage angle: the exit-1-on-miss contract lets an agent detect when a size budget was
  not met instead of shipping an oversized file silently. Keep that contract stable.
- Reviewer should scrutinize: the audio-budget reservation (avoid non-positive video bitrate on
  tiny targets), temp-file cleanup in the image search, and the exit-code behavior on the
  "target not met" path.
