"""
API Router for What-If Lab Module.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.what_if.schemas import WhatIfRequest, WhatIfEnvelope
from backend.app.modules.what_if.service import simulate_what_if

router = APIRouter(prefix="/api/what-if", tags=["What-If Lab"])


@router.post("", response_model=WhatIfEnvelope)
@router.post("/simulate", response_model=WhatIfEnvelope)
def run_what_if_simulation(
    request: WhatIfRequest,
    db: Session = Depends(get_db),
):
    """
    Run counterfactual decision simulation (e.g. add a truck, change operator, modify weather).
    """
    try:
        return simulate_what_if(db, request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation failed: {str(e)}",
        )


@router.get("/scenario-presets/{mission_id}")
def get_scenario_presets(mission_id: str, db: Session = Depends(get_db)):
    """
    Get recommended operational intervention options for a mission.
    """
    return {
        "mission_id": mission_id,
        "presets": [
            {
                "id": "add_truck",
                "label": "Add Haul Truck (+1 unit)",
                "description": "Resolve queue bottlenecks and eliminate idle wait cycles",
                "assumptions": {"add_truck": True},
            },
            {
                "id": "reassign_experienced_lead",
                "label": "Reassign to Lead Operator (OP-1001)",
                "description": "Deploy operator with high verified evidence in this context",
                "assumptions": {"operator_id": "OP-1001"},
            },
            {
                "id": "favorable_weather",
                "label": "Weather Clears (Sunny, 15% moisture)",
                "description": "Evaluate baseline trajectory assuming ground dryness",
                "assumptions": {"weather": "Sunny", "soil_moisture": 0.15},
            },
        ],
    }
