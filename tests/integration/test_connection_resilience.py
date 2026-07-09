"""Integration tests: Connection resilience — pool reset, retry, OAuth refresh.

These tests verify the get_db() retry logic and _reset_connection_pool() behavior
by mocking engine/session internals to simulate connection failures.
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.exc import TimeoutError as SATimeoutError

pytestmark = [
    pytest.mark.integration,
    pytest.mark.spec("TESTING_SPEC"),
]


@pytest.mark.req(
    "Connection resilience tested: connection errors classified as transient vs not, "
    "`_reset_connection_pool()` disposes the engine, `get_db()` retries with backoff "
    "and gives up after 3 attempts"
)
class TestIsConnectionError:
    """Verify _is_connection_error classifies errors correctly."""

    def test_disconnection_error_is_connection_error(self):
        from server.database import _is_connection_error

        exc = DisconnectionError("connection was closed")
        assert _is_connection_error(exc) is True

    def test_operational_error_is_connection_error(self):
        from server.database import _is_connection_error

        exc = OperationalError("test", {}, Exception("operational"))
        assert _is_connection_error(exc) is True

    def test_generic_exception_with_connection_message(self):
        from server.database import _is_connection_error

        exc = Exception("connection is closed unexpectedly")
        assert _is_connection_error(exc) is True

    def test_generic_exception_without_connection_message(self):
        from server.database import _is_connection_error

        exc = Exception("invalid syntax near SELECT")
        assert _is_connection_error(exc) is False

    @pytest.mark.parametrize("message", [
        "server closed the connection unexpectedly",
        "terminating connection",
        "connection reset",
        "ssl connection has been closed unexpectedly",
        "could not connect to server",
        "connection refused",
        "invalid authorization",
        "database is locked",
    ])
    def test_known_pg_error_messages(self, message):
        from server.database import _is_connection_error

        exc = Exception(message)
        assert _is_connection_error(exc) is True

    def test_pool_exhaustion_timeout_is_not_connection_error(self):
        """SQLAlchemy QueuePool TimeoutError must NOT be classified as a
        transient connection error.  Treating saturation as such triggers
        engine.dispose() during the retry path, which drops in-flight
        connections held by other concurrent requests and amplifies the
        outage.  See gh#163.
        """
        from server.database import _is_connection_error

        exc = SATimeoutError(
            "QueuePool limit of size 5 overflow 5 reached, "
            "connection timed out, timeout 30.00",
            None,
            None,
        )
        assert _is_connection_error(exc) is False


@pytest.mark.req(
    "Connection resilience tested: connection errors classified as transient vs not, "
    "`_reset_connection_pool()` disposes the engine, `get_db()` retries with backoff "
    "and gives up after 3 attempts"
)
class TestResetConnectionPool:
    """Verify _reset_connection_pool disposes the engine.

    Note: no explicit OAuth refresh happens here — Postgres credentials are
    re-injected per new connection via the do_connect listener.
    """

    def test_reset_disposes_engine(self):
        from server.database import _reset_connection_pool, engine

        with patch.object(engine, "dispose") as mock_dispose:
            _reset_connection_pool()
            mock_dispose.assert_called_once()

    def test_reset_disposes_engine_for_postgres(self):
        """When backend is PostgreSQL, engine.dispose() is called (credentials are
        injected per-connection via do_connect, so no explicit refresh needed)."""
        import server.database as db_mod

        with (
            patch.object(db_mod, "DATABASE_BACKEND", db_mod.DatabaseBackend.POSTGRESQL),
            patch.object(db_mod.engine, "dispose") as mock_dispose,
        ):
            db_mod._reset_connection_pool()
            mock_dispose.assert_called_once()


@pytest.mark.req(
    "Connection resilience tested: connection errors classified as transient vs not, "
    "`_reset_connection_pool()` disposes the engine, `get_db()` retries with backoff "
    "and gives up after 3 attempts"
)
class TestGetDbRetry:
    """Verify get_db retries on transient connection errors."""

    def test_retries_on_connection_error_then_succeeds(self):
        """get_db retries up to 3 times; succeeds on second attempt."""
        import server.database as db_mod

        call_count = 0
        real_session_local = db_mod.SessionLocal

        def _flaky_session():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise DisconnectionError("connection is closed")
            return MagicMock()

        with (
            patch.object(db_mod, "SessionLocal", side_effect=_flaky_session),
            patch.object(db_mod, "_reset_connection_pool"),
            patch.object(db_mod, "DATABASE_BACKEND", db_mod.DatabaseBackend.SQLITE),
            patch("time.sleep"),
        ):
            gen = db_mod.get_db()
            session = next(gen)
            assert session is not None
            assert call_count == 2
            # Clean up generator
            try:
                next(gen)
            except StopIteration:
                pass

    def test_gives_up_after_max_attempts(self):
        """get_db raises after 3 failed attempts."""
        import server.database as db_mod

        def _always_fail():
            raise DisconnectionError("connection is closed")

        with (
            patch.object(db_mod, "SessionLocal", side_effect=_always_fail),
            patch.object(db_mod, "_reset_connection_pool"),
            patch.object(db_mod, "DATABASE_BACKEND", db_mod.DatabaseBackend.SQLITE),
            patch("time.sleep"),
        ):
            gen = db_mod.get_db()
            with pytest.raises(DisconnectionError):
                next(gen)

    def test_non_connection_error_raises_immediately(self):
        """Non-connection errors are not retried."""
        import server.database as db_mod

        call_count = 0

        def _bad_query():
            nonlocal call_count
            call_count += 1
            raise ValueError("invalid syntax")

        with (
            patch.object(db_mod, "SessionLocal", side_effect=_bad_query),
            patch.object(db_mod, "DATABASE_BACKEND", db_mod.DatabaseBackend.SQLITE),
        ):
            gen = db_mod.get_db()
            with pytest.raises(ValueError):
                next(gen)
            assert call_count == 1  # No retry


class TestStreamingEndpointsDoNotHoldSessions:
    """Streaming/SSE endpoints must not bind a DB Session via FastAPI
    dependency injection — doing so holds one pool connection per
    subscriber for the entire stream lifetime and saturates the pool.
    See gh#163 (production cascade traced to /discovery-comments/stream).

    Intentionally not @req-linked: pool-saturation regression guards with no
    matching success criterion. (A class-level AUTHENTICATION_SPEC marker was
    removed here — module-level pytestmark overrode it in the marker collector,
    and AUTHENTICATION_SPEC has no matching criterion.)
    """

    def _signature_params(self, fn):
        import inspect

        return inspect.signature(fn).parameters

    def test_stream_discovery_comments_has_no_db_dependency(self):
        from server.routers.discovery import stream_discovery_comments

        params = self._signature_params(stream_discovery_comments)
        assert "db" not in params, (
            "Streaming endpoint must not bind a Session via Depends(get_db) — "
            "acquire SessionLocal() per poll iteration instead. See gh#163."
        )

    def test_stream_discovery_agent_run_has_no_db_dependency(self):
        from server.routers.discovery import stream_discovery_agent_run

        params = self._signature_params(stream_discovery_agent_run)
        assert "db" not in params, (
            "Streaming endpoint must not bind a Session via Depends(get_db) — "
            "acquire SessionLocal() per poll iteration instead. See gh#163."
        )
