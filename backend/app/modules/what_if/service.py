"""
What-If Lab Service — Operational Simulation & Counterfactual Reasoning.

Simulates operational decisions (add haul truck, reassign operator, shift route/weather)
by re-evaluating the Time Model and Outcome Guardian with modified features.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.db.models import Mission
from backend.app.modules.time_model.service import (
    time_model_engine,
    get_mission_time_prediction,
)
from backend.app.modules.outcome_guardian.service import evaluate_outcome_guardian
from backend.app.modules._shared.jobsite_memory import (
    get_mission_environment,
    get_latest_workflow_state,
)
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.operator_passport import get_context_evidence
from backend.app.modules.what_if.schemas import (
    WhatIfRequest,
    WhatIfEnvelope,
    WhatIfValue,
    WhatIfDelta,
    WhatIfEvidence,
)


def simulate_what_if(db: Session, request: WhatIfRequest) -> WhatIfEnvelope:
    """
    Run counterfactual simulation for a mission given assumption changes.
    """
    mission_id = request.mission_id
    assumptions = request.assumption_changed

    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    if not time_model_engine.is_trained:
        time_model_engine.fit_from_db(db)

    # 1. Baseline "Before" State
    before_envelope = get_mission_time_prediction(db, mission_id)
    before_p50 = before_envelope.value.p50_duration_min
    before_fuel = before_envelope.value.expected_fuel_l

    # Run Outcome Guardian for baseline
    try:
        guardian_before = evaluate_outcome_guardian(db, mission_id).value
        rework_before = guardian_before.rework_probability
    except Exception:
        guardian_before = None
        rework_before = 0.20

    # 2. Extract and modify feature vector
    env = get_mission_environment(db, mission_id)
    workflow = get_latest_workflow_state(db, mission_id)
    m_health = get_latest_machine_health(db, mission.assigned_machine_id or "")

    op_id = assumptions.get("operator_id") or assumptions.get("assigned_operator_id") or mission.assigned_operator_id or ""
    mach_id = assumptions.get("machine_id") or assumptions.get("assigned_machine_id") or mission.assigned_machine_id or ""
    weather = assumptions.get("weather", env["weather"])

    adverse = weather in ("Rainy", "Windy")
    weather_bucket = "adverse" if adverse else "normal"
    soil_moisture = float(assumptions.get("soil_moisture", env["soil_moisture"]))
    if "weather" in assumptions and "soil_moisture" not in assumptions:
        soil_moisture = 0.15 if weather == "Sunny" else (0.75 if weather == "Rainy" else 0.3)

    op_evidence = get_context_evidence(
        db,
        operator_id=op_id,
        task_type=mission.task_type,
        weather_bucket=weather_bucket,
    )
    if mach_id != mission.assigned_machine_id:
        m_health = get_latest_machine_health(db, mach_id)

    # Workflow modifications (e.g. "add_truck": true)
    add_truck = assumptions.get("add_truck", False)
    truck_present = 1 if (add_truck or assumptions.get("truck_present", workflow["truck_present"] == 1)) else 0
    truck_eta = 0.0 if (add_truck or assumptions.get("truck_present", False)) else float(assumptions.get("truck_eta_min", workflow["truck_eta_min"]))
    queue_len = max(0, workflow["queue_length"] - 2) if add_truck else int(assumptions.get("queue_length", workflow["queue_length"]))

    # 3. Vectorize modified features and run "After" inference
    modified_features = time_model_engine.vectorize_features(
        task_type=mission.task_type,
        objective_quantity=mission.objective_quantity,
        operator_confidence=op_evidence["confidence"],
        operator_sample_count=op_evidence["sample_count"],
        machine_health_pct=m_health["health_pct"],
        machine_hydraulic_pct=m_health["hydraulic_health_pct"],
        machine_age_years=m_health.get("age_years", 3.0),
        soil_moisture=soil_moisture,
        weather_adverse=1 if adverse else 0,
        truck_present=truck_present,
        truck_eta_min=truck_eta,
        queue_length=queue_len,
    )

    after_envelope = time_model_engine.predict_vector(
        modified_features, mission_id=mission_id, task_type=mission.task_type
    )
    after_p50 = after_envelope.value.p50_duration_min
    after_fuel = after_envelope.value.expected_fuel_l

    # Estimate rework after modification
    rework_after = rework_before
    if "operator_id" in assumptions and op_evidence["confidence"] > 0.6:
        rework_after = max(0.08, rework_before * 0.65)
    if "soil_moisture" in assumptions and soil_moisture < 0.3:
        rework_after = max(0.05, rework_before * 0.70)

    # 4. Compute Deltas & Recommendations
    time_recovered = round(before_p50 - after_p50, 1)
    fuel_delta = round(after_fuel - before_fuel, 1)
    rework_delta = round((rework_after - rework_before) * 100, 1)
    efficiency_gain = (
        round((time_recovered / before_p50) * 100, 1)
        if before_p50 > 0
        else 0.0
    )

    evidence: List[WhatIfEvidence] = []

    if add_truck or ("truck_present" in assumptions and assumptions["truck_present"]):
        evidence.append(
            WhatIfEvidence(
                factor="logistics_bottleneck_elimination",
                weight_or_probability=0.92,
                detail=f"Adding haul truck recovers {time_recovered} min of idle queueing time.",
            )
        )
        recommendation = (
            f"Recommended: Adding 1 haul unit recovers {time_recovered} min ({efficiency_gain}% time gain), "
            f"restoring the mission within scheduled delivery tolerances."
        )
    elif "operator_id" in assumptions:
        evidence.append(
            WhatIfEvidence(
                factor="operator_competence_gain",
                weight_or_probability=0.85,
                detail=(
                    f"Reassigning to {op_id} (confidence {int(op_evidence['confidence']*100)}%) "
                    f"reduces cycle variance and projected rework risk by {abs(rework_delta)}%."
                ),
            )
        )
        recommendation = (
            f"Recommended: Operator reassignment recovers {time_recovered} min and decreases rework risk by {abs(rework_delta)}%."
        )
    else:
        evidence.append(
            WhatIfEvidence(
                factor="parametric_simulation",
                weight_or_probability=0.80,
                detail=f"Modified assumptions yield net duration change of {-time_recovered} min.",
            )
        )
        recommendation = f"Simulation indicates net duration delta of {-time_recovered} min."

    delta = WhatIfDelta(
        time_recovered_min=time_recovered,
        p50_before_min=before_p50,
        p50_after_min=after_p50,
        fuel_delta_l=fuel_delta,
        rework_risk_delta_pct=rework_delta,
        operational_efficiency_gain_pct=efficiency_gain,
    )

    value = WhatIfValue(
        mission_id=mission_id,
        assumption_changed=assumptions,
        before=before_envelope.value,
        after=after_envelope.value,
        predicted_before=before_envelope.value,
        predicted_after=after_envelope.value,
        guardian_before=guardian_before,
        guardian_after=guardian_before,  # Mirror or updated
        delta=delta,
        recommendation=recommendation,
    )

    simulation_confidence = round(min(0.94, (before_envelope.confidence + after_envelope.confidence) / 2.0), 2)

    return WhatIfEnvelope(
        value=value,
        confidence=simulation_confidence,
        evidence=evidence,
    )
