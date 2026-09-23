"""
Schemas for Mission Contract Module.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MissionContractInput(BaseModel):
    project_id: str
    zone_id: str
    task_type: str
    objective_quantity: float = Field(gt=0, description="Target volume or unit")
    objective_unit: str = "m3"
    deadline: str  # ISO string
    quality_tolerance_cm: Optional[float] = 5.0
    safety_constraints: Optional[List[str]] = Field(default_factory=list)
    assigned_operator_id: Optional[str] = None
    assigned_machine_id: Optional[str] = None
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)
    start_time: Optional[str] = None


class EvidenceItem(BaseModel):
    factor: str
    weight_or_probability: float
    detail: str


class MissionContractValue(BaseModel):
    mission_id: str
    project_id: str
    zone_id: str
    task_type: str
    objective_quantity: float
    objective_unit: str
    quality_tolerance_cm: float
    deadline: str
    naive_estimated_time_min: float
    target_production_rate_unit_per_hour: float
    safety_constraints: List[str]
    assigned_operator: Optional[Dict[str, Any]] = None
    assigned_machine: Optional[Dict[str, Any]] = None
    resources_committed: Dict[str, Any]
    status: str


class MissionContractEnvelope(BaseModel):
    value: MissionContractValue
    confidence: float
    evidence: List[EvidenceItem]
