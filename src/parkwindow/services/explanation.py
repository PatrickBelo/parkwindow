"""C6 Explanation service (interface I-7).

Build step 6. Planned responsibilities (Section 7.5, rule 6):
- Send only forecast and recommendation values to the LLM (NFR-08).
- Check that every time, number, and facility in the reply appears in that
  input; on any miss, timeout, or missing API key, use a template (FR-08).
- Log every fallback to the audit log.
"""

from __future__ import annotations

from parkwindow.models import ExplanationSource


def explain(payload: dict) -> tuple[str, ExplanationSource]:
    raise NotImplementedError("Build step 6: explanation service")
