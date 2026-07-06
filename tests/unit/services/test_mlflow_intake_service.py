from types import SimpleNamespace

import pytest

from server.models import MLflowIntakeConfig, MLflowTraceInfo
from server.services.mlflow_intake_service import MLflowIntakeService


class _DummyDbService:
    def __init__(self):
        self.added_workshop_id = None
        self.added_traces = None

    def add_traces(self, workshop_id, traces):
        self.added_workshop_id = workshop_id
        self.added_traces = traces


@pytest.mark.spec("TRACE_INGESTION_SPEC")
def test_ingest_traces_sets_normalized_experiment_id(monkeypatch):
    db_service = _DummyDbService()
    service = MLflowIntakeService(db_service)
    config = MLflowIntakeConfig(experiment_id=' "12345" ', max_traces=1, filter_string=None)

    monkeypatch.setattr(
        service,
        "search_traces",
        lambda _config: [
            MLflowTraceInfo(
                trace_id="tr-1",
                request_preview="request",
                response_preview="response",
                status="OK",
                timestamp_ms=1,
            )
        ],
    )

    span = SimpleNamespace(
        name="span-1",
        span_type="LLM",
        inputs={"a": 1},
        outputs={"b": 2},
        start_time_ns=1,
        end_time_ns=2,
    )
    full_trace = SimpleNamespace(
        data=SimpleNamespace(spans=[span], request='{"messages": []}', response='{"messages": []}'),
        info=SimpleNamespace(execution_time_ms=10, status="OK", tags={"x": "y"}),
    )

    import server.services.mlflow_intake_service as intake_module

    monkeypatch.setattr(intake_module.mlflow, "get_trace", lambda trace_id: full_trace)
    monkeypatch.setattr(intake_module, "get_databricks_host", lambda: "https://dbc.example.com")

    ingested = service.ingest_traces("ws-1", config)

    assert ingested == 1
    assert db_service.added_workshop_id == "ws-1"
    assert len(db_service.added_traces) == 1
    assert db_service.added_traces[0].mlflow_experiment_id == "12345"
    assert db_service.added_traces[0].trace_metadata["mlflow_experiment_id"] == "12345"


@pytest.mark.spec("TRACE_INGESTION_SPEC")
def test_search_traces_uses_locations_argument(monkeypatch):
    db_service = _DummyDbService()
    service = MLflowIntakeService(db_service)
    config = MLflowIntakeConfig(experiment_id="exp-1", max_traces=5, filter_string=None)
    captured = {}

    def _fake_search_traces(**kwargs):
        captured.update(kwargs)
        return []

    import server.services.mlflow_intake_service as intake_module

    monkeypatch.setattr(intake_module.mlflow, "search_traces", _fake_search_traces)

    service.search_traces(config)

    assert captured["locations"] == ["exp-1"]
    assert "experiment_ids" not in captured


@pytest.mark.spec("TRACE_INGESTION_SPEC")
def test_search_traces_metadata_only_uses_server_previews(monkeypatch):
    """Search is metadata-only (include_spans=False) and previews come from TraceInfo.

    Downloading spans just to build list previews forces N fetches through the
    Databricks storage proxy, which restricted-egress apps cannot reach.
    """
    db_service = _DummyDbService()
    service = MLflowIntakeService(db_service)
    config = MLflowIntakeConfig(experiment_id="exp-1", max_traces=5, filter_string=None)
    captured = {}

    fake_trace = SimpleNamespace(
        info=SimpleNamespace(
            request_id="tr-1",
            request_preview='{"messages": [{"role": "user", "content": "hello from preview"}]}',
            response_preview='{"messages": [{"role": "assistant", "content": "answer from preview"}]}',
            execution_time_ms=5,
            status="OK",
            timestamp_ms=1,
            tags={},
        ),
        data=None,  # include_spans=False -> no trace data downloaded
    )

    def _fake_search_traces(**kwargs):
        captured.update(kwargs)
        return [fake_trace]

    import server.services.mlflow_intake_service as intake_module

    monkeypatch.setattr(intake_module.mlflow, "search_traces", _fake_search_traces)
    monkeypatch.setattr(intake_module, "get_databricks_host", lambda: "https://dbc.example.com")

    results = service.search_traces(config)

    assert captured["include_spans"] is False
    assert len(results) == 1
    assert results[0].request_preview == "hello from preview"
    assert results[0].response_preview == "answer from preview"


@pytest.mark.spec("TRACE_INGESTION_SPEC")
def test_ingest_falls_back_to_preview_only_when_spans_unreachable(monkeypatch):
    """Storage-proxy egress refusal degrades to preview-only ingest, not failure.

    Signed span-download URLs (*.storage.cloud.databricks.com) may be
    unreachable from Databricks Apps; intake must still ingest the traces using
    server-side previews and mark them preview_only.
    """
    db_service = _DummyDbService()
    service = MLflowIntakeService(db_service)
    config = MLflowIntakeConfig(experiment_id="exp-1", max_traces=1, filter_string=None)

    monkeypatch.setattr(
        service,
        "search_traces",
        lambda _config: [
            MLflowTraceInfo(
                trace_id="tr-1",
                request_preview="req",
                response_preview="resp",
                status="OK",
                timestamp_ms=1,
            )
        ],
    )
    monkeypatch.setattr(
        service,
        "_fetch_server_previews",
        lambda trace_id: (
            '{"messages": [{"role": "user", "content": "full preview input"}]}',
            '{"messages": [{"role": "assistant", "content": "full preview output"}]}',
        ),
    )

    def _refused(trace_id):
        raise Exception(
            "Failed to search MLflow traces: HTTPSConnectionPool("
            "host='us-east-2.storage.cloud.databricks.com', port=443): Max retries exceeded "
            "(Caused by NewConnectionError('[Errno 111] Connection refused'))"
        )

    import server.services.mlflow_intake_service as intake_module

    monkeypatch.setattr(intake_module.mlflow, "get_trace", _refused)
    monkeypatch.setattr(intake_module, "get_databricks_host", lambda: "https://dbc.example.com")

    ingested = service.ingest_traces("ws-1", config)

    assert ingested == 1
    assert service.last_ingest_preview_only == 1
    upload = db_service.added_traces[0]
    assert upload.input == "full preview input"
    assert upload.output == "full preview output"
    assert upload.context["preview_only"] is True
    assert upload.context["spans"] == []
    assert upload.trace_metadata["preview_only"] is True


@pytest.mark.spec("TRACE_INGESTION_SPEC")
def test_ingest_skips_trace_on_non_connectivity_error(monkeypatch):
    """Non-connectivity get_trace failures keep existing skip behavior (no fallback)."""
    db_service = _DummyDbService()
    service = MLflowIntakeService(db_service)
    config = MLflowIntakeConfig(experiment_id="exp-1", max_traces=1, filter_string=None)

    monkeypatch.setattr(
        service,
        "search_traces",
        lambda _config: [
            MLflowTraceInfo(
                trace_id="tr-1",
                request_preview="req",
                response_preview="resp",
                status="OK",
                timestamp_ms=1,
            )
        ],
    )

    def _boom(trace_id):
        raise RuntimeError("malformed trace payload")

    import server.services.mlflow_intake_service as intake_module

    monkeypatch.setattr(intake_module.mlflow, "get_trace", _boom)
    monkeypatch.setattr(intake_module, "get_databricks_host", lambda: "https://dbc.example.com")

    ingested = service.ingest_traces("ws-1", config)

    assert ingested == 0
    assert service.last_ingest_preview_only == 0
