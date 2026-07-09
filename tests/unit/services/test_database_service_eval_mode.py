"""Unit tests for eval-mode schema and workshop mode contracts."""

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.database import Base
from server.models import (
    TraceCriterionCreate,
    TraceCriterionType,
    WorkshopCreate,
    WorkshopMode,
)
from server.services.database_service import DatabaseService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.mark.spec("EVAL_MODE_SPEC")
@pytest.mark.req("Workshop can be created with `mode: \"eval\"`")
def test_create_workshop_with_eval_mode(test_db):
    service = DatabaseService(test_db)
    created = service.create_workshop(
        WorkshopCreate(
            name="Eval workshop",
            description="Per-trace criteria workshop",
            facilitator_id="fac-1",
            mode=WorkshopMode.EVAL,
        )
    )

    assert created.mode == WorkshopMode.EVAL


@pytest.mark.spec("EVAL_MODE_SPEC")
@pytest.mark.req("Existing workshop-mode behavior is unchanged")
def test_create_workshop_defaults_to_workshop_mode(test_db):
    service = DatabaseService(test_db)
    created = service.create_workshop(
        WorkshopCreate(
            name="Default workshop",
            description="Uses existing behavior",
            facilitator_id="fac-1",
        )
    )

    assert created.mode == WorkshopMode.WORKSHOP


@pytest.mark.spec("EVAL_MODE_SPEC")
@pytest.mark.req("Each criterion has a type (standard or hurdle) and weight (-10 to +10)")
def test_trace_criterion_create_requires_valid_weight_and_type():
    criterion = TraceCriterionCreate(
        text="States at least one concrete recommendation",
        criterion_type=TraceCriterionType.STANDARD,
        weight=7,
        created_by="fac-1",
    )

    assert criterion.criterion_type == TraceCriterionType.STANDARD
    assert criterion.weight == 7

    with pytest.raises(ValidationError):
        TraceCriterionCreate(
            text="Invalid over-weight criterion",
            criterion_type=TraceCriterionType.STANDARD,
            weight=11,
            created_by="fac-1",
        )

    with pytest.raises(ValidationError):
        TraceCriterionCreate(
            text="Invalid under-weight criterion",
            criterion_type=TraceCriterionType.STANDARD,
            weight=-11,
            created_by="fac-1",
        )


@pytest.mark.spec("EVAL_MODE_SPEC")
def test_eval_mode_tables_are_present_in_metadata():
    table_names = set(Base.metadata.tables.keys())
    assert "trace_criteria" in table_names
    assert "criterion_evaluations" in table_names


@pytest.mark.spec("EVAL_MODE_SPEC")
@pytest.mark.req("Mode is immutable after creation")
def test_workshop_mode_is_immutable(test_db):
    service = DatabaseService(test_db)
    created = service.create_workshop(
        WorkshopCreate(
            name="Immutable mode workshop",
            description="Mode cannot change",
            facilitator_id="fac-1",
            mode=WorkshopMode.WORKSHOP,
        )
    )

    with pytest.raises(ValueError, match="immutable"):
        service.update_workshop_mode(created.id, WorkshopMode.EVAL)


@pytest.mark.spec("EVAL_MODE_SPEC")
@pytest.mark.req("Deleting all traces removes eval-mode criteria and evaluations")
def test_delete_all_traces_removes_eval_mode_rows(test_db):
    """delete_all_traces must cascade to trace_criteria and criterion_evaluations.

    Regression for B3: these eval-mode tables (migration 0020) were omitted from
    delete_all_traces. FK ondelete=CASCADE is a no-op because the app runs SQLite
    without PRAGMA foreign_keys=ON and uses bulk deletes, so the rows were orphaned
    and resurfaced after re-ingest.
    """
    from server.database import CriterionEvaluationDB, TraceCriterionDB, TraceDB

    service = DatabaseService(test_db)
    workshop = service.create_workshop(
        WorkshopCreate(
            name="Eval workshop",
            description="Per-trace criteria workshop",
            facilitator_id="fac-1",
            mode=WorkshopMode.EVAL,
        )
    )

    test_db.add_all(
        [
            TraceDB(id="trace-1", workshop_id=workshop.id, input="in", output="out"),
            TraceCriterionDB(
                id="crit-1",
                trace_id="trace-1",
                workshop_id=workshop.id,
                text="States a concrete recommendation",
                criterion_type="standard",
                created_by="fac-1",
            ),
            CriterionEvaluationDB(
                id="eval-1",
                criterion_id="crit-1",
                trace_id="trace-1",
                workshop_id=workshop.id,
                judge_model="gpt-4",
                met=True,
            ),
        ]
    )
    test_db.commit()

    assert test_db.query(TraceCriterionDB).count() == 1
    assert test_db.query(CriterionEvaluationDB).count() == 1

    deleted = service.delete_all_traces(workshop.id)

    assert deleted == 1
    assert test_db.query(TraceCriterionDB).count() == 0
    assert test_db.query(CriterionEvaluationDB).count() == 0
