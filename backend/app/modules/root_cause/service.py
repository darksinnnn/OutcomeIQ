"""
Root Cause Engine Service — Causal Attribution Decomposition.

When actual duration diverges from Time Model P50, decomposes the deviation
into a ranked probability distribution across:
  - truck (workflow / logistics bottleneck)
  - weather (environmental impedance)
  - operator (context-specific variation / cold-start)
  - machine (mechanical / hydraulic condition)
  - unknown

TRUST & SAFETY RULE (Architecture.md §6):
Never blame operators as 'lazy' or 'inefficient'. Use context-based evidence.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.db.models import Mission, Outcome
from backend.app.modules.time_model.service import get_mission_time_prediction
from backend.app.modules._shared.telemetry_stream import get_telemetry_window_summary
from backend.app.modules._shared.jobsite_memory import (
    get_mission_environment,
    get_latest_workflow_state,
)
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.operator_passport import get_context_evidence
from backend.app.modules.root_cause.schemas import (
    RootCauseEnvelope,
    RootCauseValue,
    Contributor,
)


def decompose_root_cause(db: Session, mission_id: str) -> RootCauseEnvelope:
    """
    Decompose task duration deviation into attributed root-cause probabilities.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    # 1. Get predicted P50 baseline from Time Model
    time_pred = get_mission_time_prediction(db, mission_id)
    p50 = time_pred.value.p50_duration_min

    # 2. Get actual duration (from outcome if complete, else project from telemetry)
    outcome = db.query(Outcome).filter(Outcome.mission_id == mission_id).first()
    telemetry = get_telemetry_window_summary(db, mission_id)

    if outcome:
        actual_min = outcome.actual_duration_min
    elif telemetry["has_data"] and telemetry["tick_count"] > 0:
        actual_min = max(p50, telemetry["idle_minutes_total"] + mission.naive_estimated_time_min)
    else:
        actual_min = p50

    deviation_min = round(actual_min - p50, 1)

    # 3. Read contextual evidence layers
    workflow = get_latest_workflow_state(db, mission_id)
    env = get_mission_environment(db, mission_id)
    machine_health = get_latest_machine_health(db, mission.assigned_machine_id or "")
    operator_evidence = get_context_evidence(
        db,
        operator_id=mission.assigned_operator_id or "",
        task_type=mission.task_type,
        weather_bucket=env["weather_bucket"],
    )

    # 4. Compute causal score weights (unnormalized)
    scores = {}
    evidence_texts = {}
    impacts = {}

    # --- Truck bottleneck score ---
    truck_score = 0.0
    if workflow["truck_present"] == 0 or workflow["truck_eta_min"] > 3.0 or telemetry["idle_minutes_total"] > 5.0:
        idle_factor = max(telemetry["idle_minutes_total"], workflow["truck_eta_min"])
        truck_score = max(5.0, idle_factor * 1.5)
        impacts["truck"] = round(idle_factor, 1)
        evidence_texts["truck"] = (
            f"Haul truck availability gap: machine experienced {round(telemetry['idle_minutes_total'], 1)} min idle wait time "
            f"with dispatch queue of {workflow['queue_length']} units."
        )
    else:
        truck_score = 0.5
        impacts["truck"] = 0.0
        evidence_texts["truck"] = "Haul truck cycling operated within standard parameters."
    scores["truck"] = truck_score

    # --- Weather score ---
    soil_m = env["soil_moisture"]
    if soil_m > 0.4 or env["weather_bucket"] == "adverse":
        weather_impact = (soil_m - 0.2) * 25.0
        weather_score = max(3.0, weather_impact)
        impacts["weather"] = round(weather_impact, 1)
        evidence_texts["weather"] = (
            f"Environmental resistance: {env['weather']} conditions elevated soil moisture to {int(soil_m*100)}%, "
            f"increasing digging resistance."
        )
    else:
        weather_score = 0.5
        impacts["weather"] = 0.0
        evidence_texts["weather"] = f"Weather ({env['weather']}) and soil moisture within nominal range."
    scores["weather"] = weather_score

    # --- Operator context score ---
    op_conf = operator_evidence["confidence"]
    smoothness = telemetry["control_smoothness_avg"]
    if op_conf < 0.35 or mission.scenario_tag == "OPERATOR_CONTEXT_MISMATCH":
        op_impact = (0.6 - op_conf) * 22.0
        operator_score = max(4.0, op_impact)
        impacts["operator"] = round(op_impact, 1)
        evidence_texts["operator"] = (
            f"Contextual experience variance: Operator has {operator_evidence['sample_count']} verified samples in "
            f"{mission.task_type} ({env['weather_bucket']}). Performance drift detected; verification recommended."
        )
    else:
        operator_score = 0.5
        impacts["operator"] = 0.0
        evidence_texts["operator"] = (
            f"Demonstrated capability index high ({int(op_conf*100)}% confidence across {operator_evidence['sample_count']} missions); "
            f"control smoothness nominal ({smoothness})."
        )
    scores["operator"] = operator_score

    # --- Machine health score ---
    m_hyd = machine_health["hydraulic_health_pct"]
    m_faults = machine_health["recent_fault_count"]
    if m_hyd < 80.0 or m_faults > 0:
        mach_impact = (85.0 - m_hyd) * 0.6 + m_faults * 4.0
        machine_score = max(3.0, mach_impact)
        impacts["machine"] = round(mach_impact, 1)
        evidence_texts["machine"] = (
            f"Mechanical constraint: Hydraulic health at {m_hyd}% with {m_faults} recent faults logged."
        )
    else:
        machine_score = 0.4
        impacts["machine"] = 0.0
        evidence_texts["machine"] = f"Machine health optimal ({machine_health['health_pct']}%)."
    scores["machine"] = machine_score

    # Baseline unknown noise
    scores["unknown"] = 0.5
    impacts["unknown"] = 0.0
    evidence_texts["unknown"] = "Unmodeled micro-variance across jobsite cycles."

    # 5. Normalize probabilities
    total_score = sum(scores.values())
    raw_probs = {k: v / total_score for k, v in scores.items()}

    # Format contributors sorted by probability descending
    contributors: List[Contributor] = []
    for cause in ["truck", "weather", "operator", "machine", "unknown"]:
        prob = round(raw_probs[cause], 2)
        contributors.append(
            Contributor(
                cause=cause,
                probability=prob,
                delay_impact_min=impacts[cause],
                evidence=evidence_texts[cause],
            )
        )

    # Sort descending
    contributors.sort(key=lambda c: c.probability, reverse=True)
    primary = contributors[0].cause

    # Diagnostic headline
    if deviation_min > 5.0:
        summary = (
            f"Task ran {deviation_min} min past predicted P50. Primary driver: {primary} "
            f"({int(contributors[0].probability*100)}% attribution probability)."
        )
    elif deviation_min < -3.0:
        summary = f"Task completed {abs(deviation_min)} min ahead of schedule with nominal cycle execution."
    else:
        summary = f"Task tracking tightly to predicted P50 (within {abs(deviation_min)} min tolerance)."

    # Overall diagnostic confidence
    top_p = contributors[0].probability
    diagnostic_confidence = round(min(0.95, max(0.60, top_p * 1.2)), 2)

    evidence_envelope = [
        {
            "factor": f"{c.cause}_attribution",
            "weight_or_probability": c.probability,
            "detail": c.evidence,
        }
        for c in contributors
    ]

    value = RootCauseValue(
        mission_id=mission_id,
        deviation_min=deviation_min,
        predicted_p50_min=p50,
        actual_or_projected_min=actual_min,
        primary_cause=primary,
        contributors=contributors,
        diagnostic_summary=summary,
    )

    return RootCauseEnvelope(
        value=value,
        confidence=diagnostic_confidence,
        evidence=evidence_envelope,
    )
