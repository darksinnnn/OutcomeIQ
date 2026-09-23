"""
Machine Memory — Persistent Machine Health and Degradation Store.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.db.models import Machine, MachineHealth


def get_machine(db: Session, machine_id: str) -> Optional[Machine]:
    """Retrieve machine metadata."""
    return db.query(Machine).filter(Machine.id == machine_id).first()


def get_latest_machine_health(db: Session, machine_id: str) -> Dict[str, Any]:
    """
    Retrieve latest recorded health condition for a machine.
    """
    machine = get_machine(db, machine_id)
    if not machine:
        return {
            "machine_id": machine_id,
            "found": False,
            "health_pct": 85.0,
            "hydraulic_health_pct": 85.0,
            "engine_hours": 1000.0,
            "recent_fault_count": 0,
        }

    health = (
        db.query(MachineHealth)
        .filter(MachineHealth.machine_id == machine_id)
        .order_by(desc(MachineHealth.recorded_at))
        .first()
    )

    if not health:
        return {
            "machine_id": machine_id,
            "model": machine.model,
            "machine_family": machine.machine_family,
            "age_years": machine.age_years,
            "health_pct": 90.0,
            "hydraulic_health_pct": 90.0,
            "engine_hours": 500.0,
            "recent_fault_count": 0,
            "recorded_at": None,
        }

    return {
        "machine_id": machine_id,
        "model": machine.model,
        "machine_family": machine.machine_family,
        "age_years": machine.age_years,
        "health_pct": health.health_pct,
        "hydraulic_health_pct": health.hydraulic_health_pct,
        "engine_hours": health.engine_hours,
        "recent_fault_count": health.recent_fault_count,
        "recorded_at": health.recorded_at,
    }
