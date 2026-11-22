# ParkWindow

**Know when to leave, not just where it's full.** ParkWindow forecasts when blue-permit parking spaces are likely to open in FAU Boca Raton's Garages 1 and 2, then recommends a departure time *before* a commuter leaves home.

> **Status: under construction.** This repository currently holds the project skeleton: the package layout, data models, configuration, a health-check API, and the test harness. See [Build progress](#build-progress) for what works today.

Built for CEN 4010 (Principles of Software Engineering) at Florida Atlantic University, Fall 2026.

---

## The problem

Commuter students with blue permits routinely leave home 15–30 minutes early just to find a space, and many still arrive late to class or work. The garage entrance signs and the FAU Parking app show only *current* counts, which help only once a commuter is already on campus and circling. Interviews showed that commuters already predict turnover by hand: they watch for students leaving class and ask where they parked.

ParkWindow turns that signal into a forecast. It combines garage occupancy counts with class dismissal times to estimate, for each 10-minute arrival slot, the chance of finding a space within 10 minutes, then works backward to a recommended departure time.

ParkWindow is a **proof of concept**. FAU Parking and Transportation Services has not provided official occupancy data, so the prototype runs on synthetic data calibrated with hand-logged counts. Using it with real commuters would require an operator to supply counter data through the occupancy adapter.

## Architecture

ParkWindow is a layered client-server application with a nightly Data Intelligence pipeline. Component IDs match Section 7.2 of the Solution Design Report.

| ID | Component | Layer | Module |
| --- | --- | --- | --- |
| C1 | Commuter web app | Presentation | `src/parkwindow/web/` |
| C2 | Reviewer workbench | Presentation | `src/parkwindow/web/` |
| C3 | API layer | Application | `src/parkwindow/api/app.py` |
| C4 | Recommendation service | Application | `src/parkwindow/services/recommendation.py` |
| C5 | Permit rule engine | Application | `src/parkwindow/services/permits.py` |
| C6 | Explanation service | Application | `src/parkwindow/services/explanation.py` |
| C7 | Feedback service | Application | `src/parkwindow/services/feedback.py` |
| C8 | Ingestion job | Pipeline | `src/parkwindow/pipeline/ingestion.py` |
| C9 | Forecast job | Pipeline | `src/parkwindow/pipeline/forecast.py` |
| C10 | Accuracy monitor | Pipeline | `src/parkwindow/pipeline/accuracy.py` |
| C11 | Database (SQLite) | Data | `src/parkwindow/db.py` |

Supporting modules: `models.py` holds the records from Section 7.3, `config.py` holds the forecasting rules from Section 7.5, and `pipeline/sources.py` defines the occupancy adapter (interface I-5) that lets real data replace synthetic data without changing anything downstream.

Three control points keep bad output away from commuters:

1. **Model gate.** Forecasts start as Draft; only a reviewer-approved (Validated) model version is served.
2. **Permit filter.** Only facilities the permit allows at the arrival time are ever recommended.
3. **Claim check.** Every time, number, and facility in an AI-written explanation must appear in the forecast data, or a template sentence is used instead.

More detail: [docs/architecture.md](docs/architecture.md) · [docs/traceability.md](docs/traceability.md)

## Prerequisites

- Python 3.11 or newer
- Git
- An LLM API key is **not** needed until the explanation service (build step 6); without one, ParkWindow uses template explanations.

## Setup

Clone the repository and create a virtual environment.

**Windows (PowerShell)**

```powershell
git clone https://github.com/<your-username>/parkwindow.git
cd parkwindow
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
```

**macOS / Linux**

```bash
git clone https://github.com/<your-username>/parkwindow.git
cd parkwindow
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

If PowerShell blocks the activation script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.

## Configuration

Settings are read from environment variables or a local `.env` file. `.env` is ignored by Git; never commit it.

| Variable | Default | Purpose |
| --- | --- | --- |
| `PARKWINDOW_DB_PATH` | `data/parkwindow.db` | SQLite database file |
| `OCCUPANCY_SOURCE` | `synthetic` | `synthetic` or `hand_logged` |
| `HAND_LOG_PATH` | `data/hand_logged/hand_log.csv` | Hand-logged counts, when used |
| `SYNTHETIC_SEED` | `42` | Seed for repeatable synthetic data |
| `LLM_API_KEY` | *(empty)* | Explanation service; blank means template text only |
| `LLM_MODEL` | *(empty)* | Model name for the explanation service |
| `REVIEWER_PASSWORD` | *(empty)* | Reviewer workbench login |

## Run

Start the API server:

```bash
uvicorn parkwindow.api.app:app --reload
```

Then open <http://127.0.0.1:8000/health> (status check) or <http://127.0.0.1:8000/docs> (interactive API docs).

Check the hand-logged counts for rejected rows and stuck counters:

```bash
python -m parkwindow.pipeline.quality
```

More pipeline commands and the web app will be added here as build steps are completed.

## Test

```bash
pytest
```

Tests are named after the validation questions in the Solution Design Report. Tests for features not built yet are marked **skipped** with the build step that will enable them, so the test run doubles as a progress report.

## Data

ParkWindow uses only synthetic, public, or explicitly authorized data (NFR-12).

- **Synthetic occupancy data** is generated from a fixed seed and labeled `source=synthetic`. Its curve for each garage is set in `config.FACILITY_PROFILES`, calibrated against hand-logged readings; each assumption is cited there.
- **Hand-logged counts** are my own observations of Garage 1 and 2 availability, read manually from the public FAU Parking app and labeled `source=hand_logged`. See [data/README.md](data/README.md) for the logging template.
- **Stuck counters are flagged.** On 2026-11-18 the app showed Garage 1 frozen at 879 available for 41 minutes of the weekday peak. Runs like that are detected and flagged before forecasting (FR-13).
- **No personal data** is collected or stored: no names, student IDs, license plates, or locations. Commuters are identified only by an anonymous device token.

## Build progress

Build order follows Section 8.1 of the Solution Design Report.

- [x] Repository skeleton, data models, configuration, health-check API, CI
- [x] 1. Hand-logged counts, synthetic data generator, occupancy adapter, stuck-counter check (FR-13)
- [ ] 2. Database schema and ingestion job (FR-02, FR-03)
- [ ] 3. Forecast job (FR-04, FR-05, FR-13)
- [ ] 4. Permit rule engine and recommendation service (FR-06, FR-07, NFR-01)
- [ ] 5. Commuter web app (FR-01, FR-10, NFR-03)
- [ ] 6. Explanation service with claim check (FR-08, NFR-08)
- [ ] 7. Feedback, accuracy monitor, reviewer workbench (FR-11, FR-12, NFR-07)
- [ ] 8. Hardening: warnings, data deletion, audit log (FR-09, NFR-04, NFR-05)

## Known limitations

- Occupancy data is synthetic, calibrated only by a few days of hand-logged counts, so real-world forecast accuracy is unproven.
- The FAU Parking app's Garage 1 counter appeared stuck during testing, so Garage 1's synthetic curve rests on interview evidence rather than readings.
- Class change times are placeholders until the Registrar's schedule is loaded (build step 2).
- Only Garages 1 and 2 are covered; surface lots without counters are out of scope.
- Forecasts are advisory. ParkWindow never reserves spaces or overrides Parking Services signage or permit rules.

## AI assistance

AI tools were used to help plan, scaffold, and test this project. All AI-generated work is reviewed before it is committed, and material assistance is recorded in [AI_LOG.md](AI_LOG.md).

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) © 2026 Patrick Belo
