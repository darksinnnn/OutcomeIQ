"""
API Router for Outcome Guardian Module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.outcome_guardian.schemas import OutcomeGuardianEnvelope
from backend.app.modules.outcome_guardian.service import evaluate_outcome_guardian

router = APIRouter(prefix="/api/outcome-guardian", tags=["Outcome Guardian"])


@router.get("/{mission_id}", response_model=OutcomeGuardianEnvelope)
def get_mission_outcome_guardian(mission_id: str, db: Session = Depends(get_db)):
    """
    Get 6-signal assurance state (Time, Safety, Productivity, Fuel, Quality, Acceptance)
    and rework risk assessment for a mission.
    """
    try:
        return evaluate_outcome_guardian(db, mission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
