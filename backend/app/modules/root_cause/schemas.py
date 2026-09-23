"""
Schemas for Root Cause Engine Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Contributor(BaseModel):
    cause: str = Field(..., description="truck | weather | operator | machine | unknown")
    probability: float = Field(..., ge=0.0, le=1.0)
    delay_impact_min: float
    evidence: str


class RootCauseValue(BaseModel):
    mission_id: str
    deviation_min: float
    predicted_p50_min: float
    actual_or_projected_min: float
    primary_cause: str
    contributors: List[Contributor]
    diagnostic_summary: str


class RootCauseEnvelope(BaseModel):
    value: RootCauseValue
    confidence: float
    evidence: List[Dict[str, Any]]
