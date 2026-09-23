"""
Schemas for Time Model Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TimeModelPredictionValue(BaseModel):
    mission_id: Optional[str] = None
    p10_min: float
    p50_min: float
    p90_min: float
    p10_duration_min: float
    p50_duration_min: float
    p90_duration_min: float
    uncertainty_spread_min: float
    naive_estimated_time_min: float
    expected_duration_delta_min: float  # P50 - naive
    expected_fuel_l: float
    expected_fuel_range_l: Dict[str, float]  # {"min": ..., "max": ...}


class FeatureAttribution(BaseModel):
    factor: str
    impact_min: float  # Estimated directional impact on duration
    weight_or_probability: float
    detail: str


class TimeModelEnvelope(BaseModel):
    value: TimeModelPredictionValue
    confidence: float  # 0.0 to 1.0 (inverse of relative uncertainty)
    evidence: List[FeatureAttribution]


class TimeModelInput(BaseModel):
    task_type: str
    objective_quantity: float
    operator_id: Optional[str] = None
    machine_id: Optional[str] = None
    weather: Optional[str] = "Sunny"
    soil_moisture: Optional[float] = 0.2
    truck_present: Optional[bool] = True
    truck_eta_min: Optional[float] = 0.0
    queue_length: Optional[int] = 0
