"""C10 Accuracy monitor (weekly).

Build step 7. Planned responsibilities:
- Score the newest model version against held-out observations and feedback.
- Produce the weekly accuracy report by facility and slot (FR-12).
- Set a Validated model to Restricted if accuracy falls below
  APPROVAL_THRESHOLD (NFR-02, NFR-07).
"""

from __future__ import annotations


def run_accuracy_report() -> None:
    raise NotImplementedError("Build step 7: accuracy monitor")
