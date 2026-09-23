"""
API Router for Mission Contract Module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.mission_contract.schemas import (
    MissionContractInput,
    MissionContractEnvelope,
)
from backend.app.modules.mission_contract.service import (
    create_or_validate_contract,
    get_existing_contract,
)

router = APIRouter(prefix="/api/mission-contract", tags=["Mission Contract"])


@router.post("/validate", response_model=MissionContractEnvelope)
def validate_contract(
    input_data: MissionContractInput,
    persist: bool = False,
    db: Session = Depends(get_db),
):
    """
    Validate a work order into a structured mission contract with baseline targets.
    """
    try:
        return create_or_validate_contract(db, input_data, persist=persist)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate contract: {str(e)}",
        )


@router.get("/{mission_id}", response_model=MissionContractEnvelope)
def get_contract(
    mission_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieve contract representation for a seeded or recorded mission.
    """
    try:
        return get_existing_contract(db, mission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
