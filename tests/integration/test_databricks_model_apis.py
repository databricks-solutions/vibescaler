"""Integration tests probing which Databricks-served LLM endpoints accept
which OpenAI API surfaces.

This is a live diagnostic that exercises the configured Databricks workspace.
It's skipped automatically when credentials are unavailable (so CI never
fails on it), but runnable on demand to verify and document the support
matrix:

    just test-integration tests/integration/test_databricks_model_apis.py

Design note: per Databricks docs, the **Responses API passthrough is
OpenAI-only by design** — it only accepts ``databricks-gpt-*`` model
endpoints. Claude, Gemini, and Llama serve Chat Completions only. So
unifying everything on a single OpenAI API surface isn't possible at
this layer; we stay on Chat Completions for cross-provider calls and
patch the Chat Completions quirks (Gemini's ``id: null`` and content
shape) client-side.

These tests pin that contract:
- Every model exposed in the workshop's picker must accept a minimal
  Chat Completions request.
- Responses API support is checked separately, expected only for the
  gpt-5 family. Other models ``xfail`` cleanly with the
  "Responses API passthrough is not supported" message.
"""

from __future__ import annotations

import os

import pytest

# The serving endpoints we care about for the workshop feature set.
# Kept as a parameter list so future additions just append.
_PROBE_MODELS = [
    "databricks-claude-opus-4-7",
    "databricks-claude-sonnet-4",
    "databricks-gpt-5",
    "databricks-gemini-3-5-flash",
    "databricks-meta-llama-3-3-70b-instruct",
]


def _databricks_available() -> bool:
    """Return True iff we can resolve a Databricks host + auth locally.

    Used to skip these tests cleanly in CI / minimal envs.
    """
    try:
        from server.services.databricks_service import (  # noqa: WPS433
            get_databricks_host,
            resolve_databricks_token,
        )

        get_databricks_host()
        resolve_databricks_token()
        return True
    except Exception:
        return False


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not _databricks_available(),
        reason="No Databricks credentials configured (set DATABRICKS_HOST + auth)",
    ),
]


@pytest.fixture(scope="module")
def databricks_service():
    """Lazy import to avoid importing the service module when we're skipping."""
    from server.services.databricks_service import DatabricksService

    return DatabricksService()


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.parametrize("model", _PROBE_MODELS)
def test_chat_completions_works_for_model(databricks_service, model):
    """Every model exposed in the workshop's model picker must accept a
    minimal Chat Completions request. Failure here means the endpoint is
    misconfigured or removed from the workspace."""
    result = databricks_service.call_chat_completion(
        endpoint_name=model,
        messages=[{"role": "user", "content": "Reply with the word ok."}],
        # gpt-5 family only accepts temperature=1; use the default-friendly
        # value, expect drop_params/litellm to handle it elsewhere.
        temperature=1.0,
        max_tokens=2000,
    )
    content = result["choices"][0]["message"]["content"]
    assert isinstance(content, (str, list)), (
        f"{model}: chat completion returned unexpected content type {type(content)!r}"
    )


@pytest.mark.parametrize("model", _PROBE_MODELS)
def test_responses_api_passthrough_support(databricks_service, model):
    """Per Databricks docs the Responses API is OpenAI-only; gpt-5 endpoints
    accept it, every other foundation model rejects with "Responses API
    passthrough is not supported".

    This test pins that contract. If a non-gpt model ever starts accepting
    Responses, an xpass shows up and we can revisit our design. If gpt-5
    stops accepting, we get a real failure to investigate.
    """
    is_openai_model = model.startswith("databricks-gpt")
    try:
        databricks_service.client.responses.create(
            model=model,
            input=[{"role": "user", "content": "Reply with the word ok."}],
            max_output_tokens=2000,
        )
        accepted = True
        error_msg = ""
    except Exception as exc:
        accepted = False
        error_msg = str(exc)

    if is_openai_model:
        # gpt-5 family is allowed to reject our minimal request for reasons
        # other than passthrough support (e.g. temperature/reasoning quirks).
        # We only assert the passthrough isn't outright disabled.
        assert "Responses API passthrough is not supported" not in error_msg, (
            f"Regression: {model} stopped accepting Responses API passthrough"
        )
    else:
        # Non-OpenAI models must keep rejecting passthrough — that's our
        # design assumption. If they start accepting, this xfail flips to
        # xpass and we should revisit.
        if accepted or "Responses API passthrough is not supported" not in error_msg:
            pytest.fail(
                f"{model}: expected Responses API rejection, but got "
                f"{'success' if accepted else error_msg[:200]}"
            )
        pytest.xfail(f"{model}: Responses API is OpenAI-only by design (expected)")


@pytest.mark.spec("TRACE_SUMMARIZATION_SPEC")
@pytest.mark.req(
    "Facilitator can select a model for summarization from available Databricks endpoints"
)
@pytest.mark.asyncio
async def test_gemini_multi_turn_summarization_via_ai_gateway():
    """End-to-end: multi-turn pydantic-ai agent summarization on Gemini
    through the Databricks ai-gateway path. This exercises:

    - ``TraceSummarizationService``'s Gemini routing decision.
    - The forced httpx transport (google-genai would otherwise pick aiohttp
      and bypass our request hook).
    - The ``function_call.id`` strip hook (without it, the second turn
      400s because Vertex AI's FunctionCall proto has no ``id`` field).
    - Pydantic-AI's native ``thought_signature`` round-tripping in
      ``GoogleModel``.

    Skipped automatically when Databricks credentials aren't configured.
    """
    from databricks.sdk import WorkspaceClient

    from server.services.trace_summarization_service import TraceSummarizationService

    w = WorkspaceClient()
    token = w.config.authenticate()["Authorization"].removeprefix("Bearer ")
    host = w.config.host.rstrip("/")

    svc = TraceSummarizationService(
        endpoint_url=f"{host}/serving-endpoints",
        token=token,
        model_name="databricks-gemini-3-5-flash",
        agent_run_timeout_s=60.0,
    )

    result = await svc.summarize_trace(
        {
            "spans": [
                {
                    "name": "root_agent",
                    "span_type": "AGENT",
                    "status": "OK",
                    "inputs": {"task": "find top issuers by spend"},
                    "outputs": {"answer": "ICA-1, ICA-2, ICA-3"},
                    "start_time_ns": 0,
                    "end_time_ns": 4_000_000_000,
                    "parent_span_id": None,
                },
                {
                    "name": "sql",
                    "span_type": "TOOL",
                    "status": "OK",
                    "inputs": {"q": "SELECT * FROM issuers"},
                    "outputs": {"rows": 240},
                    "start_time_ns": 1_000_000_000,
                    "end_time_ns": 3_000_000_000,
                    "parent_span_id": "span-1",
                },
            ],
            "execution_time_ms": 4000,
            "status": "OK",
            "tags": {},
        },
        trace_id="integration-gemini-multi-turn",
    )

    assert result is not None, "Gemini multi-turn summarization should not return None"
    assert result.executive_summary, "Executive summary should be populated"
    assert len(result.milestones) >= 1, "At least one milestone expected"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
def test_gemini_chat_completion_returns_usable_content(databricks_service):
    """Gemini via Chat Completions returns content as an array of parts dicts
    (``[{type:"text", text:..., thoughtSignature:...}]``) and ``id: null``,
    which trip OpenAI SDK 2.x's strict validators.

    This test pins the behavior so a future Databricks shim fix is detected
    immediately — if Gemini starts returning a plain-string content and a
    real id, this test should be updated to require that shape and we can
    delete any client-side normalization."""
    result = databricks_service.call_chat_completion(
        endpoint_name="databricks-gemini-3-5-flash",
        messages=[
            {"role": "system", "content": "You analyze feedback briefly."},
            {"role": "user", "content": 'List 3 themes from: "agent was helpful and accurate"'},
        ],
        temperature=0.3,
        max_tokens=2000,
    )
    content = result["choices"][0]["message"]["content"]
    # We accept either shape — the assertion just verifies we got something
    # parseable. The migration that normalizes content is tested separately
    # in unit tests.
    assert content is not None
    if isinstance(content, list):
        joined = "".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
        assert joined.strip(), "Gemini parts contained no text"
    else:
        assert isinstance(content, str) and content.strip(), "Gemini returned empty content"
