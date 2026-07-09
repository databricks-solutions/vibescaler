"""Gunicorn configuration for production deployments.

Defines server hooks that run in the master process before workers fork.
"""

# Honor X-Forwarded-* from Databricks Apps so Uvicorn/Starlette see the public URL.
forwarded_allow_ips = "*"


def on_starting(server):
    """Run database migrations once in the master process before workers fork.

    This ensures pending Alembic migrations are applied once before workers fork
    when the database is available. Startup remains optimistic so the app can
    still serve the setup docs while Lakebase is being configured or waking up.
    """
    from server.db_bootstrap import SchemaAccessError, bootstrap_database
    from server.db_config import LakebaseConfig

    try:
        bootstrap_database(full=True)
    except SchemaAccessError as e:
        # Identity/ownership problem (e.g. the app's service principal rotated and a
        # previous identity still owns the schema). Migrations cannot run, but
        # crash-looping would hide the fix — start in setup mode instead so
        # /deployment/status and the logs show the operator exact remediation.
        server.log.error(
            "Database schema access problem — starting in SETUP mode; database-backed "
            "routes will fail until remediated.\n%s",
            e,
        )
    except Exception:
        # Optimistic startup is intentional ONLY while Lakebase is unconfigured: the
        # app must still serve /docs and the setup-status gate. But if Lakebase IS
        # configured, a bootstrap/migration failure means workers would fork onto a
        # broken or partially-migrated schema while the master reports a healthy
        # start (500s on DB-backed routes). Fail loudly in that case (D7).
        if LakebaseConfig.from_env() is not None:
            server.log.exception(
                "Database bootstrap failed on a configured Lakebase target; aborting "
                "startup so workers do not serve a partially-migrated schema."
            )
            raise
        server.log.exception(
            "Database bootstrap failed; continuing startup so /docs remains available. "
            "Database-backed routes may return errors until Lakebase is configured."
        )
