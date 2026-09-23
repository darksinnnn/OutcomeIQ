"""
API Router for Time Model Module.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.modules.time_model.schemas import (
    TimeModelEnvelope,
    TimeModelInput,
)
from backend.app.modules.time_model.service import (
    get_mission_time_prediction,
    predict_time_from_input,
    time_model_engine,
)

router = APIRouter(prefix="/api/time-model", tags=["Time Model"])


@router.get("/{mission_id}", response_model=TimeModelEnvelope)
def get_prediction(mission_id: str, db: Session = Depends(get_db)):
    """
    Get uncertainty-aware task duration distribution (P10/P50/P90) for a mission.
    """
    try:
        return get_mission_time_prediction(db, mission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/predict", response_model=TimeModelEnvelope)
def predict_custom(input_data: TimeModelInput, db: Session = Depends(get_db)):
    """
    Predict duration distribution for custom or counterfactual inputs.
    """
    try:
        return predict_time_from_input(db, input_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction error: {str(e)}",
        )


@router.get("/metrics/stats")
def get_model_stats(db: Session = Depends(get_db)):
    """
    Get training metrics (e.g. MAE) and model status for judges/inspectors.
    """
    if not time_model_engine.is_trained:
        time_model_engine.fit_from_db(db)
    return {
        "is_trained": time_model_engine.is_trained,
        "training_mae_min": round(time_model_engine.train_mae, 2),
        "quantiles_computed": ["P10", "P50", "P90"],
        "dataset": "causally_structured_synthetic",
    }
