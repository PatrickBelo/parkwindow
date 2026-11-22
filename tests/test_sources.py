"""Occupancy sources: hand-logged CSV and synthetic generator (build step 1)."""

from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path

import pytest

from parkwindow import config
from parkwindow.models import DataSource, Facility
from parkwindow.pipeline.sources import (
    HandLoggedCsvSource,
    SyntheticSource,
    dismissal_dip,
)

REPO = Path(__file__).resolve().parents[1]
REAL_HAND_LOG = REPO / "data" / "hand_logged" / "hand_log.csv"
ALL_TIME = (datetime.min, datetime.max)

HEADER = "date,time,facility,available,total,notes\n"


def days_covering(records) -> tuple[datetime, datetime]:
    """From the start of the first day to the end of the last day in records."""
    days = sorted({r.timestamp.date() for r in records})
    return datetime.combine(days[0], time.min), datetime.combine(days[-1], time.max)


def write_log(tmp_path: Path, rows: str) -> HandLoggedCsvSource:
    path = tmp_path / "hand_log.csv"
    path.write_text(HEADER + rows, encoding="utf-8")
    return HandLoggedCsvSource(path)


# --- Hand-logged CSV -------------------------------------------------------------


def test_hand_log_reads_template_columns(tmp_path: Path) -> None:
    source = write_log(tmp_path, "2026-11-18,10:23,garage_2,398,1030,\n")
    [record] = source.fetch(*ALL_TIME)
    assert record.facility is Facility.GARAGE_2
    assert record.timestamp == datetime(2026, 11, 18, 10, 23)
    assert record.available == 398
    assert record.capacity == 1030
    assert record.source is DataSource.HAND_LOGGED
    assert record.dataset_version.startswith("hand-log-")


def test_hand_log_blank_total_uses_configured_capacity(tmp_path: Path) -> None:
    source = write_log(tmp_path, "2026-11-18,10:23,garage_1,879,,\n")
    [record] = source.fetch(*ALL_TIME)
    assert record.capacity == config.FACILITY_PROFILES["garage_1"].capacity


@pytest.mark.parametrize(
    "row, reason",
    [
        ("11/18/2026,10:23,garage_2,398,,", "bad date"),
        ("2026-11-18,10.23am,garage_2,398,,", "bad time"),
        ("2026-11-18,10:23,garage_3,398,,", "unknown facility"),
        ("2026-11-18,10:23,garage_2,lots,,", "not a whole number"),
        ("2026-11-18,10:23,garage_2,1200,1030,", "outside"),
        ("2026-11-18,10:23,garage_2,-1,1030,", "outside"),
    ],
)
def test_fr02_malformed_rows_are_rejected_with_a_reason(
    tmp_path: Path, row: str, reason: str
) -> None:
    good = "2026-11-18,10:36,garage_2,380,,\n"
    source = write_log(tmp_path, row + "\n" + good)
    records = source.fetch(*ALL_TIME)
    assert [r.available for r in records] == [380]  # the good row still loads
    [rejection] = source.rejected
    assert rejection.line == 2
    assert reason in rejection.reason


def test_hand_log_missing_column_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "hand_log.csv"
    path.write_text("date,time,available\n2026-11-18,10:23,398\n", encoding="utf-8")
    with pytest.raises(ValueError, match="facility"):
        HandLoggedCsvSource(path).fetch(*ALL_TIME)


def test_hand_log_fetch_respects_time_range(tmp_path: Path) -> None:
    source = write_log(
        tmp_path,
        "2026-11-18,10:23,garage_2,398,,\n2026-11-18,11:04,garage_2,370,,\n",
    )
    records = source.fetch(datetime(2026, 11, 18, 10, 30), datetime(2026, 11, 18, 12))
    assert [r.available for r in records] == [370]


def test_nfr04_hand_log_version_changes_when_file_changes(tmp_path: Path) -> None:
    source = write_log(tmp_path, "2026-11-18,10:23,garage_2,398,,\n")
    before = source.dataset_version
    with source.csv_path.open("a", encoding="utf-8") as handle:
        handle.write("2026-11-18,10:36,garage_2,380,,\n")
    assert source.dataset_version != before


def test_committed_hand_log_has_no_rejected_rows() -> None:
    source = HandLoggedCsvSource(REAL_HAND_LOG)
    assert source.fetch(*ALL_TIME)
    assert source.rejected == []


# --- Synthetic generator ---------------------------------------------------------

WEEK = (datetime(2026, 11, 16), datetime(2026, 11, 23))  # Mon 16 - Sun 22


def test_synthetic_source_is_repeatable_for_the_same_seed() -> None:
    assert SyntheticSource(42).fetch(*WEEK) == SyntheticSource(42).fetch(*WEEK)


def test_synthetic_source_differs_for_another_seed() -> None:
    assert SyntheticSource(42).fetch(*WEEK) != SyntheticSource(7).fetch(*WEEK)


def test_synthetic_source_covers_weekdays_every_10_minutes() -> None:
    records = SyntheticSource(42).fetch(*WEEK)
    readings_per_day = (15 - 7) * 60 // config.SYNTHETIC_INTERVAL_MINUTES + 1  # 7:00-15:00
    assert len(records) == 5 * len(Facility) * readings_per_day
    assert {r.timestamp.weekday() for r in records} == {0, 1, 2, 3, 4}
    assert all(config.DAY_START <= r.timestamp.time() <= config.DAY_END for r in records)


def test_nfr12_synthetic_records_are_labeled_synthetic() -> None:
    records = SyntheticSource(42).fetch(*WEEK)
    assert {r.source for r in records} == {DataSource.SYNTHETIC}
    assert {r.dataset_version for r in records} == {"synthetic-v1-seed42"}


def test_class_change_frees_spaces_only_shortly_after_dismissal() -> None:
    profile = config.FACILITY_PROFILES["garage_1"]
    wednesday = date(2026, 11, 18)
    assert dismissal_dip(profile, wednesday, time(10, 40)) == 0
    assert dismissal_dip(profile, wednesday, time(10, 50)) == pytest.approx(profile.dismissal_release)
    assert dismissal_dip(profile, wednesday, time(11, 20)) == 0


def test_synthetic_garage_2_is_calibrated_to_hand_logged_readings() -> None:
    """Each real Garage 2 reading is within 5% of capacity of the nearest synthetic one."""
    real = [
        r for r in HandLoggedCsvSource(REAL_HAND_LOG).fetch(*ALL_TIME)
        if r.facility is Facility.GARAGE_2
    ]
    assert real, "no Garage 2 readings in the hand log"
    synthetic = SyntheticSource(42, (Facility.GARAGE_2,)).fetch(*days_covering(real))
    tolerance = 0.05 * config.FACILITY_PROFILES["garage_2"].capacity

    for reading in real:
        nearest = min(synthetic, key=lambda s: abs(s.timestamp - reading.timestamp))
        assert abs(nearest.available - reading.available) <= tolerance, reading.timestamp
