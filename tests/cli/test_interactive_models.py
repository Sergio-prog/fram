from fram.cli.interactive.models import CutRange


def test_cut_range_switches_active_edge() -> None:
    cut_range = CutRange()

    cut_range.switch_edge()

    assert cut_range.active_edge == "end"


def test_cut_range_moves_start_without_crossing_end() -> None:
    cut_range = CutRange(start_percent=10, end_percent=12)

    cut_range.move_active(10)

    assert cut_range.start_percent == 11


def test_cut_range_moves_end_without_crossing_start() -> None:
    cut_range = CutRange(start_percent=10, end_percent=12, active_edge="end")

    cut_range.move_active(-10)

    assert cut_range.end_percent == 11


def test_cut_range_builds_input_from_duration() -> None:
    cut_range = CutRange(start_percent=10, end_percent=50)

    assert cut_range.to_input_value(100) == "00:10 00:50"


def test_cut_range_without_duration_has_no_input_value() -> None:
    assert CutRange().to_input_value(None) == ""

