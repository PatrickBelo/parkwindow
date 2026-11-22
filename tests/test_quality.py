"""Stuck-counter detection (FR-13)."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from parkwindow.models import DataSource, Facility, OccupancyRecord
from parkwindow.pipeline.quality import find_stuck_counters
from parkwindow.pipeline.sources import HandLoggedCsvSource, SyntheticSource

REAL_HAND_LOG = Path(__file__).resolve().parents[1] / "data" / "hand_logged" / "hand_log.csv"


def readings(start: datetime, values: list[int], every_minutes: int = 15) -> list[OccupancyRecord]:
    return [
        OccupancyRecord(
            facility=Facility.GARAGE_1,
            timestamp=start + timedelta(minutes=i * every_minutes),
            occupied=1022 - available,
            capacity=1022,
            source=DataSource.HAND_LOGGED,
            dataset_version="test",
        )
        for i, available in enumerate(values)
    ]


WEDNESDAY_10AM = datetime(2026, 11, 18, 10, 0)


def test_fr13_flags_the_stuck_garage_1_counter_from_2026_11_18() -> None:
    records = HandLoggedCsvSource(REAL_HAND_LOG).fetch(datetime.min, datetime.max)
    stuck = [
        run for run in find_stuck_counters(records)
        if run.start.date() == datetime(2026, 11, 18).date()
    ]
    assert [(r.facility, r.available, r.readings, r.minutes) for r in stuck] == [
        (Facility.GARAGE_1, 879, 4, 41)
    ]


def test_fr13_changing_counts_are_not_flagged() -> None:
    assert find_stuck_counters(readings(WEDNESDAY_10AM, [398, 380, 373, 370])) == []


def test_fr13_short_or_brief_runs_are_not_flagged() -> None:
    two_readings = readings(WEDNESDAY_10AM, [500, 500])
    brief = readings(WEDNESDAY_10AM, [500, 500, 500], every_minutes=5)  # 10 minutes
    assert find_stuck_counters(two_readings + brief) == []


def test_fr13_off_peak_and_weekend_runs_are_not_flagged() -> None:
    evening = readings(datetime(2026, 11, 18, 18, 0), [900, 900, 900, 900])
    saturday = readings(datetime(2026, 11, 21, 10, 0), [900, 900, 900, 900])
    assert find_stuck_counters(evening + saturday) == []


def test_fr13_synthetic_data_has_no_stuck_runs() -> None:
    week = SyntheticSource(42).fetch(datetime(2026, 11, 16), datetime(2026, 11, 21))
    assert find_stuck_counters(week) == []
