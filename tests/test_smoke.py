"""Smoke tests: the package imports, settings load, and the API responds."""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from parkwindow import __version__
from parkwindow.api.app import app
from parkwindow.config import Settings

MODULES = [
    "parkwindow.config",
    "parkwindow.models",
    "parkwindow.db",
    "parkwindow.api.app",
    "parkwindow.services.permits",
    "parkwindow.services.recommendation",
    "parkwindow.services.explanation",
    "parkwindow.services.feedback",
    "parkwindow.pipeline.sources",
    "parkwindow.pipeline.ingestion",
    "parkwindow.pipeline.forecast",
    "parkwindow.pipeline.accuracy",
    "parkwindow.web",
]


@pytest.mark.parametrize("module", MODULES)
def test_every_component_module_imports(module: str) -> None:
    importlib.import_module(module)


def test_health_endpoint_reports_ok() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("OCCUPANCY_SOURCE", "LLM_API_KEY", "SYNTHETIC_SEED"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr("parkwindow.config.load_dotenv", lambda: None)
    settings = Settings.from_env()
    assert settings.occupancy_source == "synthetic"
    assert settings.synthetic_seed == 42
    assert settings.llm_enabled is False  # no key -> template explanations


def test_settings_reject_unknown_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OCCUPANCY_SOURCE", "parking_services_live")
    monkeypatch.setattr("parkwindow.config.load_dotenv", lambda: None)
    with pytest.raises(ValueError):
        Settings.from_env()
