"""Tests for the asynchronous alignment job lifecycle.

POST /workshops/{id}/start-alignment must return a job ID immediately (before
the alignment work completes), and GET /workshops/{id}/alignment-job/{job_id}
must report the status transition running -> completed with the final result.
"""

import asyncio
import threading
from types import SimpleNamespace

import pytest


class _FakeDatabaseService:
    """Minimal stand-in for DatabaseService used by the start-alignment route."""

    def __init__(self, db):
        self._db = db

    def get_workshop(self, workshop_id):
        return SimpleNamespace(id=workshop_id, name="Test Workshop")

    def get_mlflow_config(self, workshop_id):
        return SimpleNamespace(experiment_id="exp-123")

    def resync_annotations_to_mlflow(self, workshop_id):
        return {"synced": 0, "total": 0, "judge_names": [], "errors": []}


@pytest.mark.spec("JUDGE_EVALUATION_SPEC")
@pytest.mark.req("Alignment jobs run asynchronously")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_start_alignment_returns_job_id_before_completion_then_polls_to_completed(
    async_client, override_get_db, monkeypatch
):
    """The endpoint responds while alignment is still running; polling observes
    the running -> completed transition and the final result payload."""
    import server.routers.workshops as wmod
    from server.services.alignment_service import AlignmentService

    release = threading.Event()

    def fake_run_alignment(self, **kwargs):
        # Generator mirroring AlignmentService.run_alignment's contract:
        # yields log strings, then a final result dict.
        yield "Alignment running..."
        # Block until the test releases us — guarantees the POST response and
        # the first poll both happen while the job is genuinely incomplete.
        assert release.wait(timeout=10), "test never released the alignment worker"
        yield {"success": True, "guideline_count": 2, "example_count": 5}

    monkeypatch.setattr(wmod, "DatabaseService", _FakeDatabaseService)
    monkeypatch.setattr(AlignmentService, "__init__", lambda self, db_service: None)
    monkeypatch.setattr(AlignmentService, "run_alignment", fake_run_alignment)

    try:
        resp = await async_client.post(
            "/workshops/ws-1/start-alignment",
            json={
                "judge_name": "quality_judge",
                "judge_prompt": "Rate {{ inputs }} vs {{ outputs }}",
                "evaluation_model_name": "databricks-claude-sonnet-4",
                "alignment_model_name": "databricks-claude-sonnet-4",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        job_id = body["job_id"]

        # The endpoint returned while the worker is still blocked: the job is
        # running and has no result yet.
        assert body["status"] == "running"
        status_resp = await async_client.get(f"/workshops/ws-1/alignment-job/{job_id}")
        assert status_resp.status_code == 200
        first_poll = status_resp.json()
        assert first_poll["status"] == "running"
        assert "result" not in first_poll

        # Unblock the background worker and poll until it completes.
        release.set()
        final = first_poll
        for _ in range(100):
            status_resp = await async_client.get(f"/workshops/ws-1/alignment-job/{job_id}")
            final = status_resp.json()
            if final["status"] not in ("pending", "running"):
                break
            await asyncio.sleep(0.05)

        assert final["status"] == "completed"
        assert final["result"]["success"] is True
        assert final["result"]["guideline_count"] == 2
        assert final["result"]["example_count"] == 5
        assert any("Alignment running" in log for log in final["logs"])
    finally:
        # Never leave the daemon thread blocked past the monkeypatch lifetime.
        release.set()
