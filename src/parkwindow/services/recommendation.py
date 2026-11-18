"""C4 Recommendation service.

Build step 4. Planned responsibilities (Section 7.5, rule 5):
- Read Validated forecasts only.
- Pick the latest arrival slot meeting TARGET_LIKELIHOOD that still leaves
  PARK_SEARCH_MINUTES plus the walk before class; depart-by = slot - drive time.
- Fall back to the next allowed facility, then to a Low-confidence result
  with the commuter's usual buffer (FR-06).
- Attach stale-data and atypical-period warnings (FR-09).
"""

from __future__ import annotations

from parkwindow.models import Recommendation, ScheduleEntry


def recommend(entry: ScheduleEntry) -> Recommendation:
    raise NotImplementedError("Build step 4: recommendation service")
