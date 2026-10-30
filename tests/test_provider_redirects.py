"""Provider credentials stay on the selected request, never a redirect."""

import urllib.request

import pytest

from knowledge import providers


@pytest.mark.parametrize("header", ["Authorization", "x-api-key"])
@pytest.mark.parametrize("redirect", ["http://other.example/messages", "https://other.example/messages"])
def test_provider_credentials_are_not_forwarded(monkeypatch, header, redirect):
    requests = []

    class Response:
        def read(self):
            return b"{}"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        requests.append(request)
        return Response()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert providers._post(
        "https://configured.example/messages", {header: "dummy-redirect-credential"}, {}, 1,
    ) == {}
    assert requests[0].get_header(header.capitalize()) == "dummy-redirect-credential"

    redirected = urllib.request.HTTPRedirectHandler().redirect_request(
        requests[0], None, 302, "Found", {}, redirect,
    )
    assert redirected.get_header(header.capitalize()) is None
