"""Data quality checks on occupancy readings (FR-13).

Origin: on 2026-11-18 the FAU Parking app showed Garage 1 at exactly 879
available for 41 minutes of the weekday peak while Garage 2 kept changing.
A forecast built on a frozen counter would look confident and be wrong, so
runs like that are flagged before forecasting.

Check the hand log from the command line:

    python -m parkwindow.pipeline.quality
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby

from parkwindow import config
from parkwindow.models import Facility, OccupancyRecord


@dataclass(frozen=True)
class StuckRun:
    facility: Facility
    start: datetime
    end: datetime
    available: int
    readings: int

    @property
    def minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


def _in_peak(record: OccupancyRecord) -> bool:
    at = record.timestamp.time()
    return record.timestamp.weekday() < 5 and config.PEAK_START <= at <= config.PEAK_END


def find_stuck_counters(records: list[OccupancyRecord]) -> list[StuckRun]:
    """Return weekday-peak runs where a facility's count never changed.

    A run counts as stuck when it has at least STUCK_MIN_READINGS readings
    spanning at least STUCK_MIN_SPAN_MINUTES.
    """
    by_day: dict[tuple[Facility, object], list[OccupancyRecord]] = defaultdict(list)
    for record in records:
        if _in_peak(record):
            by_day[(record.facility, record.timestamp.date())].append(record)

    stuck: list[StuckRun] = []
    for (facility, _), day_records in sorted(by_day.items(), key=lambda kv: (kv[0][0].value, kv[0][1])):
        day_records.sort(key=lambda r: r.timestamp)
        for _, group in groupby(day_records, key=lambda r: r.occupied):
            run = list(group)
            span = (run[-1].timestamp - run[0].timestamp).total_seconds() / 60
            if len(run) >= config.STUCK_MIN_READINGS and span >= config.STUCK_MIN_SPAN_MINUTES:
                stuck.append(
                    StuckRun(facility, run[0].timestamp, run[-1].timestamp, run[0].available, len(run))
                )
    return stuck


def main() -> None:
    from parkwindow.config import Settings
    from parkwindow.pipeline.sources import HandLoggedCsvSource

    settings = Settings.from_env()
    source = HandLoggedCsvSource(settings.hand_log_path)
    records = source.fetch(datetime.min, datetime.max)

    print(f"{settings.hand_log_path}  ({source.dataset_version})")
    for facility in Facility:
        count = sum(r.facility is facility for r in records)
        print(f"  {facility.value}: {count} readings")
    for rejection in source.rejected:
        print(f"  REJECTED line {rejection.line}: {rejection.reason}")
    for run in find_stuck_counters(records):
        print(
            f"  STUCK {run.facility.value} at {run.available} available, "
            f"{run.start:%Y-%m-%d %H:%M}-{run.end:%H:%M} ({run.readings} readings, {run.minutes} min)"
        )


if __name__ == "__main__":
    main()
