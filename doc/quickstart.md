---
title: Quickstart
---

# Quickstart

Get from zero to a calibrated LLM judge: deploy VibeScaler as a Databricks App, then run one session that turns your reviewers' judgement into an aligned judge. Budget about 15 minutes to deploy and a 60–90 minute live session.

## Before you begin

- A **Databricks workspace** with **Databricks Apps** enabled.
- An **MLflow experiment** with **~10+ traces** to review. No traces yet? You can upload a CSV instead during intake.
- **One or more model serving endpoints** for the evaluation and alignment LLMs (one endpoint is fine; you can also use a separate one for each).
- **At least 2 reviewers** (SMEs) — judge alignment calibrates against independent human judgements, so it needs more than one.

## 1. Create a Lakebase database

Databricks Apps run in ephemeral containers, so VibeScaler stores its workshops, traces, rubrics, and annotations in a Lakebase (Postgres) database. From the workspace apps switcher: **Lakebase Postgres → Autoscaling → New project** and give it a name (e.g. `workshop`). Wait for the `production` branch to activate — it creates a `databricks_postgres` database automatically. Full detail: [Lakebase Setup](./lakebase-setup.md).

## 2. Create the app and attach resources

**Compute → Apps → Create app → Create a custom app**, name it, and create. Then, under **Configure**, add three **app resources**:

| Resource | Settings | Permission |
|----------|----------|------------|
| **Database** | your Lakebase project · branch `production` · db `databricks_postgres` · key `postgres` | Can connect and create |
| **Model serving endpoint** | your evaluation / alignment endpoint(s) | Can query |
| **MLflow experiment** | the experiment holding your traces | **Can edit** |

The experiment needs **Can edit** because annotations sync back to it as MLflow feedback. Attaching it as a resource lets the app use its own service principal — **no personal access token required**.

## 3. Deploy

Deploy straight from Git; Databricks runs `npm install` and `npm run build` for you, so there's nothing to pre-build.

1. On the app page, set the Git repository to `https://github.com/databrickslabs/vibescaler` (provider: **GitHub**) and **Save**.
2. **Deploy → From Git**, enter a Git reference — `main`, or a published release tag to pin a version — choose branch or tag, and **Deploy**.
3. When the app shows **Running**, open it.

> Air-gapped or workspace-only? Download the repo as a zip (GitHub's **Code** button, or a published release) and deploy from a workspace import instead — see the [Facilitator Guide](./FACILITATOR_GUIDE.md).

On first open the app runs migrations and creates its schema. If Lakebase isn't attached yet, the app shows the setup guide instead of the workshop — finish step 1, then restart or redeploy.

## 4. Add your reviewers

**Facilitator Dashboard → Workshop Users.** Add each person with their email, name, and role:

- **SME** — gives discovery feedback **and** annotates during the annotation phase (you need at least 2).
- **Participant** — discovery feedback only.

## 5. Bring in traces

**Intake → MLflow**: enter the experiment ID — find it in the experiment's URL in your Databricks workspace — and a **Max Traces** count to import (start with ~10–20 to keep reviewer attention focused). Confirm the intake status shows the expected trace count before moving on. No MLflow traces? Choose **CSV upload** instead.

## 6. Run the session and align a judge

From the **Facilitator Dashboard**, start each phase and advance the workshop as reviewers finish:

1. **Discovery** — reviewers read traces and surface what "good" looks like; the app distills their observations into findings.
2. **Rubric** — those findings become rubric criteria.
3. **Annotation** — reviewers score traces against the rubric, independently.
4. **Results** — review inter-rater agreement to see where reviewers diverge; it tells you whether the rubric is calibrated before you align.
5. **Judge alignment** — one click aligns a judge to the labels they just produced, in seconds.

Run alignment **live, in the room** — watching a judge learn the group's standard is the payoff moment. For pacing and coaching, see [Running a Facilitated Session](./RUNNING_A_SESSION.md); for the full per-phase mechanics, the [Facilitator Guide](./FACILITATOR_GUIDE.md).

## What you'll have

A calibrated LLM judge tuned to your use case, the labeled data generated along the way, and a repeatable process you can scale to your other use cases. The judge doesn't stop there — aligned to your rubric, it keeps measuring production traffic as a **living rubric**. See the [Overview](/) for where it goes next.
