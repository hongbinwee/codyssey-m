import json
from types import SimpleNamespace

import httpx
import pytest
from openai import OpenAI

from app.core.config import get_settings
from app.services import openai_service


def test_settings_read_openai_compatible_base_url(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "https://copa.codyssey.kr/v1")
    get_settings.cache_clear()
    try:
        assert get_settings().openai_base_url == "https://copa.codyssey.kr/v1"
    finally:
        get_settings.cache_clear()


def test_chat_uses_compatible_endpoint_with_summary_as_system_message(monkeypatch):
    monkeypatch.setattr(
        openai_service,
        "get_settings",
        lambda: SimpleNamespace(openai_model="gpt-5-mini", openai_max_completion_tokens=2048),
    )

    def respond(request):
        assert request.method == "POST"
        assert str(request.url) == "https://copa.codyssey.kr/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer test-virtual-key"
        body = json.loads(request.content)
        assert body["model"] == "gpt-5-mini"
        assert 0 < body["max_completion_tokens"] <= 2048
        assert body["messages"] == [
            {"role": "system", "content": "요약: 지난 7일 120분"},
            {"role": "user", "content": "최근 바빴어?"},
        ]
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 1,
                "model": "gpt-5-mini",
                "choices": [
                    {"index": 0, "message": {"role": "assistant", "content": "지난 7일 120분입니다."}, "finish_reason": "stop"}
                ],
            },
        )

    client = OpenAI(
        api_key="test-virtual-key",
        base_url="https://copa.codyssey.kr/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(respond)),
    )
    service = openai_service.OpenAIService(client=client)

    assert service.answer("요약: 지난 7일 120분", "최근 바빴어?") == "지난 7일 120분입니다."


def test_provider_error_is_readable_without_exposing_provider_details(monkeypatch):
    monkeypatch.setattr(openai_service, "get_settings", lambda: SimpleNamespace(
        openai_model="gpt-5-mini", openai_max_completion_tokens=2048,
    ))
    client = OpenAI(
        api_key="test-virtual-key", max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(
            429, json={"error": {"message": "private-provider-detail", "type": "rate_limit"}},
        ))),
    )
    service = openai_service.OpenAIService(client=client)
    with pytest.raises(RuntimeError) as error:
        service.answer("요약", "질문")
    assert "다시" in str(error.value)
    assert "private-provider-detail" not in str(error.value)
