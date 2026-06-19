"""Integration test for the item-2 fix: post-alignment re-evaluate must join human ratings.

Drives the REAL `AlignmentService.run_evaluation_with_answer_sheet` generator end-to-end with
MLflow mocked only at the boundaries (`_search_tagged_traces`, `mlflow.genai.evaluate`,
`get_scorer`, `set_experiment`). This exercises the full True-branch wiring:
prepare_alignment_data -> intersect with eval-tagged traces -> evaluate -> join human ratings ->
compute metrics. It proves the fix produces a real Cohen's kappa, and that the old
require_human_ratings=False path is the kappa=0 bug.

@spec JUDGE_EVALUATION_SPEC
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from server.services.alignment_service import AlignmentService


class _Trace:
    def __init__(self, id, mlflow_trace_id):
        self.id = id
        self.mlflow_trace_id = mlflow_trace_id
        self.summary = None
        self.input = "question"
        self.output = "answer"


class _Ann:
    def __init__(self, trace_id, rating):
        self.trace_id = trace_id  # workshop trace id
        self.rating = rating
        self.comment = None


def _fake_db():
    db = MagicMock()
    traces = [_Trace("ws-1", "mlf-1"), _Trace("ws-2", "mlf-2"), _Trace("ws-3", "mlf-3"), _Trace("ws-4", "mlf-4")]
    # Human (SME) ratings, binary: ws-1=1, ws-2=0, ws-3=1, ws-4=0
    anns = [_Ann("ws-1", 1), _Ann("ws-2", 0), _Ann("ws-3", 1), _Ann("ws-4", 0)]
    db.get_traces_for_alignment.return_value = traces
    db.get_annotations.return_value = anns
    db.get_traces.return_value = traces
    db.get_workshop.return_value = MagicMock(
        span_attribute_filter=None, input_jsonpath=None, output_jsonpath=None
    )
    return db


def _drive(require_human_ratings):
    svc = AlignmentService(_fake_db())

    # search df already carries inputs/outputs so the trace-fetch prep block is skipped.
    search_df = pd.DataFrame(
        {
            "trace_id": ["mlf-1", "mlf-2", "mlf-3", "mlf-4"],
            "inputs": ["i1", "i2", "i3", "i4"],
            "outputs": ["o1", "o2", "o3", "o4"],
        }
    )
    # The aligned judge's predictions (binary floats). 3 of 4 agree with the humans above.
    result_df = pd.DataFrame(
        {
            "trace_id": ["mlf-1", "mlf-2", "mlf-3", "mlf-4"],
            "judgeX/value": [1.0, 0.0, 1.0, 1.0],
            "judgeX/rationale": ["", "", "", ""],
        }
    )
    svc._search_tagged_traces = MagicMock(return_value=search_df)
    mlflow_config = MagicMock(experiment_id="exp-1")

    final = None
    with patch("mlflow.set_experiment"), patch(
        "mlflow.genai.scorers.get_scorer", return_value=MagicMock()
    ), patch("mlflow.genai.evaluate", return_value=MagicMock(result_df=result_df)):
        for msg in svc.run_evaluation_with_answer_sheet(
            workshop_id="w1",
            judge_name="judgeX",
            judge_prompt="prompt",
            evaluation_model_name="databricks-claude-opus-4-5",
            mlflow_config=mlflow_config,
            judge_type="binary",
            require_human_ratings=require_human_ratings,
            tag_type="eval",
            use_registered_judge=True,
        ):
            if isinstance(msg, dict):
                final = msg
    return final


@pytest.mark.spec("JUDGE_EVALUATION_SPEC")
@pytest.mark.req("Re-evaluation computes agreement against human ratings")
def test_re_evaluate_with_human_ratings_produces_real_kappa():
    """With require_human_ratings=True (the fix), the generator joins humans and reports real metrics."""
    final = _drive(require_human_ratings=True)

    assert final is not None and final.get("success") is True
    metrics = final["metrics"]
    # All 4 human-rated traces were joined and scored against the judge.
    assert metrics["total_evaluations"] == 4
    # Every evaluation carries a real human rating (the bug left these None).
    assert all(e["human_rating"] is not None for e in final["evaluations"])
    # 3/4 agree -> accuracy 0.75 and a real, positive kappa (not the degenerate 0).
    assert metrics["accuracy"] == pytest.approx(0.75)
    assert metrics["correlation"] > 0.0


@pytest.mark.spec("JUDGE_EVALUATION_SPEC")
@pytest.mark.req("Re-evaluation computes agreement against human ratings")
def test_re_evaluate_without_human_ratings_reproduces_kappa_zero_bug():
    """The old require_human_ratings=False path leaves human_rating=None, so kappa collapses to 0."""
    final = _drive(require_human_ratings=False)

    assert final is not None and final.get("success") is True
    metrics = final["metrics"]
    # Same judge predictions, but no humans joined -> zero valid pairs -> kappa 0.
    assert all(e["human_rating"] is None for e in final["evaluations"])
    assert metrics["correlation"] == 0.0
