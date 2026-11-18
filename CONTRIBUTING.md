# Contributing to ParkWindow

ParkWindow is an individual course project, but it follows the same workflow a team project would. These rules keep the history readable and the prototype trustworthy.

## Workflow

1. Create a branch for each build step or fix: `step-2-ingestion`, `fix-permit-filter`.
2. Write or update tests with the code. A feature is not done until its validation test passes.
3. Run `pytest` locally before pushing. CI runs the same tests on every push and pull request.
4. Merge into `main` through a pull request, even when working alone, so each change has a reviewable record.

## Commit messages

Use the imperative mood and name the requirement or component when one applies:

```
Add occupancy adapter interface (I-5)
Reject malformed occupancy rows in ingestion (FR-02)
Fix permit filter allowing red lots before 6pm (FR-07)
```

Keep each commit to one logical change.

## Tests

- Name tests after the validation question they answer: `test_fr07_never_recommends_disallowed_facility`.
- Mark tests for unbuilt features with `pytest.mark.skip(reason="Build step N")` rather than deleting them.
- Never call a live LLM API in tests; use the template fallback or a stub.

## Data and secrets

- Commit only synthetic data, hand-logged counts you recorded yourself, or data you are authorized to share.
- Never commit `.env`, API keys, passwords, or personal data. See [SECURITY.md](SECURITY.md).

## AI assistance

Treat AI-generated code, tests, and text as candidates. Before committing them:

1. Read and understand every line.
2. Check it against the requirements and architecture.
3. Run the tests.
4. Record material assistance in [AI_LOG.md](AI_LOG.md): what was generated, what you kept, changed, or rejected, and how you validated it.

## Style

- Follow PEP 8. Use type hints on public functions.
- Keep component boundaries from `docs/architecture.md`: services call the database through `db.py`, never directly from the API layer.
