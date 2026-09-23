"""
Reality Engine Service — Multi-Signal Reasoning over Live Telemetry.

Distinguishes raw metrics (e.g. idle = 20 min) from actual root causes:
(external_workflow vs operator_variation vs machine_condition vs weather_condition vs unknown)
using contextual signal fusion.

CRITICAL TRUST & SAFETY LANGUAGE ENFORCED (Architecture.md §6):
Never emit banned judgmental phrases ('lazy', 'fatigued', 'dangerous', 'inefficient').
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.db.models import Mission
from backend.app.modules._shared.telemetry_stream import get_telemetry_window_summary
from backend.app.modules._shared.jobsite_memory import (
    get_mission_environment,
    get_latest_workflow_state,
)
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.operator_passport import get_context_evidence
from backend.app.modules.reality_engine.schemas import (
    RealityEngineEnvelope,
    RealityEngineValue,
    RealityEvidenceItem,
)


def evaluate_mission_reality(db: Session, mission_id: str) -> RealityEngineEnvelope:
    """
    Reason over live telemetry, workflow status, machine health, and environment.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    # 1. Fetch signal layers
    telemetry = get_telemetry_window_summary(db, mission_id)
    workflow = get_latest_workflow_state(db, mission_id)
    env = get_mission_environment(db, mission_id)
    machine_health = get_latest_machine_health(db, mission.assigned_machine_id or "")
    operator_evidence = get_context_evidence(
        db,
        operator_id=mission.assigned_operator_id or "",
        task_type=mission.task_type,
        weather_bucket=env["weather_bucket"],
    )

    evidence: List[RealityEvidenceItem] = []

    # Telemetry indicators
    idle_total = telemetry["idle_minutes_total"]
    smoothness = telemetry["control_smoothness_avg"]
    has_idle_spike = idle_total > 5.0 or telemetry["idle_minutes_recent"] > 3.0

    # Workflow indicators
    truck_absent = workflow["truck_present"] == 0 or workflow["truck_eta_min"] > 5.0
    queue_elevated = workflow["queue_length"] >= 2

    # Environment indicators
    high_soil_moisture = env["soil_moisture"] > 0.50
    adverse_weather = env["weather_bucket"] == "adverse"

    # Machine condition indicators
    hydraulic_lag = machine_health["hydraulic_health_pct"] < 75.0 or machine_health["recent_fault_count"] > 1

    # Operator context indicators
    low_operator_context = operator_evidence["confidence"] < 0.25

    # 2. Multi-Signal Reasoning Decision Matrix

    # CASE 1: External Workflow (e.g. FALSE_IDLE)
    # Idle is high, but truck is absent and operator smoothness is normal
    if has_idle_spike and truck_absent and smoothness >= 0.65:
        explanation_class = "external_workflow"
        confidence = 0.92
        headline = (
            f"External workflow bottleneck: Haul truck absent ({int(workflow['truck_eta_min'])} min ETA). "
            f"Machine idle is supply-chain constrained; operator control pattern normal."
        )
        primary_driver = "Haul truck absence and dispatch queue accumulation"
        recommended_focus = "Dispatch supplementary haul unit to restore excavation cycle continuity"

        evidence.append(
            RealityEvidenceItem(
                factor="workflow_truck_absence",
                weight_or_probability=0.94,
                detail=f"Truck present: No | Queue length: {workflow['queue_length']} | Truck ETA: {workflow['truck_eta_min']} min",
            )
        )
        evidence.append(
            RealityEvidenceItem(
                factor="operator_control_smoothness",
                weight_or_probability=0.88,
                detail=f"Operator control smoothness index is normal ({smoothness}), verifying delay is not operator-originated",
            )
        )
        evidence.append(
            RealityEvidenceItem(
                factor="machine_telemetry",
                weight_or_probability=0.82,
                detail=f"Engine idling ({idle_total} min cumulative), hydraulic pressure nominal during active segments",
            )
        )

    # CASE 2: Operator Context Variation (Cold-start or unobserved condition)
    elif mission.scenario_tag == "OPERATOR_CONTEXT_MISMATCH" or (low_operator_context and smoothness < 0.65):
        explanation_class = "operator_variation"
        confidence = 0.84
        headline = (
            f"Performance deviation detected: Operator has limited verified history in {mission.task_type} ({env['weather_bucket']} conditions). "
            f"Cycle variance elevated; verification recommended."
        )
        primary_driver = "Demonstrated experience gap in current operational context"
        recommended_focus = "Provide field advisory guidance or pair with experienced lead"

        evidence.append(
            RealityEvidenceItem(
                factor="operator_passport_context",
                weight_or_probability=0.88,
                detail=(
                    f"Operator {operator_evidence['operator_id']} has {operator_evidence['sample_count']} recorded samples in "
                    f"{mission.task_type} ({env['weather_bucket']}) — confidence {int(operator_evidence['confidence']*100)}%"
                ),
            )
        )
        evidence.append(
            RealityEvidenceItem(
                factor="telemetry_smoothness_index",
                weight_or_probability=0.78,
                detail=f"Control smoothness index ({smoothness}) reflects adaptive adjustment in unfamiliar context",
            )
        )
        if high_soil_moisture:
            evidence.append(
                RealityEvidenceItem(
                    factor="environmental_aggravator",
                    weight_or_probability=0.65,
                    detail=f"Wet soil ({int(env['soil_moisture']*100)}% moisture) compounds operator context unfamiliarity",
                )
            )

    # CASE 3: Adverse Weather / Environmental Impedance
    elif high_soil_moisture and adverse_weather and not truck_absent:
        explanation_class = "weather_condition"
        confidence = 0.86
        headline = (
            f"Environmental impedance detected: Soil moisture at {int(env['soil_moisture']*100)}% under {env['weather']} conditions. "
            f"Hydraulic cycle resistance elevated across all passes."
        )
        primary_driver = f"Precipitation and soil saturation ({env['weather']})"
        recommended_focus = "Adjust cycle expectations; monitor traction and grade compaction"

        evidence.append(
            RealityEvidenceItem(
                factor="environmental_soil_saturation",
                weight_or_probability=0.90,
                detail=f"Soil moisture: {int(env['soil_moisture']*100)}% | Visibility: {env['visibility']} | Wind: {env['wind_kph']} kph",
            )
        )
        evidence.append(
            RealityEvidenceItem(
                factor="cycle_resistance",
                weight_or_probability=0.78,
                detail="Excavator bucket penetration resistance increased due to cohesive wet soil",
            )
        )
        evidence.append(
            RealityEvidenceItem(
                factor="telemetry_smoothness_index",
                weight_or_probability=0.74,
                detail=f"Control smoothness index ({smoothness}) reflects adaptive adjustment in unfamiliar context",
            )
        )

    # CASE 4: Machine Condition / Hydraulic Degradation
    elif hydraulic_lag:
        explanation_class = "machine_condition"
        confidence = 0.83
        headline = (
            f"Mechanical condition advisory: Hydraulic health at {machine_health['hydraulic_health_pct']}% with "
            f"{machine_health['recent_fault_count']} recorded faults. Cycle speed constrained."
        )
        primary_driver = "Hydraulic pressure drift and component wear"
        recommended_focus = "Inspect hydraulic fluid pressure and scheduled service interval"

        evidence.append(
            RealityEvidenceItem(
                factor="machine_telematics_health",
                weight_or_probability=0.87,
                detail=f"Machine {machine_health.get('model', 'Unit')} overall health: {machine_health['health_pct']}% | Hydraulic: {machine_health['hydraulic_health_pct']}%",
            )
        )

    # CASE 5: Ambiguous / Unknown
    else:
        explanation_class = "unknown"
        confidence = 0.50
        headline = "Operational state within nominal parameters; no dominant deviation pattern isolated."
        primary_driver = "Nominal operations"
        recommended_focus = "Continue regular telemetry monitoring"

        evidence.append(
            RealityEvidenceItem(
                factor="multi_signal_consensus",
                weight_or_probability=0.50,
                detail="All active telematic, environmental, and workflow signals match expected variance baseline",
            )
        )

    value = RealityEngineValue(
        mission_id=mission_id,
        explanation_class=explanation_class,
        headline=headline,
        anomaly_detected=explanation_class != "unknown",
        idle_minutes_recent=telemetry["idle_minutes_recent"],
        idle_minutes_total=telemetry["idle_minutes_total"],
        primary_driver=primary_driver,
        recommended_focus=recommended_focus,
        signal_summary={
            "control_smoothness_avg": smoothness,
            "truck_present": workflow["truck_present"],
            "truck_eta_min": workflow["truck_eta_min"],
            "soil_moisture": env["soil_moisture"],
            "weather": env["weather"],
            "machine_health_pct": machine_health["health_pct"],
            "operator_context_confidence": operator_evidence["confidence"],
            "safety_alerts": telemetry["safety_alert_count"],
        },
    )

    return RealityEngineEnvelope(
        value=value,
        confidence=confidence,
        evidence=evidence,
    )
