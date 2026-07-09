# Error Message Reference

Hit an error? Press **⌘K** and paste it — the messages below are quoted verbatim from the application so search lands you here. Each entry says what the message actually means and what to do, ordered from cheapest fix to most drastic.

General triage, when in doubt: **refresh the page → suspect LLM rate limits → suspect the database connection → redeploy the app**. Frontend state accounts for most one-off weirdness, and Lakebase plus LLM rate limits account for most real outages. See [When things break](RUNNING_A_SESSION.md#when-things-break) for running this ladder mid-session.

## Access and session

### "Failed to resolve auth session" / `GET /api/auth/session` returns 500

The backend couldn't establish a session — almost always an environment problem, not a login problem: the database connection is unhealthy (Lakebase outage, or the SQLite file was replaced under a running server) or the app booted with incomplete config. Refresh once; if it persists, check database health and redeploy the app.

### "Workshop not found"

The workshop id in your URL doesn't exist in the database — typically a stale link after a workshop reset, a database restore, or a redeploy onto fresh state. Re-enter from the app's workshop list rather than a bookmarked deep link.

### "User not found in workshop"

You're authenticated but not a participant of *this* workshop. The facilitator needs to add you to the workshop's participant list — joining the app is not joining the workshop.

## Setup and trace ingestion

### "MLflow configuration not found"

The workshop has no MLflow experiment configured yet. Complete intake (experiment ID, trace limits) before starting ingestion — see the [Facilitator Guide](FACILITATOR_GUIDE.md).

### "No traces found in workshop"

Ingestion either hasn't run or returned zero traces. Check that the experiment ID is correct and actually contains traces matching the filter; if traces live outside MLflow, use the CSV upload fallback.

### "Failed to process CSV file: …" / "File must be a CSV file"

The upload fallback rejected the file. Confirm it's a real CSV (not Excel renamed), with the expected columns — see the trace-ingestion spec in the Specs tab for the format. The text after the colon is the parser's specific complaint.

## During review

### "Follow-up questions are disabled for this workshop"

Not an error — a configuration state. The facilitator disabled generated follow-ups for this workshop; enable them in workshop settings if discovery should include them.

### "Failed to generate discovery data: …"

The LLM call behind follow-up questions or findings distillation failed — **rate limits are the most common cause**, especially mid-session when every reviewer triggers generation at once. Pause the room for a couple of minutes instead of letting everyone retry, then resume. If it persists outside bursts, check the serving endpoint's status and quota.

### Stuck progress, unresponsive buttons, stale views

Usually frontend state, not the backend: **refresh the page**. Tell reviewers at session start that a refresh is always safe — no submitted work is lost.

## LLM and evaluation

### "Error calling serving endpoint: …"

The app couldn't reach the configured model endpoint. Rate limiting, endpoint scaled to zero, or a permissions change are the usual suspects. The text after the colon is the provider's response — a 429 means back off and pause the room; a 403 means the app's identity lost access to the endpoint.

### "MLflow evaluation failed: …" / "Failed to evaluate judge: …"

The evaluation or alignment call errored — most often the same endpoint problems as above, occasionally a trace whose content exceeds the model's context. Retry once; if a specific trace reproducibly fails, drop it from the evaluation set and continue the session.

## Data and persistence

### "Failed to reset workshop"

The reset operation couldn't complete — typically a database connectivity issue (Lakebase). Check database health; a redeploy with healthy database connectivity is the reliable recovery.

### Writes failing or data "disappearing"

Suspect the database connection before the application. If Lakebase is healthy and the symptom persists, redeploy — some states are only recoverable wholesale, and a redeploy costs minutes.

---

*This catalog is curated: messages are quoted from the source so search matches, and remedies come from real engagements. If you hit an error that isn't listed, that's a documentation bug — please file an issue with the verbatim message.*
