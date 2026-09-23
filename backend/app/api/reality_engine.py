"""
API Router for Reality Engine Module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.reality_engine.schemas import RealityEngineEnvelope
from backend.app.modules.reality_engine.service import evaluate_mission_reality

router = APIRouter(prefix="/api/reality-engine", tags=["Reality Engine"])


@router.get("/{mission_id}", response_model=RealityEngineEnvelope)
def get_reality_evaluation(mission_id: str, db: Session = Depends(get_db)):
    """
    Perform multi-signal reasoning over live telemetry and workflow context for a mission.
    """
    try:
        return evaluate_mission_reality(db, mission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
