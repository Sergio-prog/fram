# Plan 004: Add named recipes (saved operation chains)

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. If anything
> in the "STOP conditions" section occurs, stop and report — do not improvise. When
> done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat e13d2c4..HEAD -- fram/cli fram/core/text_operations.py fram/utils`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it as a STOP
> condition.

## Status

- **Priority**: P2
- **Effort**: M
- **Risk**: LOW-MED (new config-file surface; keep schema simple and validated)
- **Depends on**: 002 (hard — **now MET**; `parse_chain` + `do_chain` are on `main`). Executable.
- **Category**: direction / dx
- **Planned at**: commit `e13d2c4`, 2026-06-30 (rebased 2026-07-01 after 001+002 merged)

## Why this matters

Today "presets" in Fram are only **TUI slider-value suggestions**
(`fram/core/action_registry.py` `ActionSpec.presets` — e.g. `("128x128 fit", ...)`); there is
no way to save a reusable, named operation **chain** and apply it by name. A user who runs the
same "make a web thumbnail" or "Instagram square" pipeline repeatedly must retype the whole
chain every time. Named recipes turn Fram from "a typed FFmpeg/Pillow wrapper you drive
manually" into "my media workshop with my saved workflows" — the differentiator for the
CLI-and-agent direction. A recipe is just a named list of the same step strings plan 002's
`do` already accepts, stored in a small user config file, so this builds directly on 002 with
no new processing logic.

## Current state

- Plan 002 added `fram/core/text_operations.py` with
  `parse_chain(steps: list[str], media_type) -> list[Operation]` and
  `build_operation(action, media_type, raw_value)`. **This plan requires it.** Confirm:
  `ls fram/core/text_operations.py` and
  `grep -n "def parse_chain" fram/core/text_operations.py`. If absent, STOP — do plan 002 first.
- Plan 002 added `fram do` (`fram/cli/main.py` `@app.command("do")`, body
  `fram.cli.commands.do_chain`). Recipes mirror this: an `apply` command resolves a recipe
  name to its steps, then runs the same `do_chain` path.
- `fram/cli/main.py` — Typer app, `COMMAND_NAMES` set, `_print_result`, `Annotated` option
  style. You will add `apply` and `recipes` commands and their names to `COMMAND_NAMES`.
- `fram/cli/commands.py` — `do_chain(input_path, steps, output_path)` exists from plan 002.
- `fram/core/errors.py` — `FramError`, `InvalidOperation`. Raise `InvalidOperation` for
  unknown recipe names and malformed config; the CLI maps `FramError` → exit 1.
- Python 3.11+ (`requires-python = ">=3.11"` in `pyproject.toml`), so `tomllib` is in the
  stdlib — use it to read TOML; **do not** add a dependency. There is no TOML *writer* in the
  stdlib, so the "save a recipe" path writes a tiny TOML document by hand (simple key/array
  lines) — see Step 3.
- No existing config-directory helper in the repo
  (`grep -rniE "config|XDG|home\(\)" fram/utils fram/core | grep -vi __pycache__` returns
  nothing relevant). You will add one.

Conventions: no comments; Conventional Commits; type hints; `Annotated[...]` Typer options.

## Recipe model & file format (target)

- Config file: `~/.config/fram/recipes.toml` (respect `$XDG_CONFIG_HOME` if set:
  `${XDG_CONFIG_HOME:-~/.config}/fram/recipes.toml`). Allow override via env var
  `FRAM_RECIPES_FILE` (absolute path) for testing and power users.
- Format: one TOML table per recipe, each with a `steps` array of step strings in the exact
  grammar plan 002 accepts:
  ```toml
  [recipes.web-thumb]
  steps = ["resize 800x800", "strip-metadata", "convert webp"]

  [recipes.ig-square]
  steps = ["crop 1080x1080 center", "convert jpg"]
  ```
- A recipe is media-type-agnostic at save time; validity is checked when applied (the
  `media_type` comes from the input file, exactly like `do`).

## CLI interface (target)

```
fram apply RECIPE INPUT [-o OUTPUT]        # run a saved recipe on one file
fram recipes list                          # list recipe names + their steps
fram recipes save NAME --op "STEP" [--op "STEP" ...]   # write/overwrite a recipe
fram recipes show NAME                     # print one recipe's steps
fram recipes remove NAME                   # delete a recipe
```

- `apply` defaults output the same way `do` does
  (`default_output_for_operations(input, operations)`).
- `recipes save` validates each step by parsing it (image media type as a smoke check) before
  writing, so a syntactically broken recipe cannot be saved.

## Commands you will need

| Purpose   | Command                                                       | Expected on success      |
|-----------|---------------------------------------------------------------|--------------------------|
| Tests     | `uv run --all-extras --group dev python -m pytest -q`         | all pass (prev + new)    |
| Lint      | `uv run --all-extras --group dev ruff check .`                | exit 0                   |
| CLI smoke | `uv run fram recipes --help` / `uv run fram apply --help`     | exit 0, usage prints     |

## Scope

**In scope** (create/modify only these):
- `fram/core/recipes.py` (**create**) — load/save/list/remove recipes; resolve a name to its
  `steps` list; config-path resolution honoring `FRAM_RECIPES_FILE` and `XDG_CONFIG_HOME`.
- `fram/cli/main.py` (**modify**) — add `apply` command and a `recipes` Typer sub-app (or
  `recipes-list` / `recipes-save` style commands if a sub-app is awkward); add the new names
  to `COMMAND_NAMES`.
- `tests/core/test_recipes.py` (**create**).
- `tests/cli/test_apply_command.py` (**create**).
- `docs/cli.md` (**modify**) — document recipes + apply (short section).

**Out of scope** (do NOT touch):
- `fram/core/action_registry.py` `presets` — those are TUI slider suggestions, a different
  concept; leave them.
- The processors / pipeline / operation factories / `text_operations.py` (reuse only).
- `fram/api`, `fram/bot` (may be deleted by plan 001).
- Adding any third-party TOML dependency — use stdlib `tomllib` for reads.

## Git workflow

- Branch: `advisor/004-named-recipes`
- Commit style: Conventional Commits, e.g. `feat: add named recipes`.
- Do NOT push or open a PR unless instructed.

## Steps

### Step 0: Confirm plan 002 is present

```
grep -n "def parse_chain" fram/core/text_operations.py && grep -n "def do_chain" fram/cli/commands.py
```
**Verify**: both print a match. If either is missing, **STOP** — plan 002 is a hard
dependency.

### Step 1: Implement `fram/core/recipes.py`

Expose:

```python
def recipes_file() -> Path: ...                       # FRAM_RECIPES_FILE > $XDG_CONFIG_HOME/fram/recipes.toml > ~/.config/fram/recipes.toml
def load_recipes() -> dict[str, list[str]]: ...        # {name: steps}; {} if file missing
def get_recipe(name: str) -> list[str]: ...            # raises InvalidOperation if unknown
def save_recipe(name: str, steps: list[str]) -> None:  # validates, writes file (creating dirs)
def remove_recipe(name: str) -> None: ...              # raises InvalidOperation if unknown
```

Rules:
- `recipes_file()`: if `os.environ.get("FRAM_RECIPES_FILE")` set, use it; else
  `Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "fram" / "recipes.toml"`.
- `load_recipes()`: if the file does not exist, return `{}`. Else read bytes, `tomllib.load`,
  read the `recipes` table; each entry must be a table with a `steps` list of strings.
  On malformed TOML or wrong shape, raise `InvalidOperation("Malformed recipes file: ...")`.
- `get_recipe(name)`: `load_recipes()[name]` or raise
  `InvalidOperation(f"Unknown recipe: {name}")`.
- `save_recipe(name, steps)`: validate each step by calling
  `parse_chain([step], MediaType.IMAGE)` for each step inside a try/except that re-raises a
  clear `InvalidOperation` (this catches typos like a bad action name; a video-only action
  will still validate structurally — that is acceptable, since validity is ultimately checked
  at apply time against the real media type). Load existing recipes, set/overwrite
  `recipes[name] = steps`, then **write** the whole file as TOML by hand:
  ```
  # for each name, steps in recipes:
  #   [recipes.<name>]
  #   steps = ["a", "b"]
  ```
  Escape any `"` and `\` in step strings when emitting the TOML array
  (`s.replace("\\", "\\\\").replace('"', '\\"')`). Create parent dirs
  (`recipes_file().parent.mkdir(parents=True, exist_ok=True)`).
  Reject a `name` containing a `.`, whitespace, or `[`/`]` (`InvalidOperation` — keep names
  TOML-bare-key-safe).
- `remove_recipe(name)`: load, `KeyError` → `InvalidOperation(f"Unknown recipe: {name}")`,
  else delete and rewrite the file.

**Verify**:
```
FRAM_RECIPES_FILE=/tmp/fram_recipes.toml uv run python -c "
from fram.core.recipes import save_recipe, get_recipe, load_recipes, remove_recipe
save_recipe('web-thumb', ['resize 800x800','convert webp'])
print(get_recipe('web-thumb'))
print(list(load_recipes()))
remove_recipe('web-thumb')
print(list(load_recipes()))
"
```
→ prints the steps, then `['web-thumb']`, then `[]`. Then `rm -f /tmp/fram_recipes.toml`.

### Step 2: Add the `apply` command

In `fram/cli/main.py`, add `"apply"` to `COMMAND_NAMES`, then:

```python
@app.command("apply")
def apply(
    recipe: Annotated[str, typer.Argument(help="Recipe name (see `fram recipes list`).")],
    file: Path,
    output: Annotated[Path | None, typer.Option("--output", "-o")] = None,
) -> None:
    _print_result(lambda: commands.do_chain(file, get_recipe(recipe), output))
```

Import `get_recipe` from `fram.core.recipes`. `do_chain` already handles parsing + default
output. The `InvalidOperation` raised by `get_recipe` for an unknown name flows through
`_print_result` → exit 1.

**Verify**: `uv run fram apply --help` exits 0 and shows `RECIPE`, `FILE`, `--output`.

### Step 3: Add the `recipes` management commands

Add a Typer sub-app for `recipes` (preferred) or individual commands. Sub-app pattern:

```python
recipes_app = typer.Typer(help="Manage saved operation recipes.")
app.add_typer(recipes_app, name="recipes")

@recipes_app.command("list")
def recipes_list() -> None: ...      # echo each "name: step1, step2" (or "No recipes." if empty)

@recipes_app.command("show")
def recipes_show(name: str) -> None: ...   # echo the recipe's steps; InvalidOperation if unknown

@recipes_app.command("save")
def recipes_save(
    name: str,
    op: Annotated[list[str], typer.Option("--op", help='Step, e.g. "resize 800x800". Repeatable.')],
) -> None: ...   # save_recipe(name, op); echo confirmation

@recipes_app.command("remove")
def recipes_remove(name: str) -> None: ...   # remove_recipe(name); echo confirmation
```

Add `"recipes"` to `COMMAND_NAMES`. Wrap the body calls so `FramError`/`InvalidOperation`
become exit 1 (reuse `_print_result` where the function returns a string, or replicate its
try/except). `recipes save` with no `--op` must error (`InvalidOperation("Provide at least
one --op.")`).

> If `app.add_typer` interacts badly with the custom `main()` dispatch in
> `fram/cli/main.py` (which intercepts `sys.argv` before calling `app(...)`), verify that
> `fram recipes list` still routes correctly. The `main()` function checks `args[0]` against
> `COMMAND_NAMES`; `recipes` must be in that set. Test it in Step 5. If sub-app routing
> fails, fall back to flat command names `recipes-list`, `recipes-save`, etc., and add each
> to `COMMAND_NAMES`.

**Verify**: `uv run fram recipes --help` (or the flat fallbacks) exits 0.

### Step 4: Document in `docs/cli.md`

Add a short "Recipes" section after the interactive section showing `recipes save`,
`recipes list`, and `apply`, plus the config-file location and `FRAM_RECIPES_FILE` override.
Keep it terse and example-driven, matching the file's existing style.

**Verify**: `grep -niE "recipe|fram apply" docs/cli.md` → at least one match.

### Step 5: Manual end-to-end smoke

```
export FRAM_RECIPES_FILE=/tmp/fram_recipes.toml
uv run fram recipes save web-thumb --op "resize 64x64" --op "convert webp"
uv run fram recipes list
uv run fram apply web-thumb media/for_test.png -o /tmp/fram_apply.webp
uv run python -c "from PIL import Image; im=Image.open('/tmp/fram_apply.webp'); print(im.size, im.format)"
uv run fram recipes remove web-thumb
unset FRAM_RECIPES_FILE
rm -f /tmp/fram_recipes.toml /tmp/fram_apply.webp
```
**Verify**: save confirms; list shows `web-thumb` with its steps; apply exits 0 and prints
the output path; the PIL line prints a size ≤ (64, 64) and format `WEBP`; remove confirms.
(If `media/for_test.png` is absent, use another image under `media/`.)

## Test plan

`tests/core/test_recipes.py` (no FFmpeg, no real config dir — drive everything through
`monkeypatch.setenv("FRAM_RECIPES_FILE", str(tmp_path / "recipes.toml"))`):
- save then load round-trips steps exactly (including a step containing a quote, to exercise
  escaping, e.g. `watermark "Hi there"` — note shell quoting is not relevant here; pass the
  raw string with an embedded `"`).
- `get_recipe` on unknown name raises `InvalidOperation`.
- `save_recipe` with an invalid step (`"bogus-action 1"`) raises `InvalidOperation` and does
  **not** create/modify the file.
- `remove_recipe` deletes and unknown-name remove raises `InvalidOperation`.
- `load_recipes()` on a missing file returns `{}`.
- overwrite: saving an existing name replaces its steps.

`tests/cli/test_apply_command.py` (model on `tests/cli/test_do_command.py` from plan 002):
- With `FRAM_RECIPES_FILE` pointed at a tmp file, save a recipe, then call
  `commands.do_chain(input_png, get_recipe("name"), out_path)` (or invoke the `apply`
  command via `CliRunner`) on a generated PIL image and assert the output exists and is the
  expected format/size.
- Applying an unknown recipe raises `InvalidOperation`.

Verification: `uv run --all-extras --group dev python -m pytest -q` → all pass incl. the new
files.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `fram/core/recipes.py` exists with `recipes_file`, `load_recipes`, `get_recipe`,
      `save_recipe`, `remove_recipe`
- [ ] `uv run fram apply --help` and `uv run fram recipes --help` (or flat fallbacks) exit 0
- [ ] `uv run --all-extras --group dev ruff check .` exits 0
- [ ] `uv run --all-extras --group dev python -m pytest -q` passes incl. the two new test files
- [ ] Recipes are stored as TOML and read back via stdlib `tomllib` (no new dependency:
      `grep -nE "toml" pyproject.toml` shows no added runtime dep)
- [ ] `grep -nE "fram\.(api|bot)" fram/core/recipes.py` → no output
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row for 004 updated

## STOP conditions

Stop and report back (do not improvise) if:

- Plan 002 (`parse_chain` / `do_chain`) is not present.
- Typer sub-app routing cannot be made to coexist with the custom `main()` argv dispatch and
  the flat-command fallback also fails.
- You find yourself wanting a TOML *writer* dependency — the hand-written emitter with
  escaping is intentional; if step strings need richer structure than a flat string array,
  STOP and report rather than redesigning the schema.

## Maintenance notes

- The recipe `steps` grammar is identical to `do`'s. If plan 002's step grammar changes,
  recipes inherit it for free — keep them coupled to `parse_chain`, never a second parser.
- Agent-usage angle: recipes give an agent a stable, named one-shot pipeline
  (`fram apply web-thumb in.jpg -o out.webp`). A future `--json` for `recipes list` would let
  an agent discover available recipes; tracked as deferred in `plans/README.md`.
- Combine with plan 003: `fram apply` over many files is the natural next ask — consider a
  `--recipe NAME` option on `batch` once both land (do not build it here).
- Reviewer should scrutinize: the hand-written TOML emitter's escaping (quotes/backslashes),
  config-path resolution honoring `FRAM_RECIPES_FILE` and `XDG_CONFIG_HOME`, and that
  `save_recipe` validates before writing (no half-written/broken recipe file).
