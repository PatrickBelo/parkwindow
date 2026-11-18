# Security and Privacy

## Reporting a problem

If you find a security or privacy issue, please do not open a public issue. Contact the maintainer through GitHub instead.

## Commitments

These follow the non-functional requirements in the Solution Design Report.

| Requirement | Commitment |
| --- | --- |
| NFR-05 Privacy | Only schedule times, buildings, and facility preferences are stored, linked to an anonymous device token. No names, student IDs, license plates, or location tracking. A user can delete all their data in one action. |
| NFR-06 Security | Secrets live in environment variables or an untracked `.env` file, never in the repository. Any university data is read-only and never committed. ParkWindow has no write access to FAU systems. |
| NFR-08 AI use | The LLM receives only forecast values and facility names, never personal data. |
| NFR-12 Data | Only synthetic, public, or explicitly authorized data is used, and each dataset is labeled with its origin. |

## Before every push

- `git status` shows no `.env`, database files, or credentials.
- No real personal data appears in `data/`, tests, or fixtures.
- New dependencies come from well-known, maintained packages.
