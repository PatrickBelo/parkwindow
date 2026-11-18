"""C9 Forecast job (nightly).

Build step 3. Planned responsibilities (Section 7.5, rules 1-3):
- For each facility, weekday, and 10-minute slot from 7am to 3pm, compute the
  share of the last HISTORY_WEEKS matching weekdays with at least
  FREE_SPACE_MARGIN spaces free within 10 minutes (FR-04).
- Assign High, Medium, or Low confidence.
- Flag turnover windows and name the dismissal behind each flag (FR-05).
- Save results as a Draft ModelVersion (NFR-07).
"""

from __future__ import annotations


def run_forecast() -> None:
    raise NotImplementedError("Build step 3: forecast job")
