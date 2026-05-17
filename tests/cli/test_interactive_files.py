from fram.cli.interactive.files import list_browser_entries


def test_list_browser_entries_includes_dirs_and_media(tmp_path) -> None:
    (tmp_path / "images").mkdir()
    (tmp_path / "image.png").write_bytes(b"")
    (tmp_path / "notes.txt").write_text("skip")

    entries = list_browser_entries(tmp_path)
    labels = [entry.label for entry in entries]

    assert "images/" in labels
    assert "image.png" in labels
    assert "notes.txt" not in labels


def test_list_browser_entries_includes_parent(tmp_path) -> None:
    child = tmp_path / "child"
    child.mkdir()

    entries = list_browser_entries(child)

    assert entries[0].label == ".."
    assert entries[0].is_dir is True
