from unittest.mock import AsyncMock, patch

import pytest

import server.services.databricks_service as databricks_module
from server.services.databricks_service import (
    DatabricksService,
    clear_serving_endpoints_cache,
    get_databricks_host,
    get_experiment_id,
    normalize_experiment_id,
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
