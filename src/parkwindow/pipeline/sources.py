"""Occupancy adapter (interface I-5).

Everything downstream reads occupancy through OccupancySource, so real
Parking Services data could replace synthetic data by adding one class here,
with no other changes (CH-3).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from parkwindow.models import OccupancyRecord


class OccupancySource(ABC):
    """Provides occupancy records for a time range."""

    @abstractmethod
    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        """Return records with start <= timestamp < end."""


class SyntheticSource(OccupancySource):
    """Seeded, repeatable synthetic counts calibrated to hand-logged data.

    Build step 1.
    """

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        raise NotImplementedError("Build step 1: synthetic data generator")


class HandLoggedCsvSource(OccupancySource):
    """Counts recorded by hand from the FAU Parking app (data/hand_logged/).

    Build step 1.
    """

    def __init__(self, csv_path: str) -> None:
        self.csv_path = csv_path

    def fetch(self, start: datetime, end: datetime) -> list[OccupancyRecord]:
        raise NotImplementedError("Build step 1: hand-logged CSV reader")
