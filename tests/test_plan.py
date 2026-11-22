"""Validation plan from the Solution Design Report (Sections 4 and 8.2).

Each test is named after a requirement's validation question and skipped until
its build step lands. Replace the skip with a real test as you build; moving a
test out of this file is fine once it passes.
"""

from __future__ import annotations

import pytest


def step(n: int) -> pytest.MarkDecorator:
    return pytest.mark.skip(reason=f"Build step {n}")


@step(1)
def test_synthetic_source_is_repeatable_for_the_same_seed() -> None: ...


@step(1)
def test_hand_logged_source_reads_template_columns() -> None: ...


@step(2)
def test_fr02_every_stored_record_has_all_fields_and_bad_rows_are_logged() -> None: ...


@step(2)
def test_fr03_dismissal_counts_match_hand_count_and_skip_online_sections() -> None: ...


@step(3)
def test_fr04_every_weekday_slot_has_probability_and_confidence() -> None: ...


@step(3)
def test_fr05_each_turnover_flag_names_a_dismissal_in_prior_15_minutes() -> None: ...


@step(3)
def test_forecasts_are_saved_as_draft_model_version() -> None: ...


@step(3)
def test_fr13_forecast_excludes_stuck_counter_readings() -> None: ...


@step(4)
def test_fr06_recommendation_matches_hand_calculation_within_5_minutes() -> None: ...


@step(4)
def test_fr07_never_recommends_disallowed_facility() -> None: ...


@step(4)
def test_recommendations_use_only_validated_models() -> None: ...


@step(4)
def test_nfr01_recommendation_returns_within_3_seconds() -> None: ...


@step(5)
def test_fr10_each_upcoming_entry_shows_a_recommendation() -> None: ...


@step(6)
def test_fr08_explanations_contain_no_unsupported_claims() -> None: ...


@step(6)
def test_fr08_llm_timeout_falls_back_to_template() -> None: ...


@step(6)
def test_nfr08_llm_prompt_contains_no_personal_data() -> None: ...


@step(7)
def test_fr11_feedback_links_to_recommendation_and_rejects_duplicates() -> None: ...


@step(7)
def test_fr12_model_below_80_percent_cannot_be_approved() -> None: ...


@step(8)
def test_fr09_stale_or_atypical_data_adds_warning_and_caps_confidence() -> None: ...


@step(8)
def test_nfr05_delete_me_removes_all_entries_and_feedback() -> None: ...
