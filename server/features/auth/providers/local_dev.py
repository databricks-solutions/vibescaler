from __future__ import annotations

import os

from fastapi import Request

from server.features.auth.schemas import ProviderIdentity, ProviderRole


class LocalDevIdentityProvider:
    provider_name = "local_dev"

    def resolve_identity(self, request: Request) -> ProviderIdentity:
        email = (
            request.cookies.get("e2e_current_user_email")
            or os.getenv("LOCAL_DEV_USER_EMAIL")
            or "local.facilitator@example.com"
        ).strip().lower()
        display_name = request.cookies.get("e2e_current_user_name") or os.getenv("LOCAL_DEV_USER_NAME", "Local Facilitator")
        return ProviderIdentity(provider=self.provider_name, email=email, display_name=display_name)

    def resolve_provider_role(self, request: Request, identity: ProviderIdentity) -> ProviderRole:
        configured = (
            request.cookies.get("e2e_current_provider_role")
            or os.getenv("LOCAL_DEV_PROVIDER_ROLE")
            or ProviderRole.CAN_MANAGE.value
        ).strip().upper()
        if configured == ProviderRole.CAN_USE.value:
            return ProviderRole.CAN_USE
        return ProviderRole.CAN_MANAGE

