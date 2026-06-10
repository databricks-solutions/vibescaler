"""Tests for discovery feedback service logic.

Exercises real DiscoveryService logic with in-memory SQLite instead of
mocking the entire service layer. Only the LLM call boundary is mocked.
"""

import asyncio
import time as stream_time_module
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server.database import Base, TraceDB, UserDB, WorkshopDB, WorkshopParticipantDB
from server.models import (
    DiscoveryCommentCreate,
    DiscoveryCommentVoteRequest,
    DiscoveryFeedbackCreate,
    FeedbackLabel,
)
from server.services.discovery_service import DiscoveryService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def discovery_service(test_db):
    return DiscoveryService(test_db)


@pytest.fixture
def workshop_with_traces(test_db):
    """Create a real workshop + trace records."""
    ws = WorkshopDB(
        id="ws-1",
        name="Test Workshop",
        facilitator_id="f-1",
        active_discovery_trace_ids=["t-1", "t-2"],
        discovery_started=True,
        current_phase="discovery",
        discovery_questions_model_name="demo",
    )
    t1 = TraceDB(id="t-1", workshop_id="ws-1", input="What is AI?", output="AI is...")
    t2 = TraceDB(id="t-2", workshop_id="ws-1", input="What is ML?", output="ML is...")
    test_db.add_all([ws, t1, t2])
    test_db.commit()
    return ws


# ============================================================================
# POST /workshops/{id}/discovery-feedback — submit_discovery_feedback
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Participants view traces and provide GOOD/BAD + comment")
@pytest.mark.unit
def test_submit_feedback_success(discovery_service, workshop_with_traces):
    """Submit GOOD/BAD feedback with comment on a trace — verify DB state."""
    data = DiscoveryFeedbackCreate(
        trace_id="t-1",
        user_id="u-1",
        feedback_label=FeedbackLabel.GOOD,
        comment="Nice answer",
    )
    result = discovery_service.submit_discovery_feedback("ws-1", data)

    assert result.feedback_label == "good"
    assert result.comment == "Nice answer"
    assert result.workshop_id == "ws-1"
    assert result.trace_id == "t-1"
    assert result.user_id == "u-1"

    # Verify in DB
    feedbacks = discovery_service.get_discovery_feedback("ws-1", user_id="u-1")
    assert len(feedbacks) == 1
    assert feedbacks[0].id == result.id


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Form validation prevents empty submissions")
@pytest.mark.unit
def test_submit_feedback_validation_rejects_empty_comment(discovery_service, workshop_with_traces):
    """Validation rejects empty comment — tests real logic in discovery_service.py."""
    data = DiscoveryFeedbackCreate(
        trace_id="t-1",
        user_id="u-1",
        feedback_label=FeedbackLabel.BAD,
        comment="",
    )
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.submit_discovery_feedback("ws-1", data)
    assert exc_info.value.status_code == 422
    assert "Comment is required" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Form validation prevents empty submissions")
@pytest.mark.unit
def test_submit_feedback_validation_rejects_whitespace_comment(discovery_service, workshop_with_traces):
    """Validation rejects whitespace-only comment."""
    data = DiscoveryFeedbackCreate(
        trace_id="t-1",
        user_id="u-1",
        feedback_label=FeedbackLabel.BAD,
        comment="   ",
    )
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.submit_discovery_feedback("ws-1", data)
    assert exc_info.value.status_code == 422


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Participants view traces and provide GOOD/BAD + comment")
@pytest.mark.unit
def test_submit_feedback_on_nonexistent_workshop(discovery_service):
    """Submit feedback on nonexistent workshop raises 404."""
    data = DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Should fail",
    )
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.submit_discovery_feedback("nonexistent-ws", data)
    assert exc_info.value.status_code == 404


# ============================================================================
# POST /workshops/{id}/generate-followup-question
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("All 3 questions required before moving to next trace")
@pytest.mark.unit
def test_generate_followup_rejects_question_4(discovery_service, workshop_with_traces):
    """Reject question_number > 3 — tests real boundary check."""
    # Submit feedback first so "no feedback" doesn't trigger
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good",
    ))

    with pytest.raises(HTTPException) as exc_info:
        discovery_service.generate_followup_question(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1", question_number=4,
        )
    assert exc_info.value.status_code == 400
    assert "1, 2, or 3" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("AI generates 3 follow-up questions per trace based on feedback")
@pytest.mark.unit
def test_generate_followup_requires_prior_feedback(discovery_service, workshop_with_traces):
    """Generating a follow-up without prior feedback raises 404."""
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.generate_followup_question(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1", question_number=1,
        )
    assert exc_info.value.status_code == 404
    assert "No feedback found" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Progressive disclosure (one question at a time)")
@pytest.mark.unit
def test_generate_followup_enforces_sequence(discovery_service, workshop_with_traces):
    """Asking for Q2 when Q1 not answered raises 400."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good",
    ))

    # Skip Q1, try to get Q2 directly
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.generate_followup_question(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1", question_number=2,
        )
    assert exc_info.value.status_code == 400
    assert "Expected question_number=1" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("AI generates 3 follow-up questions per trace based on feedback")
@pytest.mark.unit
def test_generate_followup_with_demo_model(discovery_service, workshop_with_traces):
    """With demo model, generate_followup returns a fallback question."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good answer",
    ))

    result = discovery_service.generate_followup_question(
        workshop_id="ws-1", trace_id="t-1", user_id="u-1", question_number=1,
    )

    assert "question" in result
    assert result["question_number"] == 1
    assert isinstance(result["question"], str)
    assert len(result["question"]) > 0
    # Demo model should produce a fallback
    assert result["is_fallback"] is True


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("AI generates 3 follow-up questions per trace based on feedback")
@pytest.mark.unit
def test_generate_followup_uses_sdk_auth_without_mlflow_config(
    discovery_service, workshop_with_traces, monkeypatch
):
    """Regression: follow-up generation should rely on SDK auth, not MLflow config."""
    discovery_service.submit_discovery_feedback(
        "ws-1",
        DiscoveryFeedbackCreate(
            trace_id="t-1",
            user_id="u-1",
            feedback_label=FeedbackLabel.GOOD,
            comment="Good answer",
        ),
    )

    monkeypatch.setattr(
        discovery_service,
        "_get_workshop_or_404",
        lambda _workshop_id: SimpleNamespace(discovery_questions_model_name="databricks-llm-endpoint"),
    )

    monkeypatch.setattr(
        discovery_service.db_service,
        "get_mlflow_config",
        lambda _workshop_id: None,
    )

    with patch("server.services.discovery_service.get_databricks_host", return_value="https://example.databricks.com"), patch(
        "server.services.discovery_service.resolve_databricks_token",
        return_value="dapi_test_token",
    ), patch(
        "server.services.followup_question_service.FollowUpQuestionService.generate",
        return_value=("Q?", False),
    ) as mock_generate:
        result = discovery_service.generate_followup_question(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1", question_number=1
        )

    _, kwargs = mock_generate.call_args
    assert kwargs["workspace_url"] == "https://example.databricks.com"
    assert kwargs["databricks_token"] == "dapi_test_token"
    assert kwargs["model_name"] == "databricks-llm-endpoint"
    assert result["question"] == "Q?"
    assert result["question_number"] == 1
    assert result["is_fallback"] is False


# ============================================================================
# POST /workshops/{id}/submit-followup-answer
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Questions build progressively on prior answers")
@pytest.mark.unit
def test_submit_followup_answer(discovery_service, workshop_with_traces):
    """Submit an answer to a follow-up — verify DB state."""
    # Setup: submit feedback first
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.BAD, comment="Not great",
    ))

    result = discovery_service.submit_followup_answer(
        workshop_id="ws-1",
        trace_id="t-1",
        user_id="u-1",
        question="What specifically was wrong?",
        answer="The tone was off.",
        milestone_references=["all", "m2"],
    )

    assert result["qna_count"] == 1
    assert result["complete"] is False

    # Verify in DB
    feedbacks = discovery_service.get_discovery_feedback("ws-1", user_id="u-1")
    assert len(feedbacks[0].followup_qna) == 1
    assert feedbacks[0].followup_qna[0]["question"] == "What specifically was wrong?"
    assert feedbacks[0].followup_qna[0]["answer"] == "The tone was off."
    assert feedbacks[0].followup_qna[0]["milestone_references"] == ["all", "m2"]


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Form validation prevents empty submissions")
@pytest.mark.unit
def test_submit_followup_answer_validation_rejects_empty_answer(discovery_service, workshop_with_traces):
    """Empty answer is rejected with 422."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good",
    ))

    with pytest.raises(HTTPException) as exc_info:
        discovery_service.submit_followup_answer(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1",
            question="Q1?", answer="",
        )
    assert exc_info.value.status_code == 422
    assert "Answer is required" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("All 3 questions required before moving to next trace")
@pytest.mark.unit
def test_submit_followup_answer_returns_complete_true_at_q3(discovery_service, workshop_with_traces):
    """After 3 Q&As, complete=True is returned."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good",
    ))

    for i in range(2):
        result = discovery_service.submit_followup_answer(
            workshop_id="ws-1", trace_id="t-1", user_id="u-1",
            question=f"Q{i+1}?", answer=f"A{i+1}",
        )
        assert result["complete"] is False

    # Third answer → complete
    result = discovery_service.submit_followup_answer(
        workshop_id="ws-1", trace_id="t-1", user_id="u-1",
        question="Q3?", answer="A3",
    )
    assert result["qna_count"] == 3
    assert result["complete"] is True


# ============================================================================
# GET /workshops/{id}/discovery-feedback — get_discovery_feedback
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Participants view traces and provide GOOD/BAD + comment")
@pytest.mark.unit
def test_get_discovery_feedback_list(discovery_service, workshop_with_traces):
    """List all discovery feedback for a workshop."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="Good 1",
    ))
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-2", user_id="u-1",
        feedback_label=FeedbackLabel.BAD, comment="Bad 2",
    ))

    result = discovery_service.get_discovery_feedback("ws-1")
    assert len(result) == 2
    comments = {fb.comment for fb in result}
    assert "Good 1" in comments
    assert "Bad 2" in comments


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Participants view traces and provide GOOD/BAD + comment")
@pytest.mark.unit
def test_get_discovery_feedback_filtered_by_user(discovery_service, workshop_with_traces):
    """List discovery feedback filtered by user_id returns only matching results."""
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-1",
        feedback_label=FeedbackLabel.GOOD, comment="User 1",
    ))
    discovery_service.submit_discovery_feedback("ws-1", DiscoveryFeedbackCreate(
        trace_id="t-1", user_id="u-2",
        feedback_label=FeedbackLabel.BAD, comment="User 2",
    ))

    result = discovery_service.get_discovery_feedback("ws-1", user_id="u-1")
    assert len(result) == 1
    assert result[0].user_id == "u-1"
    assert result[0].comment == "User 1"


# ============================================================================
# POST /workshops/{id}/begin-discovery (with randomize)
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Facilitator can start Discovery phase with configurable trace limit")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_begin_discovery_with_trace_limit(async_client, override_get_db, monkeypatch):
    """Begin discovery with trace_limit and randomize params.

    This test legitimately uses mocks because the begin-discovery route
    lives in workshops.py (not discovery.py) and only tests HTTP routing.
    """
    from unittest.mock import MagicMock

    from server.models import Workshop, WorkshopPhase, WorkshopStatus
    from datetime import datetime

    import server.routers.workshops as ws_mod

    mock_db_svc = MagicMock()
    mock_db_svc.get_workshop.return_value = Workshop(
        id="ws-1", name="Test", facilitator_id="f-1",
        status=WorkshopStatus.ACTIVE, current_phase=WorkshopPhase.DISCOVERY,
        discovery_started=True, active_discovery_trace_ids=["t-1", "t-2"],
        created_at=datetime.now(),
    )
    mock_traces = [MagicMock(id=f"t-{i}") for i in range(20)]
    mock_db_svc.get_traces.return_value = mock_traces
    mock_db_svc.update_workshop_phase.return_value = None
    mock_db_svc.update_phase_started.return_value = None
    mock_db_svc.update_discovery_randomize_setting.return_value = None
    mock_db_svc.update_active_discovery_traces.return_value = None

    monkeypatch.setattr(ws_mod, "DatabaseService", MagicMock(return_value=mock_db_svc))

    resp = await async_client.post("/workshops/ws-1/begin-discovery?trace_limit=5&randomize=true")
    assert resp.status_code == 200
    data = resp.json()
    assert data["traces_used"] == 5
    assert data["total_traces"] == 20
    mock_db_svc.update_discovery_randomize_setting.assert_called_once_with("ws-1", True)


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("When follow-up questions are disabled, participant flow is GOOD/BAD + comment only")
@pytest.mark.unit
def test_followup_generation_disabled_raises(discovery_service, workshop_with_traces, test_db):
    workshop = test_db.query(WorkshopDB).filter(WorkshopDB.id == "ws-1").first()
    workshop.discovery_followups_enabled = False
    test_db.commit()

    discovery_service.submit_discovery_feedback(
        "ws-1",
        DiscoveryFeedbackCreate(
            trace_id="t-1",
            user_id="u-1",
            feedback_label=FeedbackLabel.GOOD,
            comment="good",
        ),
    )
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.generate_followup_question(
            workshop_id="ws-1",
            trace_id="t-1",
            user_id="u-1",
            question_number=1,
        )
    assert exc_info.value.status_code == 400
    assert "disabled" in str(exc_info.value.detail).lower()


@pytest.mark.spec("DISCOVERY_SPEC")
# AUDIT (2026-06): retagged. The previous tag ("Facilitator `@assistant summarize this
# thread` returns a grounded summary as a thread reply") is an LLM capability criterion now
# under Roadmap — the shipped responder is a deterministic template stub. This test verifies
# the shipped mention-routing mechanics: a facilitator mention posts an assistant reply.
@pytest.mark.req("Facilitator `@assistant` mentions post an automated assistant reply in-thread (deterministic template stub)")
@pytest.mark.unit
def test_assistant_mention_creates_assistant_reply(discovery_service, workshop_with_traces):
    payload = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="f-1",
            body="@assistant summarize this thread",
        ),
    )
    assert payload["comment"].author_type == "human"
    assert payload["assistant_comment"].author_type == "assistant"
    assert "summary" in payload["assistant_comment"].body.lower()


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Users can upvote/downvote comments (single vote per user per comment with toggle behavior)")
@pytest.mark.unit
def test_comment_vote_toggle_behavior(discovery_service, workshop_with_traces):
    created = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="u-1",
            body="I think milestone 2 is strong.",
        ),
    )["comment"]

    upvoted = discovery_service.vote_discovery_comment(
        "ws-1",
        created.id,
        DiscoveryCommentVoteRequest(user_id="u-2", value=1),
    )
    assert upvoted.upvotes == 1
    assert upvoted.downvotes == 0

    toggled_off = discovery_service.vote_discovery_comment(
        "ws-1",
        created.id,
        DiscoveryCommentVoteRequest(user_id="u-2", value=1),
    )
    assert toggled_off.upvotes == 0
    assert toggled_off.downvotes == 0


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Facilitator can moderate social discussion threads by deleting comments")
@pytest.mark.unit
def test_facilitator_can_delete_comment_tree(discovery_service, workshop_with_traces):
    root = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="u-1",
            body="Root comment",
        ),
    )["comment"]
    child = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="u-2",
            body="Reply comment",
            parent_comment_id=root.id,
        ),
    )["comment"]
    discovery_service.vote_discovery_comment(
        "ws-1",
        child.id,
        DiscoveryCommentVoteRequest(user_id="u-3", value=1),
    )

    result = discovery_service.delete_discovery_comment("ws-1", root.id, user_id="f-1")
    assert result["deleted"] is True

    comments = discovery_service.list_discovery_comments("ws-1", trace_id="t-1", user_id="f-1")
    assert comments == []


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Only facilitator can delete social thread comments")
@pytest.mark.unit
def test_non_facilitator_cannot_delete_comment(discovery_service, workshop_with_traces):
    root = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="u-1",
            body="Cannot delete me",
        ),
    )["comment"]

    with pytest.raises(HTTPException) as exc_info:
        discovery_service.delete_discovery_comment("ws-1", root.id, user_id="u-2")
    assert exc_info.value.status_code == 403


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Facilitator can invoke `@agent` to run a bounded tool loop and receive a persisted agent reply in-thread with clear success/failure status")
@pytest.mark.unit
def test_agent_run_uses_trace_context_tools(discovery_service, workshop_with_traces, test_db):
    trace = test_db.query(TraceDB).filter(TraceDB.id == "t-1").first()
    trace.context = {
        "status": "OK",
        "execution_time_ms": 120,
        "spans": [
            {
                "name": "root",
                "parent_span_id": None,
                "span_type": "CHAIN",
                "status": "OK",
                "inputs": {"question": "what could have been better?"},
                "outputs": {"answer": "baseline answer"},
            },
            {
                "name": "tool_lookup",
                "parent_span_id": "root",
                "span_type": "TOOL",
                "status": "OK",
                "inputs": {"query": "retrieval"},
                "outputs": {"result": "documents"},
            },
        ],
        "tags": {},
    }
    test_db.commit()

    root_comment = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="f-1",
            body="what could have been better in this interaction?",
        ),
    )["comment"]

    run = discovery_service.db_service.create_discovery_agent_run(
        workshop_id="ws-1",
        trace_id="t-1",
        trigger_comment_id=root_comment.id,
        created_by="f-1",
    )
    discovery_service._execute_agent_run(run.id)

    completed = discovery_service.db_service.get_discovery_agent_run(run.id)
    assert completed is not None
    assert completed.status == "completed"
    assert "Trace overview" in (completed.final_output or "")


# ============================================================================
# Step 4: Social Threads & Mentions — shipped mechanics
# (Added by 2026-06 honesty audit: these mechanics ship in v1.10 but were
# untested. LLM-backed @assistant/@agent capabilities are spec Roadmap.)
# ============================================================================


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Facilitator can switch Discovery workspace between `analysis` mode and `social` mode")
@pytest.mark.unit
def test_discovery_mode_toggle_between_analysis_and_social(discovery_service, workshop_with_traces):
    result = discovery_service.update_discovery_settings("ws-1", discovery_mode="social")
    assert result["discovery_mode"] == "social"

    result = discovery_service.update_discovery_settings("ws-1", discovery_mode="analysis")
    assert result["discovery_mode"] == "analysis"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Facilitator can switch Discovery workspace between `analysis` mode and `social` mode")
@pytest.mark.unit
def test_discovery_mode_rejects_invalid_value(discovery_service, workshop_with_traces):
    with pytest.raises(HTTPException) as exc_info:
        discovery_service.update_discovery_settings("ws-1", discovery_mode="freeform")
    assert exc_info.value.status_code == 400
    assert "analysis" in exc_info.value.detail and "social" in exc_info.value.detail


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("In social mode, users can create trace-level comments")
@pytest.mark.unit
def test_create_trace_level_comment(discovery_service, workshop_with_traces):
    payload = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="Trace-level observation"),
    )
    created = payload["comment"]
    assert created.trace_id == "t-1"
    assert created.milestone_ref is None
    assert created.parent_comment_id is None

    listed = discovery_service.list_discovery_comments("ws-1", trace_id="t-1")
    assert [c.body for c in listed] == ["Trace-level observation"]


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("In social mode, users can create milestone-level comments")
@pytest.mark.unit
def test_create_milestone_level_comment(discovery_service, workshop_with_traces):
    discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="Milestone m2 concern", milestone_ref="m2"),
    )
    discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-2", body="Plain trace comment"),
    )

    milestone_comments = discovery_service.list_discovery_comments("ws-1", trace_id="t-1", milestone_ref="m2")
    assert [c.body for c in milestone_comments] == ["Milestone m2 concern"]
    assert milestone_comments[0].milestone_ref == "m2"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Users can reply to comments in-thread")
@pytest.mark.unit
def test_reply_to_comment_in_thread(discovery_service, workshop_with_traces):
    root = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="Root comment"),
    )["comment"]

    reply = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(
            trace_id="t-1",
            user_id="u-2",
            body="In-thread reply",
            parent_comment_id=root.id,
        ),
    )["comment"]

    assert reply.parent_comment_id == root.id
    listed = discovery_service.list_discovery_comments("ws-1", trace_id="t-1")
    by_body = {c.body: c for c in listed}
    assert by_body["In-thread reply"].parent_comment_id == root.id


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Non-facilitator mentions do not trigger assistant/agent execution (treated as plain text mentions)")
@pytest.mark.unit
def test_non_facilitator_mentions_treated_as_plain_text(discovery_service, workshop_with_traces):
    # u-1 is not the facilitator (facilitator_id is "f-1")
    assistant_payload = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="@assistant summarize this thread"),
    )
    assert "assistant_comment" not in assistant_payload
    assert "agent_run" not in assistant_payload
    assert assistant_payload["comment"].author_type == "human"

    agent_payload = discovery_service.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="@agent analyze this interaction"),
    )
    assert "agent_run" not in agent_payload
    assert "assistant_comment" not in agent_payload

    # Both mentions persist as ordinary human comments in the thread
    listed = discovery_service.list_discovery_comments("ws-1", trace_id="t-1")
    assert all(c.author_type == "human" for c in listed)
    assert len(listed) == 2


# ----------------------------------------------------------------------------
# SSE streaming mechanics (router-level, real generators)
# ----------------------------------------------------------------------------


@pytest.fixture
def shared_thread_db():
    """In-memory SQLite shared across threads (SSE generators run in a threadpool)."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)
    session = TestingSession()
    yield session, TestingSession
    session.close()


def _seed_social_workshop(session):
    ws = WorkshopDB(
        id="ws-1",
        name="Test Workshop",
        facilitator_id="f-1",
        active_discovery_trace_ids=["t-1"],
        discovery_started=True,
        current_phase="discovery",
        discovery_questions_model_name="demo",
    )
    t1 = TraceDB(id="t-1", workshop_id="ws-1", input="What is AI?", output="AI is...")
    session.add_all([ws, t1])
    session.commit()
    return ws


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("Thread updates appear live in the workspace while participants collaborate")
@pytest.mark.unit
def test_comments_stream_pushes_live_snapshots(shared_thread_db, monkeypatch):
    """The SSE comments stream emits a snapshot for current comments and pushes a
    fresh snapshot when a new comment arrives — the mechanism behind live thread
    updates in the workspace (DiscoveryTraceCard subscribes via EventSource)."""
    session, TestingSession = shared_thread_db
    _seed_social_workshop(session)

    svc = DiscoveryService(session)
    svc.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="u-1", body="First comment"),
    )

    monkeypatch.setattr("server.routers.discovery.SessionLocal", TestingSession)
    # Neutralize the inter-poll sleep so the test is fast
    monkeypatch.setattr(stream_time_module, "sleep", lambda _s: None)

    from server.routers.discovery import stream_discovery_comments

    async def run_stream():
        response = await stream_discovery_comments("ws-1", trace_id="t-1")
        snapshots = []
        async for chunk in response.body_iterator:
            text = chunk.decode() if isinstance(chunk, bytes) else chunk
            if "comments_snapshot" in text:
                snapshots.append(text)
            if len(snapshots) == 1 and "Second comment" not in "".join(snapshots):
                # First snapshot received — post a new comment and expect a push
                svc.create_discovery_comment(
                    "ws-1",
                    DiscoveryCommentCreate(trace_id="t-1", user_id="u-2", body="Second comment"),
                )
            if any("Second comment" in s for s in snapshots):
                break
        await response.body_iterator.aclose()
        return snapshots

    snapshots = asyncio.run(asyncio.wait_for(run_stream(), timeout=15))

    assert "First comment" in snapshots[0]
    assert any("Second comment" in s for s in snapshots)


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.req("`@agent` run lifecycle is visible (`running`, `completed`, `failed`, `timeout`) with final persisted reply")
@pytest.mark.unit
def test_agent_run_stream_reports_lifecycle_with_final_reply(shared_thread_db, monkeypatch):
    """An @agent run progresses running -> completed, the SSE stream exposes the
    lifecycle (run_started/run_completed events), and the final output is persisted
    as an in-thread agent reply."""
    session, TestingSession = shared_thread_db
    _seed_social_workshop(session)

    svc = DiscoveryService(session)
    trigger = svc.create_discovery_comment(
        "ws-1",
        DiscoveryCommentCreate(trace_id="t-1", user_id="f-1", body="what could be better here?"),
    )["comment"]

    run = svc.db_service.create_discovery_agent_run(
        workshop_id="ws-1",
        trace_id="t-1",
        trigger_comment_id=trigger.id,
        created_by="f-1",
    )
    assert run.status == "running"

    # Neutralize the token-streaming sleep, then execute the deterministic run
    monkeypatch.setattr(stream_time_module, "sleep", lambda _s: None)
    svc._execute_agent_run(run.id)

    completed = svc.db_service.get_discovery_agent_run(run.id)
    assert completed.status == "completed"
    assert completed.final_output

    # The final output is persisted as an agent reply in the thread
    listed = svc.list_discovery_comments("ws-1", trace_id="t-1")
    agent_replies = [c for c in listed if c.author_type == "agent"]
    assert len(agent_replies) == 1
    assert agent_replies[0].parent_comment_id == trigger.id
    assert agent_replies[0].body == completed.final_output

    # The SSE stream reports the lifecycle: run_started then run_completed
    monkeypatch.setattr("server.routers.discovery.SessionLocal", TestingSession)
    from server.routers.discovery import stream_discovery_agent_run

    async def run_stream():
        response = await stream_discovery_agent_run("ws-1", run.id)
        events = []
        async for chunk in response.body_iterator:
            text = chunk.decode() if isinstance(chunk, bytes) else chunk
            events.append(text)
            if "run_completed" in text or "run_failed" in text:
                break
        await response.body_iterator.aclose()
        return events

    events = asyncio.run(asyncio.wait_for(run_stream(), timeout=15))
    joined = "".join(events)
    assert "event: run_started" in joined
    assert "event: run_completed" in joined
    assert '"status": "completed"' in joined
