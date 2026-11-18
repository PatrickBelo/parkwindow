"""Configuration and forecasting rules.

Forecasting constants come from Section 7.5 of the Solution Design Report and
are kept here so they can be tuned in one place (assumption A-4).
Runtime settings are read from environment variables or a local .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import time

from dotenv import load_dotenv

# --- Forecasting rules (Section 7.5) ---------------------------------------

SLOT_MINUTES = 10                 # FR-04: 10-minute arrival slots
DAY_START = time(7, 0)            # FR-04: forecast window start
DAY_END = time(15, 0)             # FR-04: forecast window end
FREE_SPACE_MARGIN = 5             # A slot "has space" if at least this many are free
HISTORY_WEEKS = 4                 # Matching weekdays used per forecast
PARK_SEARCH_MINUTES = 10          # "Find a space within 10 minutes"
TARGET_LIKELIHOOD = 0.8           # FR-06 default target
HIGH_CONFIDENCE = 0.8             # Confidence cutoffs
MEDIUM_CONFIDENCE = 0.5
TURNOVER_LOOKBACK_MINUTES = 15    # FR-05: dismissal must fall in this window
APPROVAL_THRESHOLD = 0.8          # NFR-02, NFR-07: minimum accuracy to approve
STALE_AFTER_DAYS = 7              # FR-09: data older than this triggers a warning
ATYPICAL_SEMESTER_WEEKS = 2       # FR-09: first weeks of a semester are atypical
LLM_TIMEOUT_SECONDS = 5           # I-7
MAX_EXPLANATION_SENTENCES = 2     # FR-08

# Permit rules (FR-07)
RED_LOTS_OPEN_AFTER = time(18, 0)


# --- Runtime settings --------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    db_path: str
    occupancy_source: str
    hand_log_path: str
    synthetic_seed: int
    llm_api_key: str
    llm_model: str
    reviewer_password: str

    @property
    def llm_enabled(self) -> bool:
        """Without an API key, explanations fall back to templates."""
        return bool(self.llm_api_key)

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        source = os.getenv("OCCUPANCY_SOURCE", "synthetic")
        if source not in {"synthetic", "hand_logged"}:
            raise ValueError(f"Unknown OCCUPANCY_SOURCE: {source!r}")
        return cls(
            db_path=os.getenv("PARKWINDOW_DB_PATH", "data/parkwindow.db"),
            occupancy_source=source,
            hand_log_path=os.getenv("HAND_LOG_PATH", "data/hand_logged/hand_log.csv"),
            synthetic_seed=int(os.getenv("SYNTHETIC_SEED", "42")),
            llm_api_key=os.getenv("LLM_API_KEY", ""),
            llm_model=os.getenv("LLM_MODEL", ""),
            reviewer_password=os.getenv("REVIEWER_PASSWORD", ""),
        )
