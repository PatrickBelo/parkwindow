# Requirements Traceability

Each requirement from the Solution Design Report, where it is implemented, and the test that validates it. Update the **Status** column as build steps are completed; this table feeds the implementation summary in the final report.

Status values: Planned · In progress · Implemented · Validated

| Requirement | Priority | Component | Module | Test | Status |
| --- | --- | --- | --- | --- | --- |
| FR-01 Schedule entry | Should | C1, C3 | `api/app.py`, `web/` | `test_fr01_*` | Planned |
| FR-02 Ingest occupancy | Must | C8, C11 | `pipeline/ingestion.py` | `test_fr02_*` | Planned |
| FR-03 Dismissal slots | Should | C8 | `pipeline/ingestion.py` | `test_fr03_*` | Planned |
| FR-04 Slot forecasts | Must | C9 | `pipeline/forecast.py` | `test_fr04_*` | Planned |
| FR-05 Turnover flags | Must | C9 | `pipeline/forecast.py` | `test_fr05_*` | Planned |
| FR-06 Departure recommendation | Must | C4 | `services/recommendation.py` | `test_fr06_*` | Planned |
| FR-07 Permit filter | Must | C5 | `services/permits.py` | `test_fr07_*` | Planned |
| FR-08 Explanation claim check | Must | C6 | `services/explanation.py` | `test_fr08_*` | Planned |
| FR-09 Stale and atypical warnings | Must | C4, C9 | `services/recommendation.py` | `test_fr09_*` | Planned |
| FR-10 Recommendation view | Must | C1 | `web/` | `test_fr10_*` | Planned |
| FR-11 Feedback | Must | C1, C7 | `services/feedback.py` | `test_fr11_*` | Planned |
| FR-12 Accuracy report and approval | Should | C2, C10 | `pipeline/accuracy.py` | `test_fr12_*` | Planned |
| NFR-01 Response time | Must | C3, C4 | `api/app.py` | `test_nfr01_*` | Planned |
| NFR-02 Forecast accuracy | Must | C9, C10 | `pipeline/accuracy.py` | `test_nfr02_*` | Planned |
| NFR-04 Source traceability | Must | C4, C9, C11 | `models.py` | `test_nfr04_*` | In progress |
| NFR-05 Privacy | Must | C3, C11 | `api/app.py`, `db.py` | `test_nfr05_*` | Planned |
| NFR-06 Security | Must | Deployment | `.gitignore`, `.env.example` | Repository check | In progress |
| NFR-07 Review status | Should | C2, C10 | `pipeline/accuracy.py` | `test_nfr07_*` | Planned |
| NFR-08 AI operating conditions | Should | C6 | `services/explanation.py` | `test_nfr08_*` | Planned |
| NFR-09 Human authority | Must | C4, C5 | `services/recommendation.py` | Code and UI review | Planned |
| NFR-12 Data origin labels | Must | C8 | `models.py`, `pipeline/sources.py` | `test_nfr12_*` | In progress |

NFR-03 (readability) and NFR-10 (driver safety) are checked by UI review rather than automated tests.
