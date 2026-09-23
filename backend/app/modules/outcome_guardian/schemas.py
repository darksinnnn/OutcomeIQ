"""
Schemas for Outcome Guardian Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SignalState(BaseModel):
    status: str = Field(..., description="green | amber | red")
    score: float = Field(..., ge=0.0, le=1.0)
    summary: str


class OutcomeGuardianValue(BaseModel):
    mission_id: str
    overall_status: str = Field(..., description="green | amber | red")
    headline: str
    time: str = Field(..., description="green | amber | red")
    safety: str = Field(..., description="green | amber | red")
    productivity: str = Field(..., description="green | amber | red")
    fuel: str = Field(..., description="green | amber | red")
    quality: str = Field(..., description="green | amber | red")
    acceptance: str = Field(..., description="green | amber | red")
    rework_probability: float = Field(..., ge=0.0, le=1.0)
    acceptance_risk_level: str = Field(..., description="low | moderate | high | critical")
    signals: Dict[str, SignalState] = Field(
        ...,
        description="Keys: time, safety, productivity, fuel, quality, acceptance",
    )
    quality_metrics: Dict[str, Any]


class OutcomeGuardianEvidence(BaseModel):
    factor: str
    weight_or_probability: float
    detail: str


class OutcomeGuardianEnvelope(BaseModel):
    value: OutcomeGuardianValue
    confidence: float
    evidence: List[OutcomeGuardianEvidence]
