"""
Mission Contract service implementation.
Turns raw work order fields into a structured, validated target contract.
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.app.db.models import Mission, Project, Zone, Operator, Machine
from backend.app.modules.mission_contract.schemas import (
    MissionContractInput,
    MissionContractEnvelope,
    MissionContractValue,
    EvidenceItem,
)

NAIVE_BASE_MIN = {
    "Earth Excavation": 60.0,
    "Trenching": 45.0,
    "Material Loading": 30.0,
    "Grading": 35.0,
    "Demolition": 90.0,
}


def create_or_validate_contract(
    db: Session,
    input_data: MissionContractInput,
    mission_id: str = "CONTRACT-NEW",
    persist: bool = False,
) -> MissionContractEnvelope:
    """
    Validate work order parameters and compute baseline target contract.
    """
    evidence: List[EvidenceItem] = []
    confidence_penalties = 0.0

    # 1. Project & Zone validation
    project = db.query(Project).filter(Project.id == input_data.project_id).first()
    if not project:
        evidence.append(
            EvidenceItem(
                factor="project_reference",
                weight_or_probability=0.2,
                detail=f"Project {input_data.project_id} not found in database — defaulting to standard site parameters",
            )
        )
        confidence_penalties += 0.15
    else:
        evidence.append(
            EvidenceItem(
                factor="project_reference",
                weight_or_probability=0.9,
                detail=f"Project '{project.name}' verified with deadline {project.deadline}",
            )
        )

    zone = db.query(Zone).filter(Zone.id == input_data.zone_id).first()
    soil_desc = zone.soil_type if zone else "unspecified soil"
    evidence.append(
        EvidenceItem(
            factor="zone_parameters",
            weight_or_probability=0.85,
            detail=f"Zone '{input_data.zone_id}' validated ({soil_desc})",
        )
    )

    # 2. Operator validation
    op_info = None
    if input_data.assigned_operator_id:
        operator = (
            db.query(Operator)
            .filter(Operator.id == input_data.assigned_operator_id)
            .first()
        )
        if operator:
            op_info = {
                "id": operator.id,
                "name": operator.name,
                "experience_years": operator.experience_years,
            }
            evidence.append(
                EvidenceItem(
                    factor="operator_assignment",
                    weight_or_probability=0.95,
                    detail=f"Assigned operator {operator.name} ({operator.experience_years} yrs exp) validated",
                )
            )
        else:
            confidence_penalties += 0.2
            evidence.append(
                EvidenceItem(
                    factor="operator_assignment",
                    weight_or_probability=0.2,
                    detail=f"Operator ID {input_data.assigned_operator_id} not registered",
                )
            )

    # 3. Machine validation
    machine_info = None
    if input_data.assigned_machine_id:
        machine = (
            db.query(Machine)
            .filter(Machine.id == input_data.assigned_machine_id)
            .first()
        )
        if machine:
            machine_info = {
                "id": machine.id,
                "model": machine.model,
                "machine_family": machine.machine_family,
                "age_years": machine.age_years,
            }
            evidence.append(
                EvidenceItem(
                    factor="machine_assignment",
                    weight_or_probability=0.95,
                    detail=f"Machine {machine.model} ({machine.machine_family}, age {machine.age_years} yrs) allocated",
                )
            )
        else:
            confidence_penalties += 0.2
            evidence.append(
                EvidenceItem(
                    factor="machine_assignment",
                    weight_or_probability=0.2,
                    detail=f"Machine ID {input_data.assigned_machine_id} not found",
                )
            )

    # 4. Baseline targets
    base_time = NAIVE_BASE_MIN.get(input_data.task_type, 60.0)
    target_rate = (
        round(input_data.objective_quantity / (base_time / 60.0), 1)
        if base_time > 0
        else 0.0
    )

    evidence.append(
        EvidenceItem(
            factor="baseline_time_standard",
            weight_or_probability=0.8,
            detail=f"Standard task baseline: {base_time} min for {input_data.task_type} (Target rate: {target_rate} {input_data.objective_unit}/hr)",
        )
    )

    confidence = max(0.4, round(1.0 - confidence_penalties, 2))

    value = MissionContractValue(
        mission_id=mission_id,
        project_id=input_data.project_id,
        zone_id=input_data.zone_id,
        task_type=input_data.task_type,
        objective_quantity=input_data.objective_quantity,
        objective_unit=input_data.objective_unit,
        quality_tolerance_cm=input_data.quality_tolerance_cm or 5.0,
        deadline=input_data.deadline,
        naive_estimated_time_min=base_time,
        target_production_rate_unit_per_hour=target_rate,
        safety_constraints=input_data.safety_constraints or [],
        assigned_operator=op_info,
        assigned_machine=machine_info,
        resources_committed=input_data.resources or {},
        status="contract_active",
    )

    if persist:
        # Optionally persist into mission table
        new_mission = Mission(
            id=mission_id,
            project_id=input_data.project_id,
            zone_id=input_data.zone_id,
            task_type=input_data.task_type,
            objective_quantity=input_data.objective_quantity,
            objective_unit=input_data.objective_unit,
            quality_tolerance_cm=input_data.quality_tolerance_cm,
            deadline=input_data.deadline,
            safety_constraints=json.dumps(input_data.safety_constraints or []),
            assigned_operator_id=input_data.assigned_operator_id,
            assigned_machine_id=input_data.assigned_machine_id,
            resources=json.dumps(input_data.resources or {}),
            naive_estimated_time_min=base_time,
            start_time=input_data.start_time or datetime.utcnow().isoformat(),
            status="planned",
        )
        db.merge(new_mission)
        db.commit()

    return MissionContractEnvelope(
        value=value,
        confidence=confidence,
        evidence=evidence,
    )


def get_existing_contract(db: Session, mission_id: str) -> MissionContractEnvelope:
    """Retrieve contract for an existing mission in the database."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    safety_list = []
    if mission.safety_constraints:
        try:
            safety_list = json.loads(mission.safety_constraints)
        except Exception:
            safety_list = [mission.safety_constraints]

    resources_dict = {}
    if mission.resources:
        try:
            resources_dict = json.loads(mission.resources)
        except Exception:
            resources_dict = {}

    inp = MissionContractInput(
        project_id=mission.project_id,
        zone_id=mission.zone_id,
        task_type=mission.task_type,
        objective_quantity=mission.objective_quantity,
        objective_unit=mission.objective_unit,
        deadline=mission.deadline,
        quality_tolerance_cm=mission.quality_tolerance_cm,
        safety_constraints=safety_list,
        assigned_operator_id=mission.assigned_operator_id,
        assigned_machine_id=mission.assigned_machine_id,
        resources=resources_dict,
        start_time=mission.start_time,
    )

    return create_or_validate_contract(db, inp, mission_id=mission.id, persist=False)
