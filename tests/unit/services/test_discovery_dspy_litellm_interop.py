"""Tests for LiteLLM cross-provider interop configuration in discovery_dspy.

Discovery and follow-up question generation pass hardcoded sampling params
(temperature=0.2/0.3) into DSPy → LiteLLM. Some models reject those params:
gpt-5 / gpt-5-codex / gpt-5.1 require temperature=1, Gemini Flash 3.5 may
reject sampling params on certain Databricks shim versions. Setting
``litellm.drop_params = True`` lets LiteLLM silently strip incompatible
params per-model so the same code path works across Claude 4.6/4.7, the
gpt-5 family, and Gemini Flash 3.5 when served via Databricks.
"""

import pytest

import server.services.discovery_dspy as dspy_module
from server.services.discovery_dspy import _configure_litellm_drop_params


@pytest.fixture
def reset_litellm_configured():
    """Reset the module's idempotency guard so each test exercises the helper."""
    original_guard = dspy_module._LITELLM_CONFIGURED
    dspy_module._LITELLM_CONFIGURED = False
    yield
    dspy_module._LITELLM_CONFIGURED = original_guard


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_configure_litellm_drop_params_enables_cross_provider_interop(reset_litellm_configured):
    """Without drop_params=True, gpt-5 family raises UnsupportedParamsError on
    temperature=0.3 and Gemini may reject other sampling params. The helper
    must enable drop_params so cross-provider follow-up + discovery work."""
    import litellm

    original = litellm.drop_params
    try:
        litellm.drop_params = False
        _configure_litellm_drop_params()
        assert litellm.drop_params is True
    finally:
        litellm.drop_params = original


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_configure_litellm_drop_params_is_idempotent(reset_litellm_configured):
    """Calling the helper twice must not raise and must leave drop_params=True."""
    import litellm

    original = litellm.drop_params
    try:
        _configure_litellm_drop_params()
        _configure_litellm_drop_params()
        assert litellm.drop_params is True
    finally:
        litellm.drop_params = original


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req(
    "Facilitator can select LLM model for follow-up question generation in Discovery dashboard"
)
@pytest.mark.unit
def test_import_dspy_configures_litellm(reset_litellm_configured, monkeypatch):
    """_import_dspy must configure litellm.drop_params so every LM construction
    path (build_databricks_lm, build_custom_llm) inherits the cross-provider
    fix without requiring callers to opt in."""
    import litellm

    original = litellm.drop_params
    litellm.drop_params = False
    try:
        dspy_module._import_dspy()
        assert litellm.drop_params is True
    finally:
        litellm.drop_params = original
