---
id: lakebase-setup
title: Lakebase Setup
slug: /lakebase-setup
---

# Lakebase Setup

This docs site is designed to be available even before Lakebase is configured.
If the deployed Databricks App opens here automatically, finish the setup below
and then restart or redeploy the app.

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
