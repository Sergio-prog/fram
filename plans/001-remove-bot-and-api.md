# Plan 001: Remove the Telegram bot and HTTP API; refocus on CLI + agents

> **Executor instructions**: Follow this plan step by step. Run every verification
> command and confirm the expected result before moving to the next step. If anything
> in the "STOP conditions" section occurs, stop and report — do not improvise. When
> done, update the status row for this plan in `plans/README.md`.
>
> **Drift check (run first)**:
> `git diff --stat 7e1a3e5..HEAD -- fram/api fram/bot pyproject.toml README.md AGENTS.md .env.example docs tests`
> If any in-scope file changed since this plan was written, compare the "Current state"
> excerpts against the live code before proceeding; on a mismatch, treat it as a STOP
> condition.

## Status

- **Priority**: P1
- **Effort**: M
- **Risk**: MED (large deletion; must not break the CLI or the core)
- **Depends on**: none
- **Category**: tech-debt / direction
- **Planned at**: commit `7e1a3e5`, 2026-06-30

## Why this matters

Fram has three app adapters over one shared core: CLI, HTTP API (`fram/api`, FastAPI),
and Telegram bot (`fram/bot`, aiogram). The project owner has decided to focus the tool
on the **CLI and on agent/automation usage**, and considers the bot and API not useful in
practice. Carrying them costs real maintenance: two optional dependency sets
(`fastapi`/`uvicorn`/`python-multipart`, `aiogram`/`pydantic-settings`), duplicate
operation-parsing logic, extra docs, extra tests, and extra env configuration. Removing
them shrinks the surface area, removes web/credential attack surface (bearer token, bot
token, webhook URL), and lets every future change reason about one front end instead of
three. The shared core (`fram/core`), the CLI (`fram/cli`), and the utils (`fram/utils`)
are **untouched** and remain fully functional after this change.

## Current state

The two adapters to remove and everything that references them:

- `fram/api/` — FastAPI app. Files: `__init__.py`, `main.py`, `auth.py`, `schemas.py`,
  `settings.py`, `routes/` (`__init__.py`, `health.py`, `media.py`). Entry point is
  `fram/api/main.py`:
  ```python
  from fastapi import FastAPI
  from fram.api.routes import health, media
  app = FastAPI(title="Fram API", version="0.1.0")
  app.include_router(health.router)
  app.include_router(media.router)
  ```
- `fram/bot/` — aiogram bot. Files: `__init__.py`, `main.py`, `config.py`, `messages.py`,
  `handlers/` (`__init__.py`, `common.py`, `media.py`), `keyboards/` (`__init__.py`,
  `actions.py`), `services/` (`__init__.py`, `files.py`, `operations.py`, `processing.py`),
  `states/` (`__init__.py`, `media.py`).
- `tests/api/` — does **not** exist as a directory; API has no dedicated test dir. Confirm
  with `ls tests`. The bot tests live in `tests/bot/`: `test_operation_parsing.py`,
  `test_messages.py`. There may be a `tests/api/` — if present, it is in scope to delete.
- `pyproject.toml` — the optional-dependency groups to delete (lines ~27–36):
  ```toml
  [project.optional-dependencies]
  api = [
    "fastapi>=0.111",
    "python-multipart>=0.0.9",
    "uvicorn>=0.30",
  ]
  bot = [
    "aiogram>=3.4",
    "pydantic-settings>=2.2",
  ]
  ```
  The base `[project].dependencies`, `[dependency-groups].dev`, `[project.scripts]`
  (`fram = "fram.cli.main:main"`), `[tool.hatch...]`, and `[tool.ruff...]` blocks stay.
- `README.md` — sections to remove: `## API` (lines ~176–202) and `## Telegram Bot`
  (lines ~204–218). Also the description line ~14 and ~12 mention "API, and Telegram":
  > "A compact media workshop for your terminal, API, and Telegram."
  > "The CLI, FastAPI app, and Telegram bot use the same typed processing core."
  And the doc links block (lines ~243–249) links `docs/api.md` and `docs/bot.md`.
- `AGENTS.md` line ~6 mentions "The CLI, FastAPI app, and Telegram bot use the same typed
  processing core."
- `.env.example` — contains `FRAM_API_TOKEN`, `FRAM_BOT_TOKEN`, `FRAM_BOT_MODE`,
  `FRAM_BOT_WEBHOOK_URL`. Read it before editing (it is short).
- `docs/api.md`, `docs/bot.md` — delete entirely.
- `docs/architecture.md` lines ~9–10 describe `fram/api` and `fram/bot`.
- `docs/roadmap.md` lines ~7–8 mention "Basic FastAPI processing endpoint" and
  "Basic aiogram structure" under V1.

**Important — shared logic check:** The bot has its own text→operation parser at
`fram/bot/services/operations.py` (`build_operation`). Plan 002 introduces an independent
parser in `fram/core/text_operations.py`. **Nothing in `fram/core`, `fram/cli`, or
`fram/utils` imports from `fram/api` or `fram/bot`** — verified at planning time (see Step 1
grep). So deleting the two packages cannot break the CLI or core. Confirm this yourself in
Step 1; if the grep finds an import, STOP.

Repo conventions: commits follow Conventional Commits (see `git log --oneline`: `feat:`,
`chore:`). Comments are avoided (clean-code style). Match that.

## Commands you will need

| Purpose   | Command                                                        | Expected on success            |
|-----------|----------------------------------------------------------------|--------------------------------|
| Tests     | `uv run --all-extras --group dev python -m pytest -q`          | all pass (count drops, see below) |
| Lint      | `uv run --all-extras --group dev ruff check .`                 | exit 0, no errors              |
| CLI smoke | `uv run fram --help`                                           | exit 0, command list prints    |
| Import    | `uv run python -c "import fram.cli.main, fram.core.pipeline"`  | exit 0, no output              |

Baseline before you start: `uv run --all-extras --group dev python -m pytest -q` reports
**89 passed**. After removing `tests/bot/`, the count drops by the number of bot tests
(currently `test_operation_parsing.py` has ~13 and `test_messages.py` has a few). The exact
final number is not load-bearing — what matters is **0 failures** and **0 errors/import
collection errors**.

## Scope

**In scope** (delete or edit only these):
- Delete directory: `fram/api/`
- Delete directory: `fram/bot/`
- Delete directory: `tests/bot/` (and `tests/api/` if it exists)
- Delete files: `docs/api.md`, `docs/bot.md`
- Edit: `pyproject.toml` (remove `[project.optional-dependencies]` block)
- Edit: `README.md` (remove API + Bot sections, fix description + doc links)
- Edit: `AGENTS.md` (fix the description line)
- Edit: `.env.example` (remove API/bot env vars)
- Edit: `docs/architecture.md` (remove api/bot rows + adapter wording)
- Edit: `docs/roadmap.md` (remove the two V1 bullets)
- Edit: `uv.lock` only via the regeneration command in Step 6 — do **not** hand-edit it.

**Out of scope** (do NOT touch):
- `fram/core/`, `fram/cli/`, `fram/utils/`, `fram/updates.py`, `fram/__init__.py`,
  `fram/__main__.py` — the CLI and core stay exactly as they are.
- `fram/core/operation_factory.py` and `fram/api/schemas.py`'s pydantic specs: the API's
  `schemas.py` is deleted with `fram/api/`. Do **not** try to "rescue" it into core — plans
  002/004 build their own parsers. If you think something in `fram/api/schemas.py` is needed
  elsewhere, STOP and report instead of moving it.
- `.github/workflows/publish.yml`, `packaging/`, `scripts/install.sh` — verify they contain
  no api/bot references in Step 1; they were clean at planning time. Only edit if the grep
  in Step 1 shows a reference.

## Git workflow

- Branch: `advisor/001-remove-bot-and-api`
- Commit style: Conventional Commits, e.g. `chore: remove telegram bot and http api adapters`.
  One commit for the whole plan is fine; or split deletion vs. docs.
- Do NOT push or open a PR unless the operator instructed it.

## Steps

### Step 1: Confirm nothing the CLI/core needs imports the bot or api

Run:
```
grep -rnE "fram\.(api|bot)" fram/core fram/cli fram/utils fram/updates.py fram/__init__.py fram/__main__.py
```
**Verify**: no output (exit code 1 from grep = no matches). If there is ANY match, **STOP and
report** — a core/CLI file depends on code you are about to delete, and this plan's core
assumption is false.

Also run:
```
grep -rniE "fram\.(api|bot)|fastapi|aiogram|uvicorn" .github packaging scripts 2>/dev/null
```
**Verify**: no output. If matches appear, add those files to your edit list and remove the
references; if you are unsure how, STOP and report.

### Step 2: Delete the two adapter packages and their tests

```
git rm -r fram/api fram/bot tests/bot
[ -d tests/api ] && git rm -r tests/api || true
git rm docs/api.md docs/bot.md
```
**Verify**: `ls fram` shows `cli core utils` (plus `__init__.py`, `__main__.py`,
`updates.py`) and **no** `api` or `bot`. `ls tests` shows no `bot` (or `api`) dir.

### Step 3: Remove optional dependencies from `pyproject.toml`

Delete the entire `[project.optional-dependencies]` block shown in "Current state"
(the `api = [...]` and `bot = [...]` groups). Leave `[project].dependencies`,
`[dependency-groups]`, `[project.scripts]`, `[build-system]`, `[tool.hatch...]`, and
`[tool.ruff...]` intact.

**Verify**: `grep -nE "fastapi|aiogram|uvicorn|python-multipart|pydantic-settings|optional-dependencies" pyproject.toml`
→ no output.

### Step 4: Clean docs and metadata of api/bot references

Edit each file to remove only the api/bot content (keep everything else):

- `README.md`: delete the `## API` and `## Telegram Bot` sections in full. In the
  description near the top, change the two sentences so they describe the CLI (and the
  shared core) without naming the API or Telegram. In the docs-links list at the bottom,
  remove the `[API](docs/api.md)` and `[Bot](docs/bot.md)` lines.
- `AGENTS.md`: edit the line that says "The CLI, FastAPI app, and Telegram bot use the same
  typed processing core." to mention only the CLI / shared core.
- `.env.example`: remove the `FRAM_API_TOKEN`, `FRAM_BOT_TOKEN`, `FRAM_BOT_MODE`,
  `FRAM_BOT_WEBHOOK_URL` lines (and any now-empty comment headers for them). Keep any
  remaining CLI-relevant vars (e.g. `FRAM_WORK_DIR`, `FRAM_UPDATE_CHECK` if present).
- `docs/architecture.md`: remove the `fram/api` and `fram/bot` rows from the tree block and
  any sentence describing them as adapters; the doc should describe core + CLI.
- `docs/roadmap.md`: remove the "Basic FastAPI processing endpoint" and "Basic aiogram
  structure" bullets under V1.

**Verify**:
```
grep -rniE "fastapi|aiogram|uvicorn|telegram|FRAM_API|FRAM_BOT|docs/api\.md|docs/bot\.md" README.md AGENTS.md .env.example docs
```
→ no output. (A passing-mention of "bot" in unrelated prose is unlikely; if grep flags a
genuinely unrelated word, you may leave it, but `fastapi`/`aiogram`/`FRAM_API`/`FRAM_BOT`
must be gone.)

### Step 5: Verify the CLI and core still build and pass

```
uv run python -c "import fram.cli.main, fram.core.pipeline, fram.cli.commands"
uv run fram --help
uv run --all-extras --group dev ruff check .
uv run --all-extras --group dev python -m pytest -q
```
**Verify**: the import line prints nothing and exits 0; `fram --help` lists the commands;
ruff exits 0; pytest reports **0 failed, 0 errors** (total count is lower than 89 because
bot tests were removed — that is expected).

### Step 6: Regenerate the lockfile

The optional-dependency removal changes the resolved set. Regenerate `uv.lock` so it matches
`pyproject.toml` (do not hand-edit it):
```
uv lock
```
**Verify**: `grep -nE "fastapi|aiogram" uv.lock` → no output (these packages are no longer in
the locked set). `git status` shows `uv.lock` modified.

> If `uv lock` is unavailable or errors in this environment, STOP and report — do not
> hand-edit `uv.lock`.

## Test plan

This plan deletes code; it does not add behavior, so no new tests are written.

- The remaining suite (`tests/core`, `tests/cli`, `tests/utils`) must still pass with 0
  failures and 0 collection errors — this is the regression gate.
- Confirm no remaining test imports the deleted packages:
  `grep -rnE "fram\.(api|bot)" tests` → no output.

## Done criteria

Machine-checkable. ALL must hold:

- [ ] `fram/api/` and `fram/bot/` do not exist (`ls fram` shows neither)
- [ ] `grep -rnE "fram\.(api|bot)" fram tests` → no output
- [ ] `grep -nE "fastapi|aiogram|uvicorn|optional-dependencies" pyproject.toml` → no output
- [ ] `grep -rniE "fastapi|aiogram|FRAM_API|FRAM_BOT" README.md AGENTS.md .env.example docs` → no output
- [ ] `uv run fram --help` exits 0
- [ ] `uv run --all-extras --group dev ruff check .` exits 0
- [ ] `uv run --all-extras --group dev python -m pytest -q` → 0 failed, 0 errors
- [ ] `grep -nE "fastapi|aiogram" uv.lock` → no output
- [ ] No files outside the in-scope list are modified (`git status`)
- [ ] `plans/README.md` status row for 001 updated

## STOP conditions

Stop and report back (do not improvise) if:

- Step 1's first grep finds any `fram.api` / `fram.bot` import inside `fram/core`,
  `fram/cli`, or `fram/utils` (the no-coupling assumption is false).
- Something in `fram/api/schemas.py` or `fram/bot/services/operations.py` appears to be
  imported or needed outside the deleted packages.
- `uv lock` is unavailable or fails.
- Tests fail for a reason other than "bot tests were removed" (i.e. a core/CLI/util test
  breaks).
- The README/docs structure has drifted so far from the excerpts that you cannot locate the
  API/Bot sections cleanly.

## Maintenance notes

- After this lands, plans 002–005 assume a single CLI front end. The `fram.core` package is
  the only place processing logic should live; there is no longer a parallel parser in the
  bot to keep in sync.
- If the API or bot is ever wanted again, it should be added back as a thin adapter over
  `fram.core` (the architecture doc's "apps must not duplicate processing logic" rule still
  holds) — not by reviving the deleted code wholesale.
- Reviewer should scrutinize: that no `fram/core` or `fram/cli` file was edited (diff should
  be deletions + docs/config only), and that the test count drop is exactly the bot tests.
