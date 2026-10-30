"""The OpenAI key is only sent over https or to loopback http (OPENAI_BASE_URL is env-overridable)."""

import urllib.request

import pytest

from knowledge import providers
from knowledge.errors import SETUP, ToolError
from knowledge.providers import Route, token_url_allowed


@pytest.mark.parametrize("url", ["https://api.openai.com/v1", "http://localhost:8000/v1",
                                 "http://127.0.0.1:1/v1", "http://[::1]:1/v1"])
def test_allowed(url):
    assert token_url_allowed(url)


@pytest.mark.parametrize("url", ["http://example.com/v1", "http://localhost.evil.com", "ftp://x", "file:///x", "x.com", ""])
def test_refused(url):
    assert not token_url_allowed(url)


def test_openai_refuses_insecure_base_without_network(monkeypatch):
    called = []
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: called.append(1))
    monkeypatch.setenv("OPENAI_API_KEY", "sekret")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://example.com/v1")
    with pytest.raises(ToolError) as ei:
        providers.call(Route("openai", "m"), "s", "p")
    assert ei.value.exit_code == SETUP
    assert "sekret" not in str(ei.value)
    assert not called


def test_openai_loopback_sends_key(monkeypatch):
    seen = {}

    def fake_post(url, headers, body, timeout):
        seen.update(url=url, headers=headers)
        return {"choices": [{"message": {"content": "ok"}}]}

    monkeypatch.setattr(providers, "_post", fake_post)
    monkeypatch.setenv("OPENAI_API_KEY", "sekret")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:9/v1")
    assert providers.call(Route("openai", "m"), "s", "p") == "ok"
    assert seen["headers"]["Authorization"] == "Bearer sekret"


def test_default_openai_url_unchanged(monkeypatch):
    seen = {}
    monkeypatch.setattr(providers, "_post", lambda url, h, b, t: seen.update(url=url) or {"choices": [{"message": {"content": ""}}]})
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    providers.call(Route("openai", "m"), "s", "p")
    assert seen["url"] == "https://api.openai.com/v1/chat/completions"
