# AI Assistance Log

This log records material AI assistance during development, as required by the CEN 4010 Final Project. Each entry states what the AI produced and what I did with it. AI output is treated as a candidate until I have reviewed and validated it.

| Date | Task | AI contribution | My review and decision | Validation |
| --- | --- | --- | --- | --- |
| 2026-11-17 | Repository skeleton | Claude (Anthropic) generated the folder structure, README, LICENSE, CONTRIBUTING, SECURITY, data models, configuration, health-check API, CI workflow, and placeholder tests from the Solution Design Report | reviewed | `pytest` passes locally and in CI |
| 2026-11-22 | Build step 1: occupancy sources and data quality | Claude (Anthropic) implemented the hand-log CSV reader with row rejection, the seeded synthetic generator and its garage profiles, stuck-counter detection, the Garage 3 to Garage 2 switch, and their tests | reviewed | 48 tests pass; synthetic Garage 2 is within 8-22 spaces of the 2026-11-18 readings; `python -m parkwindow.pipeline.quality` flags the stuck Garage 1 counter |

## How to add an entry

- **Task:** the build step or problem.
- **AI contribution:** what the tool generated or suggested, in a sentence.
- **My review and decision:** what you kept, what you changed and why, and anything you rejected.
- **Validation:** the test, check, or observation that confirmed it works.
