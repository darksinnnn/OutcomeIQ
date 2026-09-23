"""
Test data layer integrity and named demo scenarios.
"""

from backend.app.db.database import SessionLocal
from backend.app.db.models import (
    Mission,
    Operator,
    Machine,
    Telemetry,
    Outcome,
    WorkflowEvent,
    OperatorCapabilityEvidence,
)
from backend.app.modules._shared.operator_passport import get_context_evidence
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.jobsite_memory import (
    get_mission_environment,
    get_latest_workflow_state,
)
from backend.app.modules._shared.telemetry_stream import get_telemetry_window_summary


def test_database_connectivity_and_tables():
    db = SessionLocal()
    try:
        missions = db.query(Mission).count()
        operators = db.query(Operator).count()
        machines = db.query(Machine).count()
        assert missions >= 200, f"Expected >= 200 missions, got {missions}"
        assert operators >= 8, f"Expected >= 8 operators, got {operators}"
        assert machines >= 6, f"Expected >= 6 machines, got {machines}"
    finally:
        db.close()


def test_scenario_false_idle():
    """
    Scenario 1: Idle spike caused by truck bottleneck, NOT operator inefficiency.
    """
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == "MISSION-FALSE-IDLE").first()
        assert mission is not None, "MISSION-FALSE-IDLE missing"

        summary = get_telemetry_window_summary(db, "MISSION-FALSE-IDLE")
        assert summary["idle_minutes_total"] > 5.0, "Expected significant idle minutes"
        assert summary["control_smoothness_avg"] >= 0.70, (
            "Control smoothness should be normal (proving operator is not inefficient)"
        )

        workflow = get_latest_workflow_state(db, "MISSION-FALSE-IDLE")
        assert workflow["has_workflow_data"] is True

        outcome = db.query(Outcome).filter(Outcome.mission_id == "MISSION-FALSE-IDLE").first()
        assert outcome is not None
        assert outcome.delay_reason == "truck"
    finally:
        db.close()


def test_scenario_on_time_low_quality():
    """
    Scenario 3: Mission is on schedule, but quality is degraded underneath.
    """
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == "MISSION-ON-TIME-LOW-QUALITY").first()
        assert mission is not None, "MISSION-ON-TIME-LOW-QUALITY missing"

        outcome = db.query(Outcome).filter(Outcome.mission_id == "MISSION-ON-TIME-LOW-QUALITY").first()
        assert outcome is not None

        # Verify on-schedule (<15% deviation from naive baseline)
        naive = mission.naive_estimated_time_min
        actual = outcome.actual_duration_min
        drift_pct = abs(actual - naive) / naive
        assert drift_pct < 0.15, f"Drift {drift_pct} should be < 0.15 to represent 'on-schedule'"

        # Verify quality is degraded (< 0.75)
        assert outcome.quality_score < 0.75, f"Expected degraded quality, got {outcome.quality_score}"
    finally:
        db.close()


def test_scenario_operator_context_mismatch():
    """
    Scenario 2: Competent operator, but near-zero evidence in this specific context (cold start).
    """
    db = SessionLocal()
    try:
        mission = db.query(Mission).filter(Mission.id == "MISSION-OPERATOR-CONTEXT-MISMATCH").first()
        assert mission is not None, "MISSION-OPERATOR-CONTEXT-MISMATCH missing"

        env = get_mission_environment(db, "MISSION-OPERATOR-CONTEXT-MISMATCH")
        evidence = get_context_evidence(
            db,
            operator_id=mission.assigned_operator_id,
            task_type=mission.task_type,
            weather_bucket=env["weather_bucket"],
        )
        assert evidence["confidence"] <= 0.15, (
            f"Expected low/cold-start confidence, got {evidence['confidence']}"
        )
    finally:
        db.close()


def test_operator_passport_trust_language():
    """
    Ensure no banned judgmental words are emitted by Operator Passport evidence labels.
    """
    db = SessionLocal()
    try:
        operators = db.query(Operator).all()
        banned = ["lazy", "fatigued", "dangerous", "inefficient"]
        for op in operators:
            ev = get_context_evidence(db, op.id, "Earth Excavation", "normal")
            label_lower = ev["evidence_label"].lower()
            for word in banned:
                assert word not in label_lower, f"Banned word '{word}' found in evidence label"
    finally:
        db.close()
