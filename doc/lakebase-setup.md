---
id: lakebase-setup
title: Lakebase Setup
slug: /lakebase-setup
---

# Lakebase Setup

:::important You were sent here because Lakebase is not configured yet

This documentation site is **always available** at `/docs` — even when Lakebase is not set up — so you can complete configuration from the deployed app.

**If the Databricks App opened this page automatically:**

1. Complete every step in the sections below to attach Lakebase to the app.
2. **Restart or redeploy the app** when you are done (required — the app only picks up the database connection after a new deploy/restart).
3. Open the app root URL again. You should see the workshop UI instead of this setup guide.

Until Lakebase is configured and the app has been restarted, the workshop experience at `/` will keep redirecting here.

:::

## Why Lakebase Is Required

Databricks Apps run in ephemeral containers. Lakebase provides the persistent
PostgreSQL database used to store workshops, participants, traces, rubrics, and
annotations across app restarts and deploys.

## Create a Lakebase Project

1. Open the apps switcher in your Databricks workspace.
2. Select **Lakebase Postgres**.
3. Choose **Autoscaling**.
4. Click **New project**.
5. Create a project for the workshop.
6. Wait for the `production` branch to become active.

Lakebase creates a `databricks_postgres` database on the production branch.

## Attach Lakebase to the App

Open the Databricks App configuration and add a resource with these values:

| Field | Value |
| --- | --- |
| Resource type | Database |
| Project | Your Lakebase project |
| Branch | `production` |
| Database | `databricks_postgres` |
| Permission | Can connect and create |
| Resource key | `postgres` |

After the resource is attached, Databricks injects the Postgres connection
variables used by the app: `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPORT`,
`PGAPPNAME`, and `PGSSLMODE`.

## Restart the App

Restart or redeploy the Databricks App after attaching the database resource.
On startup, the app will run migrations and create the schema/tables needed for
the workshop.

## Expected Behavior

- Before Lakebase is configured, the app should show this setup guide.
- After Lakebase is configured, the app should open the workshop experience.
- If Lakebase is temporarily unavailable, the docs site should still be served.
