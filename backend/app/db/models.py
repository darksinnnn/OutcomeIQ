"""
SQLAlchemy ORM models for CAT OutcomeIQ.
Maps exactly to schema.sql and Architecture.md §3.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    ForeignKey,
    Text,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Project(Base):
    __tablename__ = "project"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    deadline = Column(String, nullable=False)  # ISO datetime
    target_quantity = Column(Float, nullable=True)
    quality_criteria = Column(Text, nullable=True)  # json

    zones = relationship("Zone", back_populates="project")
    missions = relationship("Mission", back_populates="project")


class Zone(Base):
    __tablename__ = "zone"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)
    name = Column(String, nullable=False)
    soil_type = Column(String, nullable=False)
    notes = Column(Text, nullable=True)

    project = relationship("Project", back_populates="zones")
    missions = relationship("Mission", back_populates="zone")


class Operator(Base):
    __tablename__ = "operator"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    experience_years = Column(Float, nullable=False)
    certifications = Column(Text, nullable=True)  # json list

    evidence = relationship("OperatorCapabilityEvidence", back_populates="operator")
    missions = relationship("Mission", back_populates="operator")


class OperatorCapabilityEvidence(Base):
    """
    Operator Passport evidence rows — capability demonstrated in context, not a score.
    """
    __tablename__ = "operator_capability_evidence"

    id = Column(String, primary_key=True)
    operator_id = Column(String, ForeignKey("operator.id"), nullable=False)
    task_type = Column(String, nullable=False)
    weather_bucket = Column(String, nullable=False)  # 'normal' | 'adverse'
    material = Column(String, nullable=True)
    sample_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    avg_time_delta_pct = Column(Float, nullable=True)
    avg_quality_success_pct = Column(Float, nullable=True)
    confidence = Column(Float, nullable=False, default=0.0)
    last_verified_at = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("operator_id", "task_type", "weather_bucket", "material", name="uq_operator_context"),
        Index("idx_evidence_operator", "operator_id", "task_type", "weather_bucket"),
    )

    operator = relationship("Operator", back_populates="evidence")


class Machine(Base):
    __tablename__ = "machine"

    id = Column(String, primary_key=True)
    model = Column(String, nullable=False)
    machine_family = Column(String, nullable=False)
    age_years = Column(Float, nullable=False)
    install_date = Column(String, nullable=False)

    health_records = relationship("MachineHealth", back_populates="machine")
    missions = relationship("Mission", back_populates="machine")


class MachineHealth(Base):
    __tablename__ = "machine_health"

    id = Column(String, primary_key=True)
    machine_id = Column(String, ForeignKey("machine.id"), nullable=False)
    engine_hours = Column(Float, nullable=False)
    health_pct = Column(Float, nullable=False)
    hydraulic_health_pct = Column(Float, nullable=False)
    recent_fault_count = Column(Integer, nullable=False, default=0)
    recorded_at = Column(String, nullable=False)

    machine = relationship("Machine", back_populates="health_records")


class Mission(Base):
    __tablename__ = "mission"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("project.id"), nullable=False)
    zone_id = Column(String, ForeignKey("zone.id"), nullable=False)
    task_type = Column(String, nullable=False)
    objective_quantity = Column(Float, nullable=False)
    objective_unit = Column(String, nullable=False, default="m3")
    quality_tolerance_cm = Column(Float, nullable=True)
    deadline = Column(String, nullable=False)
    safety_constraints = Column(Text, nullable=True)  # json list
    assigned_machine_id = Column(String, ForeignKey("machine.id"), nullable=True)
    assigned_operator_id = Column(String, ForeignKey("operator.id"), nullable=True)
    resources = Column(Text, nullable=True)  # json
    naive_estimated_time_min = Column(Float, nullable=True)
    start_time = Column(String, nullable=False)
    status = Column(String, nullable=False, default="planned")
    scenario_tag = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_mission_status", "status"),
    )

    project = relationship("Project", back_populates="missions")
    zone = relationship("Zone", back_populates="missions")
    machine = relationship("Machine", back_populates="missions")
    operator = relationship("Operator", back_populates="missions")

    environments = relationship("Environment", back_populates="mission")
    workflow_events = relationship("WorkflowEvent", back_populates="mission")
    telemetry = relationship("Telemetry", back_populates="mission")
    quality_observations = relationship("QualityObservation", back_populates="mission")
    outcome = relationship("Outcome", back_populates="mission", uselist=False)
    predictions = relationship("Prediction", back_populates="mission")
    root_cause_attributions = relationship("RootCauseAttribution", back_populates="mission")
    what_if_scenarios = relationship("WhatIfScenario", back_populates="mission")


class Environment(Base):
    __tablename__ = "environment"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    weather = Column(String, nullable=False)
    soil_moisture = Column(Float, nullable=False)
    visibility = Column(String, nullable=False)
    temperature_c = Column(Float, nullable=True)
    wind_kph = Column(Float, nullable=True)

    mission = relationship("Mission", back_populates="environments")


class WorkflowEvent(Base):
    __tablename__ = "workflow_event"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    timestamp = Column(String, nullable=False)
    truck_present = Column(Integer, nullable=False)  # 0 or 1
    truck_eta_min = Column(Float, nullable=True)
    queue_length = Column(Integer, nullable=False, default=0)
    material_available = Column(Integer, nullable=False, default=1)
    nearby_machine_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_workflow_mission_ts", "mission_id", "timestamp"),
    )

    mission = relationship("Mission", back_populates="workflow_events")


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    machine_id = Column(String, ForeignKey("machine.id"), nullable=False)
    operator_id = Column(String, ForeignKey("operator.id"), nullable=False)
    timestamp = Column(String, nullable=False)
    engine_hours = Column(Float, nullable=False)
    fuel_used_l = Column(Float, nullable=False)
    load_cycles = Column(Integer, nullable=False)
    idle_minutes = Column(Float, nullable=False)
    seatbelt_status = Column(String, nullable=False)
    occupancy_signal = Column(Integer, nullable=False, default=1)
    machine_speed_kph = Column(Float, nullable=False, default=0.0)
    machine_moving = Column(Integer, nullable=False, default=0)
    control_smoothness_score = Column(Float, nullable=True)
    safety_alert_triggered = Column(Integer, nullable=False, default=0)
    safety_signal_pattern = Column(String, nullable=True, default="normal")

    __table_args__ = (
        Index("idx_telemetry_mission_ts", "mission_id", "timestamp"),
    )

    mission = relationship("Mission", back_populates="telemetry")


class QualityObservation(Base):
    __tablename__ = "quality_observation"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    timestamp = Column(String, nullable=False)
    elevation_error_cm = Column(Float, nullable=False)
    pass_count = Column(Integer, nullable=False)
    surface_variance = Column(Float, nullable=False)

    __table_args__ = (
        Index("idx_quality_mission_ts", "mission_id", "timestamp"),
    )

    mission = relationship("Mission", back_populates="quality_observations")


class Outcome(Base):
    """
    Ground truth outcome — used for evaluation and passport updates ONLY.
    NEVER fed into feature vectors at prediction time.
    """
    __tablename__ = "outcome"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False, unique=True)
    actual_duration_min = Column(Float, nullable=False)
    actual_fuel_l = Column(Float, nullable=False)
    quantity_completed = Column(Float, nullable=False)
    quality_score = Column(Float, nullable=False)
    rework_flag = Column(Integer, nullable=False, default=0)
    safety_event_count = Column(Integer, nullable=False, default=0)
    delay_reason = Column(String, nullable=True)

    mission = relationship("Mission", back_populates="outcome")


class Prediction(Base):
    """
    Uniform envelope for module outputs (Architecture.md §4).
    """
    __tablename__ = "prediction"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    module_name = Column(String, nullable=False)
    generated_at = Column(String, nullable=False)
    value = Column(Text, nullable=False)  # json
    confidence = Column(Float, nullable=False)
    evidence = Column(Text, nullable=False)  # json list

    __table_args__ = (
        Index("idx_prediction_mission_module", "mission_id", "module_name"),
    )

    mission = relationship("Mission", back_populates="predictions")


class RootCauseAttribution(Base):
    __tablename__ = "root_cause_attribution"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    generated_at = Column(String, nullable=False)
    deviation_min = Column(Float, nullable=False)
    contributors = Column(Text, nullable=False)  # json list

    mission = relationship("Mission", back_populates="root_cause_attributions")


class WhatIfScenario(Base):
    __tablename__ = "what_if_scenario"

    id = Column(String, primary_key=True)
    mission_id = Column(String, ForeignKey("mission.id"), nullable=False)
    generated_at = Column(String, nullable=False)
    assumption_changed = Column(Text, nullable=False)  # json
    predicted_before = Column(Text, nullable=False)  # json
    predicted_after = Column(Text, nullable=False)  # json

    mission = relationship("Mission", back_populates="what_if_scenarios")
