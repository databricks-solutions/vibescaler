from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from server.models import User, UserPermissions


class ProviderRole(StrEnum):
    CAN_MANAGE = "CAN_MANAGE"
    CAN_USE = "CAN_USE"


class ProviderIdentity(BaseModel):
    provider: str
    email: str
    display_name: str | None = None


class AuthSession(BaseModel):
    user: User
    permissions: UserPermissions
    provider: str
    provider_role: ProviderRole

