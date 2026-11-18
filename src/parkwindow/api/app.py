"""C3 API layer.

Run with:  uvicorn parkwindow.api.app:app --reload

Planned endpoints (Section 7.4), added as build steps are completed:
- I-1  POST   /v1/schedule-entries        (step 5)
- I-2  GET    /v1/recommendations/{entry} (step 4)
- I-3  POST   /v1/feedback                (step 7)
- I-4  DELETE /v1/me                      (step 8)
- I-8  POST   /v1/models/{id}/approve     (step 7)
"""

from __future__ import annotations

from fastapi import FastAPI

from parkwindow import __version__

app = FastAPI(
    title="ParkWindow",
    version=__version__,
    description="Forecasts commuter parking turnover and recommends a departure time.",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok", "version": __version__}
