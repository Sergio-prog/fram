from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fram import __version__
from fram.core.errors import FramError

REPOSITORY = "Sergio-prog/fram"
LATEST_RELEASE_URL = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
RELEASE_PAGE_URL = f"https://github.com/{REPOSITORY}/releases/latest"
HOMEBREW_FORMULA = "sergio-prog/tap/fram"
DEFAULT_CACHE_TTL_SECONDS = 12 * 60 * 60


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag: str
    url: str


@dataclass(frozen=True)
class UpdateStatus:
    current_version: str
    latest: ReleaseInfo | None

    @property
    def is_available(self) -> bool:
        return self.latest is not None and is_newer_version(
            self.latest.version,
            self.current_version,
        )


def check_for_update(
    *,
    use_cache: bool = True,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    timeout_seconds: float = 1.5,
) -> UpdateStatus:
    if _update_checks_disabled():
        return UpdateStatus(current_version=__version__, latest=None)

    cached = _read_cached_release(cache_ttl_seconds) if use_cache else None
    if cached is not None:
        return UpdateStatus(current_version=__version__, latest=cached)

    release = fetch_latest_release(timeout_seconds=timeout_seconds)
    if release is not None:
        _write_cached_release(release)
    return UpdateStatus(current_version=__version__, latest=release)


def update_notice() -> str:
    status = check_for_update()
    if not status.is_available or status.latest is None:
        return ""
    return (
        f"Fram {status.latest.version} is available "
        f"(current {status.current_version}). Run `fram update`."
    )


def fetch_latest_release(*, timeout_seconds: float = 3.0) -> ReleaseInfo | None:
    request = Request(
        LATEST_RELEASE_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"fram/{__version__}",
        },
    )
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None

    tag = str(payload.get("tag_name") or "")
    version = normalize_version(tag)
    if not version:
        return None
    return ReleaseInfo(
        version=version,
        tag=tag,
        url=str(payload.get("html_url") or RELEASE_PAGE_URL),
    )


def install_latest_release(source: str | None = None) -> str:
    status = check_for_update(use_cache=False, timeout_seconds=5.0)
    if status.latest is None and source is None:
        raise FramError("Could not find the latest GitHub release.")

    package_source = source or f"git+https://github.com/{REPOSITORY}.git@{status.latest.tag}"
    if source is None and _installed_with_homebrew():
        command = _homebrew_upgrade_command()
    else:
        command = _installer_command(package_source)
    result = subprocess.run(command, text=True, check=False)
    if result.returncode != 0:
        raise FramError(f"Update command failed with exit code {result.returncode}.")

    if status.latest is None:
        _clear_cached_release()
        return f"Updated Fram from {package_source}."

    _write_cached_release(status.latest)
    return f"Updated Fram to {status.latest.version}."


def is_newer_version(candidate: str, current: str) -> bool:
    return _version_key(candidate) > _version_key(current)


def normalize_version(value: str) -> str:
    version = value.strip()
    if version.startswith(("v", "V")):
        version = version[1:]
    return version


def _installed_with_homebrew() -> bool:
    parts = Path(sys.prefix).resolve().parts
    return any(
        parent == "Cellar" and child == "fram"
        for parent, child in zip(parts, parts[1:], strict=False)
    )


def _homebrew_upgrade_command() -> list[str]:
    if shutil.which("brew"):
        return ["brew", "upgrade", HOMEBREW_FORMULA]
    raise FramError("Fram was installed with Homebrew, but `brew` is not on PATH.")


def _installer_command(package_source: str) -> list[str]:
    if shutil.which("uv"):
        return ["uv", "tool", "install", "--force", package_source]
    if shutil.which("pipx"):
        return ["pipx", "install", "--force", package_source]
    raise FramError("Install uv or pipx first, then rerun `fram update`.")


def _version_key(version: str) -> tuple[int, ...]:
    parts: list[int] = []
    for part in normalize_version(version).split("."):
        digits = ""
        for char in part:
            if not char.isdigit():
                break
            digits += char
        parts.append(int(digits or "0"))
    return tuple(parts)


def _update_checks_disabled() -> bool:
    value = os.environ.get("FRAM_UPDATE_CHECK", "").lower()
    return value in {"0", "false", "no", "off"}


def _cache_path() -> Path:
    cache_root = os.environ.get("XDG_CACHE_HOME")
    root = Path(cache_root) if cache_root else Path.home() / ".cache"
    return root / "fram" / "latest-release.json"


def _read_cached_release(cache_ttl_seconds: int) -> ReleaseInfo | None:
    path = _cache_path()
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

    checked_at = float(payload.get("checked_at") or 0)
    if time.time() - checked_at > cache_ttl_seconds:
        return None

    tag = str(payload.get("tag") or "")
    version = str(payload.get("version") or normalize_version(tag))
    if not tag or not version:
        return None
    return ReleaseInfo(version=version, tag=tag, url=str(payload.get("url") or RELEASE_PAGE_URL))


def _write_cached_release(release: ReleaseInfo) -> None:
    path = _cache_path()
    payload = {
        "checked_at": time.time(),
        "version": release.version,
        "tag": release.tag,
        "url": release.url,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        return


def _clear_cached_release() -> None:
    try:
        _cache_path().unlink(missing_ok=True)
    except OSError:
        return
