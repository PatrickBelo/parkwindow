# Architecture

ParkWindow is a layered client-server application with a nightly Data Intelligence pipeline. This page maps the design in the Solution Design Report (Sections 6–7) onto the code.

## Layers and components

| ID | Component | Module | Responsibility |
| --- | --- | --- | --- |
| C1 | Commuter web app | `web/` | Schedule entry, recommendation view, feedback |
| C2 | Reviewer workbench | `web/` | Accuracy report; approve or restrict model versions |
| C3 | API layer | `api/app.py` | Validates requests, checks device token or reviewer login, routes |
| C4 | Recommendation service | `services/recommendation.py` | Arrival slot, depart-by time, backup facility, warnings |
| C5 | Permit rule engine | `services/permits.py` | Filters facilities by permit color and time of day |
| C6 | Explanation service | `services/explanation.py` | LLM phrasing, claim check, template fallback |
| C7 | Feedback service | `services/feedback.py` | Stores one arrival outcome per recommendation |
| C8 | Ingestion job | `pipeline/ingestion.py`, `pipeline/sources.py`, `pipeline/quality.py` | Loads occupancy through the adapter and the class schedule; rejects bad rows; flags stuck counters |
| C9 | Forecast job | `pipeline/forecast.py` | Slot probabilities, confidence, turnover flags; saves a Draft model |
| C10 | Accuracy monitor | `pipeline/accuracy.py` | Weekly accuracy; restricts models below 80% |
| C11 | Database | `db.py` | SQLite storage and audit log |

All modules live under `src/parkwindow/`.

## Interfaces

| ID | Interface | Type | Where |
| --- | --- | --- | --- |
| I-1 | `POST /v1/schedule-entries` | Sync | `api/app.py` |
| I-2 | `GET /v1/recommendations/{entry}` | Sync | `api/app.py` |
| I-3 | `POST /v1/feedback` | Sync | `api/app.py` |
| I-4 | `DELETE /v1/me` | Sync | `api/app.py` |
| I-5 | `OccupancySource.fetch(start, end)` | Async, nightly | `pipeline/sources.py` |
| I-6 | `ScheduleImporter.load(term)` | Async, once per term | `pipeline/ingestion.py` |
| I-7 | `explain(payload)` | Sync, 5 s timeout | `services/explanation.py` |
| I-8 | `POST /v1/models/{id}/approve` | Sync | `api/app.py` |

## Rules of the road

- The API layer never touches the database directly; it calls services, and services call `db.py`.
- The recommendation service reads only **Validated** model versions.
- The permit filter runs before any recommendation is built.
- The LLM receives forecast values only, never schedule entries or tokens.
- Swapping data sources means writing a new `OccupancySource`; nothing downstream changes.

## Forecasting rules

The numeric rules from Section 7.5 live in `config.py` so they can be tuned in one place: slot length, forecast window, the 5-space margin, 4 weeks of history, the 80% target likelihood and approval threshold, and the stale-data limit.
