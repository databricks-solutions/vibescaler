import pytest


@pytest.mark.spec("BUILD_AND_DEPLOY_SPEC")
@pytest.mark.req("API endpoints respond correctly")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    """Smoke: the real ASGI app answers /health.

    Frontend serving is covered by tests/unit/test_build_deploy.py
    (TestServerServesFrontend); API routes over a real DB are covered by
    tests/integration/test_build_deploy_runtime.py.
    """
    resp = await async_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
