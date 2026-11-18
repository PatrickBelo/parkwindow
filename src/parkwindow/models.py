"""Information structures from Section 7.3 of the Solution Design Report.

Every record that comes from data or a model carries its source or version,
so any forecast or recommendation can be traced back (NFR-04, NFR-12).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class Facility(str, Enum):
    GARAGE_1 = "garage_1"
    GARAGE_3 = "garage_3"


class Permit(str, Enum):
    BLUE = "blue"
    RED = "red"
    GREEN = "green"


class DataSource(str, Enum):
    SYNTHETIC = "synthetic"
    HAND_LOGGED = "hand_logged"
    PARKING_SERVICES = "parking_services"


class Confidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ModelStatus(str, Enum):
    DRAFT = "draft"
    VALIDATED = "validated"
    RESTRICTED = "restricted"


class ExplanationSource(str, Enum):
    LLM = "llm"
    TEMPLATE = "template"


class Outcome(str, Enum):
    WITHIN_10_MIN = "within_10_min"
    LATER = "later"
    ELSEWHERE = "elsewhere"
    DID_NOT_PARK = "did_not_park"


@dataclass(frozen=True)
class OccupancyRecord:
    facility: Facility
    timestamp: datetime
    occupied: int
    capacity: int
    source: DataSource
    dataset_version: str

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        if not 0 <= self.occupied <= self.capacity:
            raise ValueError("occupied must be between 0 and capacity")

    @property
    def available(self) -> int:
        return self.capacity - self.occupied


@dataclass(frozen=True)
class ClassSection:
    term: str
    section: str
    days: str                 # e.g. "MWF", "TR"
    start: time
    end: time
    building: str
    enrollment: int
    instructional_method: str  # online sections are excluded from dismissals


@dataclass(frozen=True)
class DismissalSlot:
    facility: Facility
    weekday: int              # 0 = Monday
    slot_start: time
    seats_released: int


@dataclass(frozen=True)
class Forecast:
    facility: Facility
    weekday: int
    slot_start: time
    probability: float        # chance of a space within 10 minutes
    confidence: Confidence
    turnover_flag: bool
    model_version: str
    dismissal_note: str | None = None  # FR-05: names the dismissal behind a flag

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("probability must be between 0 and 1")


@dataclass
class ModelVersion:
    id: str
    created: datetime
    data_start: date
    data_end: date
    accuracy: float | None = None
    status: ModelStatus = ModelStatus.DRAFT
    reviewer: str | None = None
    approved_at: datetime | None = None


@dataclass(frozen=True)
class ScheduleEntry:
    device_token: str         # anonymous; no personal identifiers (NFR-05)
    weekday: int
    start_time: time
    building: str
    preferred_facility: Facility
    drive_minutes: int
    walk_minutes: int


@dataclass(frozen=True)
class Recommendation:
    id: str
    entry_id: str
    depart_by: time
    facility: Facility
    backup_facility: Facility | None
    probability: float
    confidence: Confidence
    explanation: str
    explanation_source: ExplanationSource
    model_version: str
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Feedback:
    recommendation_id: str
    outcome: Outcome
    submitted_at: datetime


@dataclass(frozen=True)
class AuditEvent:
    event: str                # approval, rejection, fallback, deletion, ...
    actor: str
    time: datetime
    details: str = ""
