# Data

ParkWindow uses only synthetic, public, or explicitly authorized data (NFR-12). Nothing in this folder may contain personal information.

| Folder | Contents | Committed? |
| --- | --- | --- |
| `hand_logged/` | Garage counts I recorded by hand from the public FAU Parking app | Yes |
| `generated/` | Synthetic data produced by the generator | No (recreated from the seed) |
| `parkwindow.db` | Local SQLite database | No |

## Hand-logging garage counts

Add one row per reading to `hand_logged/hand_log.csv` (the template shows the columns). Check the file afterward with `python -m parkwindow.pipeline.quality`.

| Column | Format | Example |
| --- | --- | --- |
| `date` | YYYY-MM-DD | 2026-11-18 |
| `time` | HH:MM, 24-hour | 08:40 |
| `facility` | `garage_1` or `garage_2` | garage_1 |
| `available` | Spaces shown in the app | 112 |
| `total` | Total spaces shown in the app | 1022 |
| `notes` | Optional | rain; exam week |

Guidelines:

- Read the app every 15–20 minutes, ideally covering 8–11am on weekdays.
- **Never log while driving.** Record only when parked, walking, or at home (NFR-10).
- Read the app manually. Do not automate requests to the FAU Parking app or its servers.
- Note anything unusual (exams, events, holidays, weather) in `notes`; the forecast treats atypical periods with lower confidence.
