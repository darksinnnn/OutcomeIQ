"""
Telemetry and Quality stream data access.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.db.models import Telemetry, QualityObservation


def get_mission_telemetry(db: Session, mission_id: str) -> List[Telemetry]:
    """Retrieve all chronological telemetry records for a mission."""
    return (
        db.query(Telemetry)
        .filter(Telemetry.mission_id == mission_id)
        .order_by(Telemetry.timestamp.asc())
        .all()
    )


def get_telemetry_window_summary(db: Session, mission_id: str) -> Dict[str, Any]:
    """
    Summarize recent telemetry window to drive Reality Engine and Live Operation.
    """
    records = get_mission_telemetry(db, mission_id)
    if not records:
        return {
            "has_data": False,
            "idle_minutes_total": 0.0,
            "idle_minutes_recent": 0.0,
            "fuel_used_l": 0.0,
            "load_cycles": 0,
            "control_smoothness_avg": 0.85,
            "seatbelt_status": "Fastened",
            "machine_moving": 0,
            "machine_speed_kph": 0.0,
            "safety_alert_count": 0,
            "safety_signal_pattern": "normal",
            "tick_count": 0,
        }

    total_idle = sum(r.idle_minutes for r in records)
    recent_tick = records[-1]
    recent_idle = recent_tick.idle_minutes

    smoothness_vals = [
        r.control_smoothness_score
        for r in records
        if r.control_smoothness_score is not None
    ]
    avg_smoothness = (
        round(sum(smoothness_vals) / len(smoothness_vals), 2)
        if smoothness_vals
        else 0.85
    )

    safety_alerts = sum(r.safety_alert_triggered for r in records)
    suspicious_patterns = sum(
        1 for r in records if r.safety_signal_pattern == "suspicious"
    )

    return {
        "has_data": True,
        "idle_minutes_total": round(total_idle, 1),
        "idle_minutes_recent": round(recent_idle, 1),
        "fuel_used_l": recent_tick.fuel_used_l,
        "load_cycles": recent_tick.load_cycles,
        "control_smoothness_avg": avg_smoothness,
        "seatbelt_status": recent_tick.seatbelt_status,
        "machine_moving": recent_tick.machine_moving,
        "machine_speed_kph": recent_tick.machine_speed_kph,
        "safety_alert_count": safety_alerts,
        "safety_signal_pattern": "suspicious" if suspicious_patterns > 0 else "normal",
        "tick_count": len(records),
        "latest_timestamp": recent_tick.timestamp,
    }


def get_mission_quality_observations(
    db: Session, mission_id: str
) -> List[QualityObservation]:
    """Retrieve chronological quality observations for a mission."""
    return (
        db.query(QualityObservation)
        .filter(QualityObservation.mission_id == mission_id)
        .order_by(QualityObservation.timestamp.asc())
        .all()
    )
