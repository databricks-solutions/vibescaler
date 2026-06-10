"""Registry portability guard for BUILD_AND_DEPLOY_SPEC.

Lockfiles must resolve against public registries so anyone outside the
Databricks network can install dependencies. uv.lock has repeatedly been
re-locked against the internal PyPI proxy (pypi-proxy.dev.databricks.com):
running plain ``uv run`` (without ``--frozen``/``--no-sync``) while
UV_DEFAULT_INDEX points at the proxy silently rewrites every package source
in the lockfile. This guard pins the public-registry invariant.
"""

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Known internal proxy hosts seen in past regressions:
#   pypi-proxy.dev.databricks.com, pypi-proxy.cloud.databricks.com
INTERNAL_HOST_MARKERS = ("pypi-proxy.", ".databricks.com")
PUBLIC_PYPI_REGISTRY = "https://pypi.org/simple"


@pytest.mark.spec("BUILD_AND_DEPLOY_SPEC")
@pytest.mark.req("Lockfiles resolve against public registries (no internal proxy URLs)")
class TestRegistryPortability:
    """SC: Lockfiles resolve against public registries (no internal proxy URLs)."""

    def test_uv_lock_has_no_internal_proxy_references(self):
        """uv.lock must contain zero references to internal Databricks proxy hosts."""
        content = (PROJECT_ROOT / "uv.lock").read_text()
        offending = [
            lineno
            for lineno, line in enumerate(content.splitlines(), start=1)
            if any(marker in line for marker in INTERNAL_HOST_MARKERS)
        ]
        assert offending == [], (
            f"uv.lock references internal Databricks proxy hosts on "
            f"{len(offending)} lines (first: {offending[:5]}). "
            "Restore the public-registry lock (git checkout -- uv.lock) and "
            "never run plain `uv run` with UV_DEFAULT_INDEX set — use "
            "`uv run --frozen` or `uv run --no-sync`."
        )

    def test_uv_lock_resolves_against_public_pypi(self):
        """Every package source registry in uv.lock must be public PyPI."""
        content = (PROJECT_ROOT / "uv.lock").read_text()
        registries = set(re.findall(r'registry = "([^"]+)"', content))
        assert registries, "uv.lock must declare package source registries"
        assert registries == {PUBLIC_PYPI_REGISTRY}, (
            f"uv.lock resolves against non-public registries: "
            f"{sorted(registries - {PUBLIC_PYPI_REGISTRY})}. "
            f"All package sources must use {PUBLIC_PYPI_REGISTRY}."
        )

    def test_npm_lockfiles_have_no_internal_proxy_references(self):
        """Any committed package-lock.json must not pin internal proxy URLs."""
        candidates = [
            PROJECT_ROOT / "package-lock.json",
            PROJECT_ROOT / "client" / "package-lock.json",
            PROJECT_ROOT / "docs" / "package-lock.json",
        ]
        offenders = {}
        for lock in candidates:
            if not lock.is_file():
                continue
            content = lock.read_text()
            if INTERNAL_PROXY_SUFFIX in content:
                offenders[str(lock.relative_to(PROJECT_ROOT))] = content.count(
                    INTERNAL_PROXY_SUFFIX
                )
        assert offenders == {}, (
            f"npm lockfiles reference internal Databricks proxy hosts: {offenders}. "
            "Regenerate them against the public npm registry."
        )
