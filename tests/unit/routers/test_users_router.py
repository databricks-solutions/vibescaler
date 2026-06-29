from datetime import datetime

import pytest

from server.models import User, UserRole, UserStatus


@pytest.mark.spec("AUTHENTICATION_SPEC")
@pytest.mark.req("No \"permission denied\" errors on normal login")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_user_permissions_derived_from_role(async_client, app):
    import server.routers.users as users_router

    u = User(
        id="u1",
        email="u@example.com",
        name="U",
        role=UserRole.SME,
        workshop_id="w1",
        status=UserStatus.ACTIVE,
        created_at=datetime.now(),
        last_active=None,
    )

    class FakeDBService:
        def get_user(self, user_id: str):
            assert user_id == "u1"
            return u

    app.dependency_overrides[users_router.get_database_service] = lambda: FakeDBService()
    try:
        resp = await async_client.get("/api/users/u1/permissions")
        assert resp.status_code == 200
        body = resp.json()
        # SMEs cannot create rubric and cannot view rubric (facilitator shares)
        assert body["can_create_rubric"] is False
        assert body["can_view_rubric"] is False
    finally:
        app.dependency_overrides.pop(users_router.get_database_service, None)
