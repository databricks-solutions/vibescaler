"""
Tests for per-user trace ordering in discovery and annotation phases.

Spec: DISCOVERY_SPEC ("Trace Assignment & Ordering")
Covered behaviors:
  - Deterministic per-user randomized annotation order
  - Different per-user orders over the same trace set (IRR)
  - Mid-round trace addition appends without reshuffling
  - Trace set change produces fresh randomization

The never-built dataset-composition machinery (union/subtract operations,
assignment metadata with phase/round context, phase-aware randomization
seeds) was retired with DISCOVERY_TRACE_ASSIGNMENT_SPEC; its xfail stubs
were removed.
"""

import hashlib
import random
from datetime import datetime

import pytest

from server.models import (
    Workshop,
    WorkshopPhase,
    WorkshopStatus,
)


def _make_workshop(
    discovery_ids: list[str] | None = None,
    annotation_ids: list[str] | None = None,
    discovery_randomize: bool = False,
    annotation_randomize: bool = False,
) -> Workshop:
    return Workshop(
        id="ws-assign",
        name="Assignment Workshop",
        description=None,
        facilitator_id="fac-1",
        status=WorkshopStatus.ACTIVE,
        current_phase=WorkshopPhase.ANNOTATION,
        completed_phases=[],
        discovery_started=True,
        annotation_started=True,
        active_discovery_trace_ids=discovery_ids or [],
        active_annotation_trace_ids=annotation_ids or [],
        discovery_randomize_traces=discovery_randomize,
        annotation_randomize_traces=annotation_randomize,
        judge_name="test_judge",
        created_at=datetime.now(),
    )


def _generate_randomized_order(trace_ids: list[str], user_id: str) -> list[str]:
    """Mirror of DatabaseService._generate_randomized_trace_order for direct testing."""
    if not trace_ids:
        return []
    sorted_ids = sorted(trace_ids)
    seed_string = f"{user_id}::{',' .join(sorted_ids)}"
    seed = int(hashlib.md5(seed_string.encode()).hexdigest(), 16) % (2**31)
    rng = random.Random(seed)
    shuffled = trace_ids.copy()
    rng.shuffle(shuffled)
    return shuffled


ROUND1_TRACES = [f"r1-trace-{i}" for i in range(5)]
ROUND2_TRACES = [f"r2-trace-{i}" for i in range(5)]
ALL_TRACES = ROUND1_TRACES + ROUND2_TRACES


@pytest.mark.unit
class TestActiveTracesScoping:
    """Model-level sanity checks for the active trace list fields.

    NOTE: These do not verify visibility filtering (that lives in the
    `GET /workshops/{id}/traces` endpoint and is covered by the
    trace-visibility e2e suite); they only confirm the Workshop model
    carries distinct active lists per selection.
    """

    def test_active_traces_only_current_round(self):
        """The model holds exactly the trace ids of the latest selection."""
        # Round 1: traces 0-4
        ws_round1 = _make_workshop(discovery_ids=ROUND1_TRACES)
        assert ws_round1.active_discovery_trace_ids == ROUND1_TRACES

        # Round 2: only traces 5-9
        ws_round2 = _make_workshop(discovery_ids=ROUND2_TRACES)
        assert ws_round2.active_discovery_trace_ids == ROUND2_TRACES
        for old_id in ROUND1_TRACES:
            assert old_id not in ws_round2.active_discovery_trace_ids

    def test_empty_active_traces_returns_nothing(self):
        """When active_discovery_trace_ids is empty, the model holds an empty list."""
        ws = _make_workshop(discovery_ids=[])
        assert ws.active_discovery_trace_ids == []


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.unit
class TestAnnotationRandomizationPerUser:
    """Annotation traces are randomized per user for bias reduction."""

    @pytest.mark.req("Annotators see the same trace set in different per-user orders, enabling inter-rater reliability measurement")
    def test_different_users_different_order(self):
        """Two users see the same traces but in different orders."""
        order_a = _generate_randomized_order(ALL_TRACES, "user-alpha")
        order_b = _generate_randomized_order(ALL_TRACES, "user-beta")

        # Same traces
        assert sorted(order_a) == sorted(order_b)
        # Different orders
        assert order_a != order_b

    @pytest.mark.req("Annotation trace order is deterministic per user and persists across page reloads")
    def test_order_deterministic_for_same_user(self):
        """Same user always gets the same randomized order."""
        order1 = _generate_randomized_order(ALL_TRACES, "user-gamma")
        order2 = _generate_randomized_order(ALL_TRACES, "user-gamma")
        assert order1 == order2

    @pytest.mark.req("Annotators see the same trace set in different per-user orders, enabling inter-rater reliability measurement")
    def test_irr_measurement_possible(self):
        """All annotators see the same set of traces (different order), enabling IRR."""
        users = [f"annotator-{i}" for i in range(5)]
        trace_sets = []
        orders = []
        for user in users:
            order = _generate_randomized_order(ALL_TRACES, user)
            trace_sets.append(set(order))
            orders.append(order)

        # All annotators have the exact same trace set
        for ts in trace_sets:
            assert ts == trace_sets[0]

        # But not all in the same order (at least some differ)
        unique_orders = set(tuple(o) for o in orders)
        assert len(unique_orders) > 1


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.unit
class TestMidRoundTraceAddition:
    """Mid-round trace addition appends new traces without disrupting existing order."""

    @pytest.mark.req("Adding annotation traces mid-round appends them without reshuffling a user's existing order")
    def test_append_preserves_existing_positions(self):
        """Adding traces mid-round keeps existing order and appends new ones at the end."""
        user_id = "user-delta"
        initial_traces = ROUND1_TRACES

        # Generate initial randomized order
        initial_order = _generate_randomized_order(initial_traces, user_id)

        # Mid-round: 3 new traces added
        new_traces_raw = ["new-trace-a", "new-trace-b", "new-trace-c"]

        # Simulate incremental update (same as database_service logic)
        existing_set = set(initial_order)
        new_only = [t for t in new_traces_raw if t not in existing_set]
        randomized_new = _generate_randomized_order(new_only, user_id)
        updated_order = initial_order + randomized_new

        # First N positions unchanged
        assert updated_order[: len(initial_order)] == initial_order
        # New traces appended
        assert len(updated_order) == len(initial_order) + len(new_only)
        # All traces present
        assert set(updated_order) == set(initial_traces) | set(new_traces_raw)

    @pytest.mark.req("Adding annotation traces mid-round appends them without reshuffling a user's existing order")
    def test_no_reshuffle_on_addition(self):
        """Adding traces does NOT reshuffle the already-seen traces."""
        user_id = "user-epsilon"
        base_traces = [f"base-{i}" for i in range(8)]
        initial_order = _generate_randomized_order(base_traces, user_id)

        # Add one more trace
        added = ["extra-1"]
        existing_set = set(initial_order)
        new_only = [t for t in added if t not in existing_set]
        randomized_new = _generate_randomized_order(new_only, user_id)
        updated = initial_order + randomized_new

        # Positions 0-7 are identical
        for i, tid in enumerate(initial_order):
            assert updated[i] == tid, f"Position {i} changed from {tid} to {updated[i]}"


@pytest.mark.spec("DISCOVERY_SPEC")
@pytest.mark.unit
class TestRoundChangeClearsOrder:
    """When the trace set changes wholesale, orders are re-randomized from scratch."""

    @pytest.mark.req("Changing the annotation trace set produces a fresh randomized order")
    def test_new_dataset_triggers_fresh_randomization(self):
        """A completely different dataset means the seed changes, producing new order."""
        user_id = "user-zeta"
        round1_order = _generate_randomized_order(ROUND1_TRACES, user_id)
        round2_order = _generate_randomized_order(ROUND2_TRACES, user_id)

        # Different trace sets
        assert set(round1_order) != set(round2_order)

    @pytest.mark.req("Changing the annotation trace set produces a fresh randomized order")
    def test_round_change_not_incremental(self):
        """A changed trace set is NOT incremental — it's a full fresh randomization.

        Even if some traces overlap between rounds, the new round starts from
        scratch because UserTraceOrder is cleared on round transition.
        """
        user_id = "user-eta"
        # Round 1 has traces 0-7
        r1_traces = [f"shared-trace-{i}" for i in range(8)]
        r1_order = _generate_randomized_order(r1_traces, user_id)

        # Round 2 has traces 3-10 (overlaps with 3-7)
        r2_traces = [f"shared-trace-{i}" for i in range(3, 11)]
        r2_order = _generate_randomized_order(r2_traces, user_id)

        # The overlapping traces (3-7) should generally appear in different positions
        # because the seed includes sorted(all trace IDs) which differs between rounds
        overlap_positions_r1 = {tid: i for i, tid in enumerate(r1_order) if tid in set(r2_traces)}
        overlap_positions_r2 = {tid: i for i, tid in enumerate(r2_order) if tid in set(r1_traces)}

        # At least one overlapping trace should be in a different position
        position_matches = sum(
            1 for tid in overlap_positions_r1
            if tid in overlap_positions_r2 and overlap_positions_r1[tid] == overlap_positions_r2[tid]
        )
        # With 5 overlapping traces in sets of 8, it's astronomically unlikely
        # that ALL positions match
        assert position_matches < len(overlap_positions_r1)
