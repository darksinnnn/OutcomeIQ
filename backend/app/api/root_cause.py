"""
API Router for Root Cause Engine Module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.root_cause.schemas import RootCauseEnvelope
from backend.app.modules.root_cause.service import decompose_root_cause

router = APIRouter(prefix="/api/root-cause", tags=["Root Cause Engine"])


@router.get("/{mission_id}", response_model=RootCauseEnvelope)
def get_root_cause_attribution(mission_id: str, db: Session = Depends(get_db)):
    """
    Decompose task duration deviation into ranked root-cause contributors with evidence.
    """
    try:
        return decompose_root_cause(db, mission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
