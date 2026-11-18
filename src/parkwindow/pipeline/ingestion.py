"""C8 Ingestion job (nightly).

Build step 2. Planned responsibilities:
- Fetch occupancy through an OccupancySource (I-5) and store valid records.
- Reject malformed rows and log each rejection (FR-02).
- Load the class schedule once per term (I-6) and derive DismissalSlots,
  excluding online sections (FR-03).
"""

from __future__ import annotations


def run_ingestion() -> None:
    raise NotImplementedError("Build step 2: ingestion job")
