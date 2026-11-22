"""Record validation and traceability fields (NFR-04, NFR-12)."""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime, time

import pytest

from parkwindow.models import (
    Confidence,
    DataSource,
    Facility,
    Forecast,
    OccupancyRecord,
    Recommendation,
)
from parkwindow.pipeline.sources import OccupancySource


def make_record(occupied: int = 900, capacity: int = 1022) -> OccupancyRecord:
    return OccupancyRecord(
        facility=Facility.GARAGE_1,
        timestamp=datetime(2026, 11, 18, 8, 40),
        occupied=occupied,
        capacity=capacity,
        source=DataSource.SYNTHETIC,
        dataset_version="test-v1",
    )


def test_occupancy_record_computes_available_spaces() -> None:
    assert make_record(occupied=900, capacity=1022).available == 122


@pytest.mark.parametrize("occupied, capacity", [(-1, 1022), (1023, 1022), (0, 0)])
def test_occupancy_record_rejects_impossible_counts(occupied: int, capacity: int) -> None:
    with pytest.raises(ValueError):
        make_record(occupied=occupied, capacity=capacity)


@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_forecast_rejects_probability_outside_0_to_1(probability: float) -> None:
    with pytest.raises(ValueError):
        Forecast(
            facility=Facility.GARAGE_2,
            weekday=1,
            slot_start=time(9, 30),
            probability=probability,
            confidence=Confidence.LOW,
            turnover_flag=False,
            model_version="m-test",
        )


def test_nfr12_occupancy_records_carry_their_origin() -> None:
    names = {f.name for f in fields(OccupancyRecord)}
    assert {"source", "dataset_version"} <= names


def test_nfr04_recommendations_carry_model_version_and_explanation_source() -> None:
    names = {f.name for f in fields(Recommendation)}
    assert {"model_version", "explanation_source"} <= names


def test_occupancy_source_is_an_interface() -> None:
    with pytest.raises(TypeError):
        OccupancySource()  # type: ignore[abstract]
