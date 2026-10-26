from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from google.auth.exceptions import DefaultCredentialsError

from app import dependencies
from app.services import openai_service


def test_chat_reports_missing_openai_key_before_loading_firestore(monkeypatch):
    monkeypatch.setattr(
        openai_service,
        "get_settings",
        lambda: SimpleNamespace(openai_api_key="", openai_model="gpt-5.6-luna"),
    )

    def unexpected_repository_load():
        pytest.fail("Firestore must not load when the OpenAI key is absent")

    monkeypatch.setattr(dependencies, "get_repository", unexpected_repository_load)

    with pytest.raises(HTTPException) as error:
        dependencies.get_chat_service()

    assert error.value.status_code == 503
    assert "OPENAI_API_KEY" in str(error.value.detail)


def test_repository_reports_missing_firebase_credentials(monkeypatch):
    dependencies.get_repository.cache_clear()

    def missing_credentials():
        raise DefaultCredentialsError("test: credentials absent")

    monkeypatch.setattr(dependencies, "FirestoreRepository", missing_credentials)

    with pytest.raises(HTTPException) as error:
        dependencies.get_repository()

    assert error.value.status_code == 503
    assert "Firebase" in str(error.value.detail)
