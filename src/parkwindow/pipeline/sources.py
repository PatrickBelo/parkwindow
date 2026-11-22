"""Occupancy adapter (interface I-5).

Everything downstream reads occupancy through OccupancySource, so real
Parking Services data could replace synthetic data by adding one class here,
with no other changes (CH-3).
"""

from __future__ import annotations

import csv
import hashlib
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from parkwindow import config
from parkwindow.models import DataSource, Facility, OccupancyRecord

log = logging.getLogger(__name__)


class OccupancySource(ABC):
    """Provides occupancy records for a time range."""

    @abstractmethod
    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        """Return records with start <= timestamp < end, oldest first."""


# --- Hand-logged counts ------------------------------------------------------------

HAND_LOG_COLUMNS = ("date", "time", "facility", "available", "total", "notes")


@dataclass(frozen=True)
class Rejection:
    """A row that could not be used, and why (FR-02)."""

    line: int
    reason: str
    raw: dict[str, str]


class HandLoggedCsvSource(OccupancySource):
    """Counts recorded by hand from the FAU Parking app (data/hand_logged/).

    Malformed rows are skipped and kept in ``rejected`` with a reason, so one
    typo never stops the pipeline. A blank ``total`` falls back to the
    facility's configured capacity.
    """

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)
        self.rejected: list[Rejection] = []

    @property
    def dataset_version(self) -> str:
        """Changes whenever the file's contents change (NFR-04)."""
        digest = hashlib.sha256(self.csv_path.read_bytes()).hexdigest()
        return f"hand-log-{digest[:10]}"

    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        self.rejected = []
        version = self.dataset_version
        records: list[OccupancyRecord] = []

        with self.csv_path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            missing = set(HAND_LOG_COLUMNS[:4]) - set(reader.fieldnames or ())
            if missing:
                raise ValueError(f"{self.csv_path} is missing columns: {sorted(missing)}")

            # Line 1 is the header, so data starts on line 2.
            for line, row in enumerate(reader, start=2):
                try:
                    record = self._parse(row, version)
                except ValueError as err:
                    self.rejected.append(Rejection(line, str(err), dict(row)))
                    log.warning("Rejected %s line %d: %s", self.csv_path.name, line, err)
                    continue
                if start <= record.timestamp < end:
                    records.append(record)

        return sorted(records, key=lambda r: (r.timestamp, r.facility.value))

    @staticmethod
    def _parse(row: dict[str, str], version: str) -> OccupancyRecord:
        clean = {k: (v or "").strip() for k, v in row.items() if k}

        try:
            day = datetime.strptime(clean["date"], "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"bad date {clean['date']!r}, expected YYYY-MM-DD") from None
        try:
            clock = datetime.strptime(clean["time"], "%H:%M").time()
        except ValueError:
            raise ValueError(f"bad time {clean['time']!r}, expected HH:MM") from None
        try:
            facility = Facility(clean["facility"].lower())
        except ValueError:
            raise ValueError(f"unknown facility {clean['facility']!r}") from None
        try:
            available = int(clean["available"])
        except ValueError:
            raise ValueError(f"available {clean['available']!r} is not a whole number") from None

        if clean.get("total"):
            try:
                total = int(clean["total"])
            except ValueError:
                raise ValueError(f"total {clean['total']!r} is not a whole number") from None
        else:
            total = config.FACILITY_PROFILES[facility.value].capacity

        if not 0 <= available <= total:
            raise ValueError(f"available {available} is outside 0-{total}")

        return OccupancyRecord(
            facility=facility,
            timestamp=datetime.combine(day, clock),
            occupied=total - available,
            capacity=total,
            source=DataSource.HAND_LOGGED,
            dataset_version=version,
        )


# --- Synthetic counts ----------------------------------------------------------------


def _minutes(t: time) -> int:
    return t.hour * 60 + t.minute


def _smoothstep(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def baseline_fill(profile: config.FacilityProfile, at: time) -> float:
    """Expected fraction occupied before class-change dips and noise."""
    now = _minutes(at)
    start, peak = _minutes(config.DAY_START), _minutes(profile.peak_reached)
    decline, end = _minutes(config.AFTERNOON_DECLINE_START), _minutes(config.DAY_END)

    if now <= peak:
        progress = _smoothstep((now - start) / (peak - start))
        return profile.early_fill + (profile.peak_fill - profile.early_fill) * progress
    if now <= decline:
        return profile.peak_fill
    progress = min((now - decline) / (end - decline), 1.0)
    return profile.peak_fill + (profile.afternoon_fill - profile.peak_fill) * progress


def dismissal_dip(profile: config.FacilityProfile, day: date, at: time) -> float:
    """Fraction of capacity freed by recent class changes (assumption A-1)."""
    pattern = "MWF" if day.weekday() in (0, 2, 4) else "TR"
    now = _minutes(at)
    dip = 0.0
    for dismissal in config.DISMISSAL_TIMES[pattern]:
        since = now - _minutes(dismissal)
        if 0 <= since < config.DISMISSAL_REFILL_MINUTES:
            dip += profile.dismissal_release * (1 - since / config.DISMISSAL_REFILL_MINUTES)
    return dip


class SyntheticSource(OccupancySource):
    """Seeded, repeatable weekday counts shaped by FACILITY_PROFILES.

    The same seed always produces the same data, so tests and accuracy
    reports can be reproduced exactly.
    """

    def __init__(self, seed: int, facilities: tuple[Facility, ...] = tuple(Facility)) -> None:
        self.seed = seed
        self.facilities = facilities

    @property
    def dataset_version(self) -> str:
        return f"synthetic-{config.SYNTHETIC_GENERATOR_VERSION}-seed{self.seed}"

    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        records: list[OccupancyRecord] = []
        day = start.date()
        while day <= end.date():
            if day.weekday() < 5:  # weekdays only
                for facility in self.facilities:
                    records.extend(
                        r for r in self._day(facility, day) if start <= r.timestamp < end
                    )
            day += timedelta(days=1)
        return sorted(records, key=lambda r: (r.timestamp, r.facility.value))

    def _day(self, facility: Facility, day: date) -> list[OccupancyRecord]:
        profile = config.FACILITY_PROFILES[facility.value]
        # A string seed is hashed the same way on every run and platform.
        rng = random.Random(f"{self.seed}:{facility.value}:{day.isoformat()}")
        step = timedelta(minutes=config.SYNTHETIC_INTERVAL_MINUTES)
        moment = datetime.combine(day, config.DAY_START)
        last = datetime.combine(day, config.DAY_END)

        readings: list[OccupancyRecord] = []
        while moment <= last:
            at = moment.time()
            fill = baseline_fill(profile, at) - dismissal_dip(profile, day, at)
            fill += rng.gauss(0, profile.noise)
            occupied = round(min(max(fill, 0.0), 1.0) * profile.capacity)
            readings.append(
                OccupancyRecord(
                    facility=facility,
                    timestamp=moment,
                    occupied=occupied,
                    capacity=profile.capacity,
                    source=DataSource.SYNTHETIC,
                    dataset_version=self.dataset_version,
                )
            )
            moment += step
        return readings
