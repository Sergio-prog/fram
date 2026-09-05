import json
import time

import fram.updates as updates


def test_version_comparison_handles_v_prefix() -> None:
    assert updates.is_newer_version("v0.2.0", "0.1.9") is True
    assert updates.is_newer_version("0.1.0", "0.1.0") is False


def test_check_for_update_uses_fresh_cache(tmp_path, monkeypatch) -> None:
    cache_dir = tmp_path / "cache"
    cache_file = cache_dir / "fram" / "latest-release.json"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text(
        json.dumps(
            {
                "checked_at": time.time(),
                "version": "9.9.9",
                "tag": "v9.9.9",
                "url": "https://example.test/release",
            }
        )
    )
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache_dir))
    monkeypatch.setattr(updates, "fetch_latest_release", lambda timeout_seconds: None)

    status = updates.check_for_update()

    assert status.is_available is True
    assert status.latest is not None
    assert status.latest.tag == "v9.9.9"


def test_update_notice_can_be_disabled(monkeypatch) -> None:
    monkeypatch.setenv("FRAM_UPDATE_CHECK", "0")

    assert updates.update_notice() == ""


def test_install_latest_release_uses_release_tag(monkeypatch) -> None:
    release = updates.ReleaseInfo("9.9.9", "v9.9.9", "https://example.test/release")
    status = updates.UpdateStatus(current_version="0.1.0", latest=release)
    calls: list[list[str]] = []

    monkeypatch.setattr(updates, "check_for_update", lambda **kwargs: status)
    monkeypatch.setattr(updates.sys, "prefix", "/home/user/.local/share/uv/tools/fram")
    monkeypatch.setattr(
        updates.shutil,
        "which",
        lambda name: "/usr/bin/uv" if name == "uv" else None,
    )

    def fake_run(command: list[str], text: bool, check: bool):
        calls.append(command)
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    monkeypatch.setattr(updates, "_write_cached_release", lambda latest: None)

    result = updates.install_latest_release()

    assert result == "Updated Fram to 9.9.9."
    assert calls == [
        ["uv", "tool", "install", "--force", "git+https://github.com/Sergio-prog/fram.git@v9.9.9"]
    ]


def test_install_latest_release_uses_brew_for_homebrew_installs(monkeypatch) -> None:
    release = updates.ReleaseInfo("9.9.9", "v9.9.9", "https://example.test/release")
    status = updates.UpdateStatus(current_version="0.1.0", latest=release)
    calls: list[list[str]] = []

    monkeypatch.setattr(updates, "check_for_update", lambda **kwargs: status)
    monkeypatch.setattr(updates.sys, "prefix", "/opt/homebrew/Cellar/fram/0.1.0/libexec")
    monkeypatch.setattr(updates.shutil, "which", lambda name: f"/opt/homebrew/bin/{name}")

    def fake_run(command: list[str], text: bool, check: bool):
        calls.append(command)
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    monkeypatch.setattr(updates, "_write_cached_release", lambda latest: None)

    result = updates.install_latest_release()

    assert result == "Updated Fram to 9.9.9."
    assert calls == [["brew", "upgrade", "sergio-prog/tap/fram"]]


def test_install_latest_release_honors_source_on_homebrew_installs(monkeypatch) -> None:
    status = updates.UpdateStatus(current_version="0.1.0", latest=None)
    calls: list[list[str]] = []

    monkeypatch.setattr(updates, "check_for_update", lambda **kwargs: status)
    monkeypatch.setattr(updates.sys, "prefix", "/opt/homebrew/Cellar/fram/0.1.0/libexec")
    monkeypatch.setattr(updates.shutil, "which", lambda name: f"/opt/homebrew/bin/{name}")

    def fake_run(command: list[str], text: bool, check: bool):
        calls.append(command)
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr(updates.subprocess, "run", fake_run)
    monkeypatch.setattr(updates, "_clear_cached_release", lambda: None)

    updates.install_latest_release("git+https://example.test/fram.git")

    assert calls == [["uv", "tool", "install", "--force", "git+https://example.test/fram.git"]]
