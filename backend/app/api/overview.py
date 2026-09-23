"""
Overview and Composite Endpoints.

Provides list views (missions, operators, machines) and composite screen feeds
(Live Operation composite) without coupling module internals.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.database import get_db
from backend.app.db.models import Mission, Operator, Machine, Outcome, Zone
from backend.app.modules.mission_contract.service import get_existing_contract
from backend.app.modules.reality_engine.service import evaluate_mission_reality
from backend.app.modules.time_model.service import get_mission_time_prediction
from backend.app.modules.outcome_guardian.service import evaluate_outcome_guardian
from backend.app.modules._shared.operator_passport import get_all_operator_evidence
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.telemetry_stream import get_telemetry_window_summary

router = APIRouter(prefix="/api", tags=["Overview & Composite"])


@router.get("/missions")
def list_missions(
    limit: int = 50,
    scenario_only: bool = False,
    db: Session = Depends(get_db),
):
    """
    List missions with metadata, status, and scenario tags.
    """
    query = db.query(Mission)
    if scenario_only:
        query = query.filter(Mission.scenario_tag.isnot(None))
    missions = query.order_by(Mission.start_time.asc()).limit(limit).all()

    results = []
    for m in missions:
        results.append({
            "id": m.id,
            "project_id": m.project_id,
            "zone_id": m.zone_id,
            "task_type": m.task_type,
            "objective_quantity": m.objective_quantity,
            "objective_unit": m.objective_unit,
            "naive_estimated_time_min": m.naive_estimated_time_min,
            "deadline": m.deadline,
            "assigned_operator_id": m.assigned_operator_id,
            "assigned_machine_id": m.assigned_machine_id,
            "status": m.status,
            "scenario_tag": m.scenario_tag,
            "start_time": m.start_time,
        })
    return results


@router.get("/operators")
def list_operators(db: Session = Depends(get_db)):
    """List operators registered in the jobsite system."""
    ops = db.query(Operator).all()
    return [
        {
            "id": op.id,
            "name": op.name,
            "experience_years": op.experience_years,
            "certifications": op.certifications,
        }
        for op in ops
    ]


@router.get("/operators/{operator_id}/passport")
def get_operator_passport(operator_id: str, db: Session = Depends(get_db)):
    """
    Retrieve full Operator Passport evidence for an operator.
    Evidence-based demonstrated capability in context, NOT a surveillance score.
    """
    op = db.query(Operator).filter(Operator.id == operator_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operator not found")

    evidence_records = get_all_operator_evidence(db, operator_id)
    return {
        "operator": {
            "id": op.id,
            "name": op.name,
            "experience_years": op.experience_years,
        },
        "evidence_count": len(evidence_records),
        "evidence_records": evidence_records,
    }


@router.get("/machines")
def list_machines(db: Session = Depends(get_db)):
    """List fleet machines with their latest health condition."""
    machines = db.query(Machine).all()
    return [get_latest_machine_health(db, m.id) for m in machines]


@router.get("/composite/live-operation/{mission_id}")
def get_live_operation_composite(mission_id: str, db: Session = Depends(get_db)):
    """
    Composite endpoint powering the Live Operation dashboard screen.
    Combines Mission Contract, Reality Engine reasoning, Time Model prediction,
    Outcome Guardian assurance, and Telemetry window metrics in a single payload.
    """
    try:
        contract = get_existing_contract(db, mission_id)
        reality = evaluate_mission_reality(db, mission_id)
        time_pred = get_mission_time_prediction(db, mission_id)
        guardian = evaluate_outcome_guardian(db, mission_id)
        telemetry = get_telemetry_window_summary(db, mission_id)

        return {
            "mission_id": mission_id,
            "contract": contract,
            "reality_engine": reality,
            "time_model": time_pred,
            "outcome_guardian": guardian,
            "telemetry_window": telemetry,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
