from types import SimpleNamespace

from server.features.auth.providers.databricks_apps import DatabricksAppsIdentityProvider
from server.features.auth.schemas import ProviderRole


def test_databricks_apps_role_lookup_forces_delegated_token_auth(monkeypatch):
    """Apps permission lookup must not mix forwarded user token auth with app SP env auth."""
    calls = []

    class FakeWorkspaceClient:
        def __init__(self, **kwargs):
            calls.append(kwargs)
            self.apps = self

        def get_permissions(self, app_name):
            assert app_name == "test-app"
            return SimpleNamespace(
                access_control_list=[
                    SimpleNamespace(
                        user_name="manager@example.com",
                        all_permissions=[
                            SimpleNamespace(permission_level=SimpleNamespace(value="CAN_MANAGE")),
                        ],
                    )
                ]
            )

    import databricks.sdk

    monkeypatch.setattr(databricks.sdk, "WorkspaceClient", FakeWorkspaceClient)
    monkeypatch.setenv("DATABRICKS_HOST", "https://example.databricks.com")
    monkeypatch.setenv("DATABRICKS_CLIENT_ID", "app-client-id")
    monkeypatch.setenv("DATABRICKS_CLIENT_SECRET", "app-client-secret")

    provider = DatabricksAppsIdentityProvider(app_name="test-app", ttl_seconds=0)
    request = SimpleNamespace(headers={"x-forwarded-access-token": "delegated-user-token"})

    role = provider._fetch_provider_role(request, "manager@example.com")

    assert role == ProviderRole.CAN_MANAGE
    assert len(calls) == 1
    assert calls[0]["host"] == "https://example.databricks.com"
    assert "token" not in calls[0]
    assert "auth_type" not in calls[0]

    credentials_strategy = calls[0]["credentials_strategy"]
    assert credentials_strategy.auth_type() == "databricks_apps_delegated_oauth"
    assert credentials_strategy(None)() == {"Authorization": "Bearer delegated-user-token"}
