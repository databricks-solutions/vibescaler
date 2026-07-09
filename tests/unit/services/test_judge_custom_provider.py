"""Tests for custom LLM provider helpers in the workshops router.

Covers the helpers behind the CUSTOM_LLM_PROVIDER_SPEC Configuration and
Connection Testing criteria: chat-completions URL construction used by the
connection test endpoint, and the in-memory API key storage key format.

NOTE: judge evaluation does NOT use custom providers — that integration
(proxy_url to MLflow) is unbuilt and tracked under the spec's Roadmap
section. Do not tag tests here to those roadmap criteria.
"""

import pytest


@pytest.mark.spec("CUSTOM_LLM_PROVIDER_SPEC")
@pytest.mark.req("Test Connection button verifies endpoint is reachable")
@pytest.mark.unit
def test_build_chat_completions_url_appends_full_path():
    """A bare base URL (no /v1, no /chat/completions) gets /v1/chat/completions appended."""
    from server.routers.workshops import _build_chat_completions_url

    url = _build_chat_completions_url(
        "https://my-resource.openai.azure.com/openai/deployments/gpt-4"
    )
    assert url == "https://my-resource.openai.azure.com/openai/deployments/gpt-4/v1/chat/completions"


@pytest.mark.spec("CUSTOM_LLM_PROVIDER_SPEC")
@pytest.mark.req("Test Connection button verifies endpoint is reachable")
@pytest.mark.unit
def test_build_chat_completions_url_with_v1_suffix():
    """URL ending with /v1 should get /chat/completions appended."""
    from server.routers.workshops import _build_chat_completions_url

    url = _build_chat_completions_url("https://api.example.com/v1")
    assert url == "https://api.example.com/v1/chat/completions"


@pytest.mark.spec("CUSTOM_LLM_PROVIDER_SPEC")
@pytest.mark.req("Test Connection button verifies endpoint is reachable")
@pytest.mark.unit
def test_build_chat_completions_url_already_has_suffix():
    """URL that already ends with /chat/completions should be returned as-is."""
    from server.routers.workshops import _build_chat_completions_url

    url = _build_chat_completions_url("https://api.example.com/v1/chat/completions")
    assert url == "https://api.example.com/v1/chat/completions"


@pytest.mark.spec("CUSTOM_LLM_PROVIDER_SPEC")
@pytest.mark.req("Test Connection button verifies endpoint is reachable")
@pytest.mark.unit
def test_build_chat_completions_url_strips_trailing_slash():
    """Trailing slashes should be stripped before appending."""
    from server.routers.workshops import _build_chat_completions_url

    url = _build_chat_completions_url("https://api.example.com/v1/")
    # After stripping trailing slash: "https://api.example.com/v1"
    # Ends with /v1, so append /chat/completions
    assert url == "https://api.example.com/v1/chat/completions"


@pytest.mark.spec("CUSTOM_LLM_PROVIDER_SPEC")
@pytest.mark.req("API key is stored securely in memory (not database)")
@pytest.mark.unit
def test_custom_provider_api_key_stored_with_correct_key_format():
    """API keys for custom providers use the format custom_llm_{workshop_id}.

    Per CUSTOM_LLM_PROVIDER_SPEC.md:
    > Storage key is `custom_llm_{workshop_id}`
    """
    from server.routers.workshops import _get_custom_llm_storage_key

    key = _get_custom_llm_storage_key("workshop-123")
    assert key == "custom_llm_workshop-123"
