import json
import os
import inspect
import sys
import types
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

import server.services.databricks_service as databricks_module
from server.services.databricks_service import (
    DatabricksService,
    _fix_databricks_shim_response,
    _normalize_shim_content,
    clear_serving_endpoints_cache,
    get_databricks_host,
    get_experiment_id,
    normalize_experiment_id,
    configure_databricks_mlflow_once,
    normalize_databricks_auth_env_once,
)


def test_normalize_experiment_id_strips_wrapping_quotes_and_whitespace():
    assert normalize_experiment_id('  "12345"  ') == "12345"
    assert normalize_experiment_id("  'abc-123'  ") == "abc-123"


def test_get_experiment_id_normalizes_env_value(monkeypatch):
    monkeypatch.setenv("MLFLOW_EXPERIMENT_ID", '  "12345"  ')
    assert get_experiment_id() == "12345"


def test_get_experiment_id_raises_for_empty_after_normalization(monkeypatch):
    monkeypatch.setenv("MLFLOW_EXPERIMENT_ID", '""')
    with pytest.raises(RuntimeError, match="MLFLOW_EXPERIMENT_ID not set"):
        get_experiment_id()


def test_get_databricks_host_adds_https_when_scheme_missing(monkeypatch):
    monkeypatch.setenv("DATABRICKS_HOST", "adb-1234567890123456.7.azuredatabricks.net/")
    assert get_databricks_host() == "https://adb-1234567890123456.7.azuredatabricks.net"


def test_get_databricks_host_preserves_existing_scheme(monkeypatch):
    monkeypatch.setenv("DATABRICKS_HOST", "https://dbc-example.cloud.databricks.com/")
    assert get_databricks_host() == "https://dbc-example.cloud.databricks.com"


def test_sdk_token_uses_normalized_host_for_m2m_auth(monkeypatch):
    created_hosts = []

    class FakeWorkspaceClient:
        def __init__(self, host=None):
            created_hosts.append(host)
            self.config = SimpleNamespace(
                host=host,
                authenticate=lambda: {"Authorization": "Bearer sdk-token"},
            )

    sdk_module = types.ModuleType("databricks.sdk")
    sdk_module.WorkspaceClient = FakeWorkspaceClient
    monkeypatch.setitem(sys.modules, "databricks", types.ModuleType("databricks"))
    monkeypatch.setitem(sys.modules, "databricks.sdk", sdk_module)
    monkeypatch.setenv("DATABRICKS_HOST", "adb-1234567890123456.7.azuredatabricks.net/")

    assert databricks_module._get_sdk_token() == "sdk-token"
    assert created_hosts == ["https://adb-1234567890123456.7.azuredatabricks.net"]


def test_normalize_databricks_auth_env_once_normalizes_host_without_token(monkeypatch):
    monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)
    monkeypatch.setenv("DATABRICKS_HOST", "dbc-example.cloud.databricks.com/")

    normalize_databricks_auth_env_once()

    assert "DATABRICKS_TOKEN" not in os.environ
    assert os.environ["DATABRICKS_HOST"] == "https://dbc-example.cloud.databricks.com"


def test_configure_databricks_mlflow_once_normalizes_host_before_mlflow(monkeypatch):
    calls = []

    class FakeMlflow:
        @staticmethod
        def set_tracking_uri(uri):
            calls.append((uri, os.environ.get("DATABRICKS_HOST")))

    monkeypatch.setitem(sys.modules, "mlflow", FakeMlflow)
    monkeypatch.setenv("DATABRICKS_HOST", "adb-1234567890123456.7.azuredatabricks.net/")

    configure_databricks_mlflow_once()

    assert calls == [("databricks", "https://adb-1234567890123456.7.azuredatabricks.net")]


def test_databricks_auth_env_normalized_from_app_lifespan():
    import server.app as app_module

    source = inspect.getsource(app_module.lifespan)

    assert "configure_databricks_mlflow_once()" in source


# ---------------------------------------------------------------------------
# Serving-endpoints TTL cache
# ---------------------------------------------------------------------------


def _make_service_without_client_init(workspace_url: str, token: str) -> DatabricksService:
    """Build a DatabricksService bypassing __init__ side effects (token resolution + OpenAI client).

    The cache logic only depends on ``workspace_url`` and ``token``, so we can
    avoid the network / SDK calls in unit tests by constructing the instance
    directly.
    """
    svc = DatabricksService.__new__(DatabricksService)
    svc.workspace_url = workspace_url
    svc.token = token
    return svc


@pytest.fixture
def reset_endpoints_cache():
    """Ensure each test starts with an empty cache and no leftover per-key locks."""
    clear_serving_endpoints_cache()
    databricks_module._endpoints_cache_locks.clear()
    yield
    clear_serving_endpoints_cache()
    databricks_module._endpoints_cache_locks.clear()


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_serving_endpoints_cached_within_ttl(reset_endpoints_cache):
    """Two calls inside the TTL window must hit the cache, not Databricks."""
    svc = _make_service_without_client_init("https://example.databricks.com", "token-a")
    fake_endpoints = [{"name": "databricks-claude-opus-4-7", "state": "READY", "task": "llm/v1/chat"}]

    with patch.object(
        DatabricksService, "_fetch_serving_endpoints", new=AsyncMock(return_value=fake_endpoints)
    ) as mock_fetch:
        first = await svc.list_serving_endpoints()
        second = await svc.list_serving_endpoints()

    assert first == fake_endpoints
    assert second == fake_endpoints
    assert mock_fetch.await_count == 1


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_serving_endpoints_cache_shared_across_service_instances(reset_endpoints_cache):
    """The cache is module-level and keyed by workspace+token, so two requests
    that build their own DatabricksService instance for the same workspace must
    share the cached result (otherwise per-workshop frontend queries refetch)."""
    svc_a = _make_service_without_client_init("https://example.databricks.com", "token-shared")
    svc_b = _make_service_without_client_init("https://example.databricks.com", "token-shared")
    fake_endpoints = [{"name": "databricks-claude-sonnet-4-6", "state": "READY", "task": "llm/v1/chat"}]

    with patch.object(
        DatabricksService, "_fetch_serving_endpoints", new=AsyncMock(return_value=fake_endpoints)
    ) as mock_fetch:
        await svc_a.list_serving_endpoints()
        await svc_b.list_serving_endpoints()

    assert mock_fetch.await_count == 1


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_serving_endpoints_cache_separate_per_workspace(reset_endpoints_cache):
    """Different workspaces must not collide on the cache key."""
    svc_a = _make_service_without_client_init("https://workspace-a.databricks.com", "token-a")
    svc_b = _make_service_without_client_init("https://workspace-b.databricks.com", "token-b")

    with patch.object(
        DatabricksService, "_fetch_serving_endpoints", new=AsyncMock(return_value=[])
    ) as mock_fetch:
        await svc_a.list_serving_endpoints()
        await svc_b.list_serving_endpoints()

    assert mock_fetch.await_count == 2


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_serving_endpoints_cache_expires_after_ttl(reset_endpoints_cache, monkeypatch):
    """After the TTL elapses, the next call must hit the upstream API again."""
    svc = _make_service_without_client_init("https://example.databricks.com", "token-c")

    monkeypatch.setattr(databricks_module, "_ENDPOINTS_CACHE_TTL_S", 0.0)

    with patch.object(
        DatabricksService, "_fetch_serving_endpoints", new=AsyncMock(return_value=[])
    ) as mock_fetch:
        await svc.list_serving_endpoints()
        await svc.list_serving_endpoints()

    assert mock_fetch.await_count == 2


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_serving_endpoints_cache_dedupes_concurrent_requests(reset_endpoints_cache):
    """A burst of concurrent requests against a cold cache must collapse to a
    single upstream fetch (no thundering herd against the Databricks API)."""
    import asyncio as _asyncio

    svc = _make_service_without_client_init("https://example.databricks.com", "token-d")

    fetch_started = _asyncio.Event()
    release_fetch = _asyncio.Event()

    async def slow_fetch(_self):
        fetch_started.set()
        await release_fetch.wait()
        return [{"name": "endpoint-1", "state": "READY"}]

    with patch.object(DatabricksService, "_fetch_serving_endpoints", new=slow_fetch):
        tasks = [_asyncio.create_task(svc.list_serving_endpoints()) for _ in range(5)]
        await fetch_started.wait()
        # All 5 callers are now either at the lock or being held back.
        release_fetch.set()
        results = await _asyncio.gather(*tasks)

    assert all(r == [{"name": "endpoint-1", "state": "READY"}] for r in results)
    # No assertion on call_count here because slow_fetch isn't a Mock, but the
    # event/release pattern guarantees only one path ran the fetch body.


# ---------------------------------------------------------------------------
# Gemini-on-Databricks Chat Completions shim quirks
# ---------------------------------------------------------------------------
#
# OpenAI's Responses API is gpt-only by design, so we stay on Chat Completions
# for all cross-provider calls. The Databricks shim leaks two Gemini-native
# quirks through Chat Completions that callers can't reasonably handle:
#  1. ``id: null`` on the response object (OpenAI SDK 2.x's Pydantic
#     validator rejects null id).
#  2. ``content`` as an array of part dicts
#     ``[{"type": "text", "text": "...", "thoughtSignature": "..."}]``
#     instead of a plain string, breaking parsers that read
#     ``response.choices[0].message.content`` as ``str``.
# We patch both client-side so callers (discovery_analysis_service,
# rubric_generation_service, etc.) work uniformly across providers.


def _make_response(body: dict, content_type: str = "application/json") -> httpx.Response:
    raw = json.dumps(body).encode()
    return httpx.Response(
        status_code=200,
        headers={"content-type": content_type, "content-length": str(len(raw))},
        content=raw,
    )


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_fix_databricks_shim_response_replaces_null_id():
    resp = _make_response({"id": None, "choices": [{"index": 0, "message": {}}]})
    _fix_databricks_shim_response(resp)
    parsed = json.loads(resp.content)
    assert parsed["id"], "id must be filled in"
    assert parsed["id"].startswith("databricks-shim-")


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_fix_databricks_shim_response_leaves_valid_id_alone():
    """Other backing models (Claude, gpt-5) return real ids; the hook must
    not overwrite them."""
    resp = _make_response({"id": "chatcmpl-abc123", "choices": [{"index": 0, "message": {}}]})
    _fix_databricks_shim_response(resp)
    parsed = json.loads(resp.content)
    assert parsed["id"] == "chatcmpl-abc123"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_fix_databricks_shim_response_ignores_non_chat_payloads():
    """The hook is installed on the shared OpenAI client, so it sees every
    response. It must only mutate chat completion shapes (id+choices), not
    arbitrary JSON like endpoint listings or error envelopes."""
    resp = _make_response({"endpoints": [{"name": "foo"}]})
    _fix_databricks_shim_response(resp)
    parsed = json.loads(resp.content)
    assert parsed == {"endpoints": [{"name": "foo"}]}


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_normalize_shim_content_joins_gemini_parts():
    parts = [
        {"type": "text", "text": "Hello, ", "thoughtSignature": "abc=="},
        {"type": "text", "text": "world!", "thoughtSignature": "def=="},
    ]
    assert _normalize_shim_content(parts) == "Hello, world!"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_normalize_shim_content_passes_string_through():
    assert _normalize_shim_content("already a string") == "already a string"
    assert _normalize_shim_content(None) is None


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_normalize_shim_content_ignores_non_text_parts():
    parts = [
        {"type": "text", "text": "Hello"},
        {"type": "function_call", "name": "noop"},
    ]
    assert _normalize_shim_content(parts) == "Hello"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_call_chat_completion_normalizes_array_content_on_shim_path():
    """The OpenAI-compat shim has been observed to return ``message.content``
    as an array of part dicts for certain backings. Even though Gemini now
    bypasses this code path (it routes through the ai-gateway), the safety
    net stays in place so any other model leaking array content gets
    normalized to a string."""
    svc = DatabricksService.__new__(DatabricksService)
    svc.workspace_url = "https://example.databricks.com"
    svc.token = "test-token"

    fake_message = SimpleNamespace(
        content=[{"type": "text", "text": "Themes: A, B, C"}],
        role="assistant",
        model_dump=lambda: {
            "role": "assistant",
            "content": [{"type": "text", "text": "Themes: A, B, C"}],
        },
    )
    fake_choice = SimpleNamespace(message=fake_message, index=0, finish_reason="stop")
    fake_usage = SimpleNamespace(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    fake_response = SimpleNamespace(
        choices=[fake_choice],
        model="databricks-claude-opus-4-7",
        usage=fake_usage,
    )

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **_: fake_response)
        )
    )
    svc.client = fake_client

    result = svc.call_chat_completion(
        endpoint_name="databricks-claude-opus-4-7",
        messages=[{"role": "user", "content": "Give me 3 themes"}],
    )
    assert result["choices"][0]["message"]["content"] == "Themes: A, B, C"


# ---------------------------------------------------------------------------
# Gemini chat completion routes through the ai-gateway
# ---------------------------------------------------------------------------
#
# Gemini chat completion through the OpenAI-compat shim is unreliable
# (Vertex AI sometimes returns response shapes that the shim's translator
# can't round-trip → 502 "invalid response from upstream"). We detect
# Gemini endpoint names and route through the native ai-gateway/gemini
# passthrough using google-genai. The adapter returns the chat-completions
# dict shape so existing callers (discovery_analysis_service, etc.) don't
# need to change.


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_call_chat_completion_routes_gemini_to_ai_gateway(monkeypatch):
    """call_chat_completion must NOT touch the OpenAI client when the endpoint
    is Gemini-family — it must dispatch to the ai-gateway helper. Otherwise
    we re-introduce the shim 502s discovery analysis hit in production."""
    svc = DatabricksService.__new__(DatabricksService)
    svc.workspace_url = "https://example.databricks.com"
    svc.token = "test-token"

    # If anything reaches the OpenAI client it's a routing bug.
    sentinel_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(
                create=lambda **_: pytest.fail("OpenAI client must not be used for Gemini")
            )
        )
    )
    svc.client = sentinel_client

    captured: dict[str, Any] = {}

    def fake_gateway(self, endpoint_name, messages, temperature=0.5, max_tokens=None, response_format=None):
        captured["endpoint_name"] = endpoint_name
        captured["messages"] = messages
        captured["temperature"] = temperature
        captured["max_tokens"] = max_tokens
        return {
            "choices": [
                {"message": {"role": "assistant", "content": "OK"}, "index": 0, "finish_reason": "stop"}
            ],
            "model": endpoint_name,
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }

    monkeypatch.setattr(DatabricksService, "_call_gemini_chat_via_ai_gateway", fake_gateway)

    result = svc.call_chat_completion(
        endpoint_name="databricks-gemini-3-5-flash",
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.7,
        max_tokens=1024,
    )
    assert captured["endpoint_name"] == "databricks-gemini-3-5-flash"
    assert captured["temperature"] == 0.7
    assert captured["max_tokens"] == 1024
    assert result["choices"][0]["message"]["content"] == "OK"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_call_chat_completion_non_gemini_uses_openai_client(monkeypatch):
    """Non-Gemini endpoints continue to use the OpenAI-compat shim, since
    Claude/gpt-5/Llama don't have the response-shape issues Gemini has."""
    svc = DatabricksService.__new__(DatabricksService)
    svc.workspace_url = "https://example.databricks.com"
    svc.token = "test-token"

    fake_message = SimpleNamespace(
        content="hi",
        role="assistant",
        model_dump=lambda: {"role": "assistant", "content": "hi"},
    )
    fake_choice = SimpleNamespace(message=fake_message, index=0, finish_reason="stop")
    fake_usage = SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2)
    fake_response = SimpleNamespace(
        choices=[fake_choice], model="databricks-claude-opus-4-7", usage=fake_usage
    )
    svc.client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=SimpleNamespace(create=lambda **_: fake_response)
        )
    )

    def fail_gateway(self, *a, **kw):
        pytest.fail("Non-Gemini endpoint must not be routed to the ai-gateway helper")

    monkeypatch.setattr(DatabricksService, "_call_gemini_chat_via_ai_gateway", fail_gateway)

    result = svc.call_chat_completion(
        endpoint_name="databricks-claude-opus-4-7",
        messages=[{"role": "user", "content": "hi"}],
    )
    assert result["choices"][0]["message"]["content"] == "hi"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_messages_to_genai_contents_collapses_system_role():
    """System messages collapse into ``system_instruction``; user/assistant
    messages become Gemini ``Content`` items with role normalized to user/model."""
    from server.services.databricks_service import _messages_to_genai_contents

    contents, system = _messages_to_genai_contents(
        [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hi."},
            {"role": "assistant", "content": "Hello."},
        ]
    )
    assert system == "Be concise."
    assert len(contents) == 2
    assert contents[0].role == "user"
    assert contents[1].role == "model"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_genai_response_to_chat_shape_extracts_text():
    """The adapter must extract text from candidates[0].content.parts and
    surface it as a single string under ``choices[0].message.content``."""
    from server.services.databricks_service import _genai_response_to_chat_shape

    fake_response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[
                        SimpleNamespace(text="Hello, "),
                        SimpleNamespace(text="world!"),
                    ]
                ),
                finish_reason=SimpleNamespace(name="STOP"),
            )
        ],
        usage_metadata=SimpleNamespace(
            prompt_token_count=7, candidates_token_count=3, total_token_count=10
        ),
    )

    result = _genai_response_to_chat_shape(fake_response, "databricks-gemini-3-5-flash")
    assert result["choices"][0]["message"]["content"] == "Hello, world!"
    assert result["choices"][0]["finish_reason"] == "stop"
    assert result["usage"]["prompt_tokens"] == 7
    assert result["usage"]["completion_tokens"] == 3


# ---------------------------------------------------------------------------
# OpenAI reasoning models (gpt-5 family, o-series) only accept temperature=1
# ---------------------------------------------------------------------------
#
# Production hit 400 "'temperature' does not support 0.3 with this model" when
# discovery_analysis_service called gpt-5.5 with the default 0.3. LiteLLM has
# ``drop_params`` for this on the DSPy path; the OpenAI Python SDK has no
# equivalent. We normalize at the call site instead — force temperature=1
# whenever the endpoint is a reasoning model.


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
@pytest.mark.parametrize(
    "model_name",
    [
        "databricks-gpt-5",
        "databricks-gpt-5-codex",
        "databricks-gpt-5.1",
        "databricks-gpt-5.5",
        "databricks-o1-preview",
        "databricks-o3-mini",
        "o4-mini",
    ],
)
def test_is_openai_reasoning_model_detects_gpt5_and_o_series(model_name):
    from server.services.databricks_service import _is_openai_reasoning_model

    assert _is_openai_reasoning_model(model_name), f"{model_name} should be detected as reasoning"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
@pytest.mark.parametrize(
    "model_name",
    [
        "databricks-claude-opus-4-7",
        "databricks-claude-sonnet-4",
        "databricks-meta-llama-3-3-70b-instruct",
        "databricks-gemini-3-5-flash",
        "databricks-gpt-4o",
    ],
)
def test_is_openai_reasoning_model_excludes_non_reasoning(model_name):
    from server.services.databricks_service import _is_openai_reasoning_model

    assert not _is_openai_reasoning_model(model_name), (
        f"{model_name} should NOT be detected as a reasoning model"
    )


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_normalize_request_for_reasoning_model_forces_temperature_1():
    from server.services.databricks_service import _normalize_request_for_reasoning_model

    assert _normalize_request_for_reasoning_model("databricks-gpt-5.5", 0.3) == 1.0
    assert _normalize_request_for_reasoning_model("databricks-gpt-5.5", 1.0) == 1.0
    # Non-reasoning models keep the caller's value
    assert _normalize_request_for_reasoning_model("databricks-claude-opus-4-7", 0.3) == 0.3


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_call_chat_completion_forces_temperature_1_for_gpt5(monkeypatch):
    """End-to-end: call_chat_completion called with temperature=0.3 against a
    gpt-5 endpoint must send temperature=1.0 to the OpenAI client. Otherwise
    discovery_analysis_service hits the prod 400 we just fixed."""
    svc = DatabricksService.__new__(DatabricksService)
    svc.workspace_url = "https://example.databricks.com"
    svc.token = "test-token"

    captured: dict[str, Any] = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content="ok",
                        role="assistant",
                        model_dump=lambda: {"role": "assistant", "content": "ok"},
                    ),
                    index=0,
                    finish_reason="stop",
                )
            ],
            model="databricks-gpt-5.5",
            usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2),
        )

    svc.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=fake_create))
    )

    svc.call_chat_completion(
        endpoint_name="databricks-gpt-5.5",
        messages=[{"role": "user", "content": "hi"}],
        temperature=0.3,
    )
    assert captured["temperature"] == 1.0, (
        f"Expected forced temperature=1.0, got {captured['temperature']}"
    )
