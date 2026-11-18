"""C7 Feedback service (interface I-3).

Build step 7. Stores one arrival outcome per recommendation, linked to its
forecast and timestamp (FR-11). A second submission is rejected (409).
"""

from __future__ import annotations

from parkwindow.models import Feedback


def record_feedback(feedback: Feedback) -> None:
    raise NotImplementedError("Build step 7: feedback service")
