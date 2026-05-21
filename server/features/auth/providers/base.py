from __future__ import annotations

from typing import Protocol

from fastapi import Request

from server.features.auth.schemas import ProviderIdentity, ProviderRole


class IdentityProvider(Protocol):
    provider_name: str

    def resolve_identity(self, request: Request) -> ProviderIdentity:
        """Resolve the authenticated provider identity for this request."""

    def resolve_provider_role(self, request: Request, identity: ProviderIdentity) -> ProviderRole:
        """Resolve provider-native app access for this identity."""

