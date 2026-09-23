"""
Jobsite Memory — Zone, Environment, and Workflow Event Store.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.db.models import Mission, Zone, Environment, WorkflowEvent


def get_mission(db: Session, mission_id: str) -> Optional[Mission]:
    """Retrieve mission by ID."""
    return db.query(Mission).filter(Mission.id == mission_id).first()


def get_zone(db: Session, zone_id: str) -> Optional[Zone]:
    """Retrieve zone by ID."""
    return db.query(Zone).filter(Zone.id == zone_id).first()


def get_mission_environment(db: Session, mission_id: str) -> Dict[str, Any]:
    """Retrieve environmental conditions for a mission."""
    env = db.query(Environment).filter(Environment.mission_id == mission_id).first()
    if not env:
        return {
            "weather": "Sunny",
            "soil_moisture": 0.15,
            "visibility": "good",
            "temperature_c": 22.0,
            "wind_kph": 5.0,
            "weather_bucket": "normal",
        }
    
    adverse = env.weather in ("Rainy", "Windy")
    return {
        "weather": env.weather,
        "soil_moisture": env.soil_moisture,
        "visibility": env.visibility,
        "temperature_c": env.temperature_c,
        "wind_kph": env.wind_kph,
        "weather_bucket": "adverse" if adverse else "normal",
    }


def get_latest_workflow_state(db: Session, mission_id: str) -> Dict[str, Any]:
    """Retrieve latest workflow event (truck presence, queue length, etc.)."""
    event = (
        db.query(WorkflowEvent)
        .filter(WorkflowEvent.mission_id == mission_id)
        .order_by(desc(WorkflowEvent.timestamp))
        .first()
    )
    if not event:
        return {
            "truck_present": 1,
            "truck_eta_min": 0.0,
            "queue_length": 0,
            "material_available": 1,
            "nearby_machine_count": 0,
            "has_workflow_data": False,
        }
    
    return {
        "truck_present": event.truck_present,
        "truck_eta_min": event.truck_eta_min or 0.0,
        "queue_length": event.queue_length,
        "material_available": event.material_available,
        "nearby_machine_count": event.nearby_machine_count,
        "timestamp": event.timestamp,
        "has_workflow_data": True,
    }


def get_all_workflow_events(db: Session, mission_id: str) -> List[WorkflowEvent]:
    """Retrieve chronological workflow events for a mission."""
    return (
        db.query(WorkflowEvent)
        .filter(WorkflowEvent.mission_id == mission_id)
        .order_by(WorkflowEvent.timestamp.asc())
        .all()
    )
