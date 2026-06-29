"""Tests for public redirect URL rewriting on Databricks Apps."""

from starlette.requests import Request

from server.app import _public_redirect_url


def _request(headers: list[tuple[bytes, bytes]] | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": headers or [],
        "query_string": b"",
        "client": ("127.0.0.1", 8000),
        "server": ("localhost", 8000),
        "scheme": "http",
    }
    return Request(scope)


def test_relative_location_is_unchanged():
    request = _request()
    assert _public_redirect_url(request, "/docs/lakebase-setup/") == "/docs/lakebase-setup/"


def test_localhost_location_becomes_relative_without_forwarded_headers():
    request = _request()
    assert (
        _public_redirect_url(request, "http://localhost:8000/docs/lakebase-setup/")
        == "/docs/lakebase-setup/"
    )


def test_localhost_location_uses_forwarded_host_when_present():
    request = _request(
        [
            (b"x-forwarded-host", b"jbw4-7395834863327820.aws.databricksapps.com"),
            (b"x-forwarded-proto", b"https"),
        ]
    )
    assert (
        _public_redirect_url(request, "http://localhost:8000/docs/lakebase-setup/")
        == "https://jbw4-7395834863327820.aws.databricksapps.com/docs/lakebase-setup/"
    )
