"""C5 Permit rule engine.

Build step 4. Runs before every recommendation (FR-07):
blue facilities always; red facilities only for arrivals after 6pm; green never.
"""

from __future__ import annotations

from datetime import time

from parkwindow.models import Permit


def allowed_permit_colors(permit: Permit, arrival: time) -> set[str]:
    """Return the lot colors a permit may use at the arrival time."""
    raise NotImplementedError("Build step 4: permit rule engine")
