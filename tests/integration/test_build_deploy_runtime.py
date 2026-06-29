"""Integration tests for BUILD_AND_DEPLOY_SPEC runtime criteria.

Genuine behavior coverage for the deployment criteria that used to be tagged
to config-string meta-tests: real HTTP requests through the real FastAPI app
into a real database (SQLite in-memory by default, Postgres via
``--backend postgres``).
"""

import pytest
from sqlalchemy import text

pytestmark = [
    pytest.mark.integration,
    pytest.mark.spec("BUILD_AND_DEPLOY_SPEC"),
    pytest.mark.asyncio,
]


@pytest.mark.req("API endpoints respond correctly")
async def test_api_endpoints_respond(client, seed_workshop):
    """Health, list, and detail endpoints respond over HTTP with a real DB."""
    ws = seed_workshop(name="Deploy Smoke Workshop")

    health = await client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}

    listing = await client.get("/workshops/")
    assert listing.status_code == 200
    assert any(w["id"] == ws.id for w in listing.json())

    detail = await client.get(f"/workshops/{ws.id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Deploy Smoke Workshop"


@pytest.mark.req("Database connection established")
async def test_database_connection_established(client, integration_db):
    """A real database connection is open and usable by the app.

    Asserts both directly (SELECT 1 over the SQLAlchemy session) and through
    the HTTP stack (a route that must hit the DB to answer).
    """
    assert integration_db.execute(text("SELECT 1")).scalar() == 1

    resp = await client.get("/workshops/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
