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
    from server.db_bootstrap import bootstrap_database

    try:
        bootstrap_database(full=True)
    except Exception:
        server.log.exception(
            "Database bootstrap failed; continuing startup so /docs remains available. "
            "Database-backed routes may return errors until Lakebase is configured."
        )
