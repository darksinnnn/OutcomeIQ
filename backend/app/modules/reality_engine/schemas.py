"""
Schemas for Reality Engine Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RealityEvidenceItem(BaseModel):
    factor: str
    weight_or_probability: float
    detail: str


class RealityEngineValue(BaseModel):
    mission_id: str
    explanation_class: str = Field(
        ...,
        description="external_workflow | operator_variation | machine_condition | weather_condition | unknown",
    )
    headline: str
    anomaly_detected: bool
    idle_minutes_recent: float
    idle_minutes_total: float
    primary_driver: str
    recommended_focus: str
    signal_summary: Dict[str, Any]


class RealityEngineEnvelope(BaseModel):
    value: RealityEngineValue
    confidence: float
    evidence: List[RealityEvidenceItem]
