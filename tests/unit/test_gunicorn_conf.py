"""Tests for gunicorn_conf.py — the on_starting hook that runs migrations."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.spec("BUILD_AND_DEPLOY_SPEC")
@pytest.mark.req("Pending Alembic migrations are applied automatically before workers accept traffic")
class TestOnStartingHook:
    """SC: Pending Alembic migrations are applied automatically before workers accept traffic."""

    def test_on_starting_calls_bootstrap_database(self):
        """on_starting hook calls bootstrap_database(full=True)."""
        from gunicorn_conf import on_starting

        mock_server = MagicMock()

        with patch("server.db_bootstrap.bootstrap_database") as mock_bootstrap:
            on_starting(mock_server)
            mock_bootstrap.assert_called_once_with(full=True)

    def test_on_starting_survives_bootstrap_failure(self):
        """If bootstrap_database raises, startup continues (optimistic startup).

        The app must still come up to serve /docs and the setup-status gate
        while Lakebase is unconfigured or waking; the failure is logged.
        """
        from gunicorn_conf import on_starting

        mock_server = MagicMock()

        with (
            patch("server.db_bootstrap.bootstrap_database", side_effect=RuntimeError("migration failed")),
            patch("server.db_config.LakebaseConfig.from_env", return_value=None),
        ):
            on_starting(mock_server)

        mock_server.log.exception.assert_called_once()

    def test_on_starting_reraises_when_lakebase_configured(self):
        """If Lakebase IS configured and bootstrap fails, startup aborts (D7).

        A migration/connection failure on a configured target must not let workers
        fork onto a partially-migrated schema while the master reports a healthy start.
        """
        from gunicorn_conf import on_starting

        mock_server = MagicMock()

        with (
            patch("server.db_bootstrap.bootstrap_database", side_effect=RuntimeError("migration failed")),
            patch("server.db_config.LakebaseConfig.from_env", return_value=object()),
        ):
            with pytest.raises(RuntimeError, match="migration failed"):
                on_starting(mock_server)

        mock_server.log.exception.assert_called_once()
