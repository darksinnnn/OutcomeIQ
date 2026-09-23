"""
Schemas for What-If Lab Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.app.modules.time_model.schemas import TimeModelPredictionValue
from backend.app.modules.outcome_guardian.schemas import OutcomeGuardianValue


class WhatIfRequest(BaseModel):
    mission_id: str
    assumption_changed: Dict[str, Any] = Field(
        ...,
        description="Key modifications, e.g. {'add_truck': True}, {'operator_id': 'OP-1002'}, {'weather': 'Sunny'}",
    )


class WhatIfDelta(BaseModel):
    time_recovered_min: float = Field(..., description="Positive value means task finishes faster")
    p50_before_min: float
    p50_after_min: float
    fuel_delta_l: float
    rework_risk_delta_pct: float
    operational_efficiency_gain_pct: float


class WhatIfValue(BaseModel):
    mission_id: str
    assumption_changed: Dict[str, Any]
    before: TimeModelPredictionValue
    after: TimeModelPredictionValue
    predicted_before: TimeModelPredictionValue
    predicted_after: TimeModelPredictionValue
    guardian_before: Optional[OutcomeGuardianValue] = None
    guardian_after: Optional[OutcomeGuardianValue] = None
    delta: WhatIfDelta
    recommendation: str


class WhatIfEvidence(BaseModel):
    factor: str
    weight_or_probability: float
    detail: str


class WhatIfEnvelope(BaseModel):
    value: WhatIfValue
    confidence: float
    evidence: List[WhatIfEvidence]
