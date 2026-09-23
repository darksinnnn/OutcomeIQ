"""
Time Model Service — Gradient-Boosted Quantile Regression.

Predicts task duration as an uncertainty-aware P10 / P50 / P90 distribution,
plus expected fuel range and feature attribution evidence.

LEAKAGE RULE (Architecture.md §4 & §5):
NEVER include any 'outcome' table field in feature extraction.
Only pre-mission and mission-start data are permitted.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sqlalchemy.orm import Session

from backend.app.db.models import (
    Mission,
    Outcome,
    Environment,
    WorkflowEvent,
    Machine,
    MachineHealth,
    OperatorCapabilityEvidence,
)
from backend.app.modules._shared.operator_passport import get_context_evidence
from backend.app.modules._shared.machine_memory import get_latest_machine_health
from backend.app.modules._shared.jobsite_memory import (
    get_mission_environment,
    get_latest_workflow_state,
)
from backend.app.modules.time_model.schemas import (
    TimeModelEnvelope,
    TimeModelPredictionValue,
    FeatureAttribution,
    TimeModelInput,
)

TASK_TYPES = ["Earth Excavation", "Trenching", "Material Loading", "Grading", "Demolition"]
NAIVE_BASE_MIN = {
    "Earth Excavation": 60.0,
    "Trenching": 45.0,
    "Material Loading": 30.0,
    "Grading": 35.0,
    "Demolition": 90.0,
}

FEATURE_NAMES = [
    "task_Earth_Excavation",
    "task_Trenching",
    "task_Material_Loading",
    "task_Grading",
    "task_Demolition",
    "objective_quantity",
    "naive_base_min",
    "operator_confidence",
    "operator_sample_count",
    "machine_health_pct",
    "machine_hydraulic_pct",
    "machine_age_years",
    "soil_moisture",
    "weather_adverse",
    "truck_present",
    "truck_eta_min",
    "queue_length",
]


class TimeModelEngine:
    """
    Trained Quantile Regressors for P10, P50, P90 duration and Fuel consumption.
    """

    def __init__(self):
        self.model_p10 = GradientBoostingRegressor(loss="quantile", alpha=0.10, n_estimators=60, max_depth=3, random_state=42)
        self.model_p50 = GradientBoostingRegressor(loss="quantile", alpha=0.50, n_estimators=60, max_depth=3, random_state=42)
        self.model_p90 = GradientBoostingRegressor(loss="quantile", alpha=0.90, n_estimators=60, max_depth=3, random_state=42)
        self.model_fuel = GradientBoostingRegressor(loss="squared_error", n_estimators=60, max_depth=3, random_state=42)
        self.is_trained = False
        self.train_mae = 0.0

    def fit_from_db(self, db: Session):
        """Train models using historical missions in SQLite database."""
        missions = (
            db.query(Mission)
            .join(Outcome, Outcome.mission_id == Mission.id)
            .filter(Mission.status == "complete")
            .all()
        )
        if len(missions) < 20:
            return

        X_rows = []
        y_duration = []
        y_fuel = []

        for m in missions:
            # Strictly pre-mission / mission-start features
            feat = self.extract_features_for_mission(db, m)
            X_rows.append(feat)
            y_duration.append(m.outcome.actual_duration_min)
            y_fuel.append(m.outcome.actual_fuel_l)

        X = np.array(X_rows)
        y_d = np.array(y_duration)
        y_f = np.array(y_fuel)

        self.model_p10.fit(X, y_d)
        self.model_p50.fit(X, y_d)
        self.model_p90.fit(X, y_d)
        self.model_fuel.fit(X, y_f)

        pred_p50 = self.model_p50.predict(X)
        self.train_mae = float(np.mean(np.abs(pred_p50 - y_d)))
        self.is_trained = True

    def extract_features_for_mission(self, db: Session, mission: Mission) -> List[float]:
        """Extract clean non-leaking feature vector for a mission."""
        env = get_mission_environment(db, mission.id)
        workflow = get_latest_workflow_state(db, mission.id)
        m_health = get_latest_machine_health(db, mission.assigned_machine_id or "")
        op_ev = get_context_evidence(
            db,
            operator_id=mission.assigned_operator_id or "",
            task_type=mission.task_type,
            weather_bucket=env["weather_bucket"],
        )

        return self.vectorize_features(
            task_type=mission.task_type,
            objective_quantity=mission.objective_quantity,
            operator_confidence=op_ev["confidence"],
            operator_sample_count=op_ev["sample_count"],
            machine_health_pct=m_health["health_pct"],
            machine_hydraulic_pct=m_health["hydraulic_health_pct"],
            machine_age_years=m_health.get("age_years", 3.0),
            soil_moisture=env["soil_moisture"],
            weather_adverse=1 if env["weather_bucket"] == "adverse" else 0,
            truck_present=workflow["truck_present"],
            truck_eta_min=workflow["truck_eta_min"],
            queue_length=workflow["queue_length"],
        )

    def vectorize_features(
        self,
        task_type: str,
        objective_quantity: float,
        operator_confidence: float,
        operator_sample_count: int,
        machine_health_pct: float,
        machine_hydraulic_pct: float,
        machine_age_years: float,
        soil_moisture: float,
        weather_adverse: int,
        truck_present: int,
        truck_eta_min: float,
        queue_length: int,
    ) -> List[float]:
        """Convert scalar features into numerical vector."""
        naive_base = NAIVE_BASE_MIN.get(task_type, 60.0)

        one_hot_task = [1.0 if task_type == t else 0.0 for t in TASK_TYPES]

        features = one_hot_task + [
            float(objective_quantity),
            float(naive_base),
            float(operator_confidence),
            float(operator_sample_count),
            float(machine_health_pct),
            float(machine_hydraulic_pct),
            float(machine_age_years),
            float(soil_moisture),
            float(weather_adverse),
            float(truck_present),
            float(truck_eta_min),
            float(queue_length),
        ]
        return features

    def predict_vector(
        self,
        feature_vector: List[float],
        mission_id: Optional[str] = None,
        task_type: str = "Earth Excavation",
    ) -> TimeModelEnvelope:
        """Run quantile inference over vectorized features."""
        X = np.array([feature_vector])
        naive_base = NAIVE_BASE_MIN.get(task_type, 60.0)

        if not self.is_trained:
            # Analytical baseline fallback
            p50 = naive_base * 1.15
            p10 = p50 * 0.9
            p90 = p50 * 1.25
            fuel = naive_base * 0.4
        else:
            p10 = float(self.model_p10.predict(X)[0])
            p50 = float(self.model_p50.predict(X)[0])
            p90 = float(self.model_p90.predict(X)[0])
            fuel = float(self.model_fuel.predict(X)[0])

        # Enforce quantile monotonicity
        p10 = max(10.0, p10)
        p50 = max(p10 + 1.0, p50)
        p90 = max(p50 + 1.0, p90)

        uncertainty_spread = p90 - p10
        relative_spread = uncertainty_spread / p50
        # Confidence formula: narrower spread = higher confidence
        confidence = round(max(0.2, min(0.96, 1.0 / (1.0 + relative_spread * 1.2))), 2)

        # Feature Attribution Evidence
        evidence = self._generate_evidence(feature_vector, p50, naive_base)

        value = TimeModelPredictionValue(
            mission_id=mission_id,
            p10_min=round(p10, 1),
            p50_min=round(p50, 1),
            p90_min=round(p90, 1),
            p10_duration_min=round(p10, 1),
            p50_duration_min=round(p50, 1),
            p90_duration_min=round(p90, 1),
            uncertainty_spread_min=round(uncertainty_spread, 1),
            naive_estimated_time_min=round(naive_base, 1),
            expected_duration_delta_min=round(p50 - naive_base, 1),
            expected_fuel_l=round(fuel, 1),
            expected_fuel_range_l={
                "min": round(fuel * 0.88, 1),
                "max": round(fuel * 1.15, 1),
            },
        )

        return TimeModelEnvelope(
            value=value,
            confidence=confidence,
            evidence=evidence,
        )

    def _generate_evidence(
        self, feat: List[float], p50: float, naive_base: float
    ) -> List[FeatureAttribution]:
        """Decompose contributing factors driving difference from naive baseline."""
        evidence: List[FeatureAttribution] = []

        # Feature index map
        # 5: objective_quantity, 7: operator_confidence, 9: machine_health_pct,
        # 12: soil_moisture, 14: truck_present, 15: truck_eta_min
        op_conf = feat[7]
        m_health = feat[9]
        m_hydraulic = feat[10]
        soil_m = feat[12]
        truck_pres = feat[14]
        truck_eta = feat[15]

        # 1. Truck availability attribution
        if truck_pres == 0 or truck_eta > 5:
            impact = max(5.0, truck_eta)
            evidence.append(
                FeatureAttribution(
                    factor="workflow_truck_bottleneck",
                    impact_min=round(impact, 1),
                    weight_or_probability=0.88,
                    detail=f"Truck unavailable at dispatch (estimated delay: {round(truck_eta, 1)} min queueing)",
                )
            )
        else:
            evidence.append(
                FeatureAttribution(
                    factor="workflow_truck_present",
                    impact_min=0.0,
                    weight_or_probability=0.80,
                    detail="Continuous truck presence confirmed at loading zone",
                )
            )

        # 2. Environmental soil moisture attribution
        if soil_m > 0.4:
            impact = (soil_m - 0.2) * 20.0
            evidence.append(
                FeatureAttribution(
                    factor="environmental_soil_moisture",
                    impact_min=round(impact, 1),
                    weight_or_probability=round(min(0.9, 0.5 + soil_m * 0.4), 2),
                    detail=f"Elevated soil moisture ({round(soil_m*100, 1)}%) increases hydraulic bucket resistance",
                )
            )

        # 3. Operator context evidence
        if op_conf < 0.3:
            impact = max(3.0, (0.5 - op_conf) * 22.0)
            evidence.append(
                FeatureAttribution(
                    factor="operator_context_experience",
                    impact_min=round(impact, 1),
                    weight_or_probability=0.75,
                    detail=f"Limited historical operator sample in this context (confidence {round(op_conf*100, 1)}%)",
                )
            )
        else:
            evidence.append(
                FeatureAttribution(
                    factor="operator_context_experience",
                    impact_min=-3.0,
                    weight_or_probability=round(op_conf, 2),
                    detail=f"Demonstrated competence in comparable missions (confidence {round(op_conf*100, 1)}%)",
                )
            )

        # 4. Machine condition
        if m_health < 80.0 or m_hydraulic < 80.0:
            impact = max(2.0, (85.0 - m_health) * 0.4)
            evidence.append(
                FeatureAttribution(
                    factor="machine_hydraulic_degradation",
                    impact_min=round(impact, 1),
                    weight_or_probability=0.70,
                    detail=f"Hydraulic efficiency index ({round(m_hydraulic, 1)}%) suggests increased cycle times",
                )
            )

        return evidence


# Singleton engine instance
time_model_engine = TimeModelEngine()


def get_mission_time_prediction(db: Session, mission_id: str) -> TimeModelEnvelope:
    """Predict task duration distribution for a seeded mission."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise ValueError(f"Mission '{mission_id}' not found")

    if not time_model_engine.is_trained:
        time_model_engine.fit_from_db(db)

    features = time_model_engine.extract_features_for_mission(db, mission)
    return time_model_engine.predict_vector(
        features, mission_id=mission.id, task_type=mission.task_type
    )


def predict_time_from_input(db: Session, input_data: TimeModelInput) -> TimeModelEnvelope:
    """Predict task duration for arbitrary counterfactual or custom inputs."""
    if not time_model_engine.is_trained:
        time_model_engine.fit_from_db(db)

    # Resolve operator evidence if provided
    op_conf = 0.5
    op_samples = 10
    if input_data.operator_id:
        adverse = input_data.weather in ("Rainy", "Windy")
        ev = get_context_evidence(
            db,
            input_data.operator_id,
            input_data.task_type,
            "adverse" if adverse else "normal",
        )
        op_conf = ev["confidence"]
        op_samples = ev["sample_count"]

    # Resolve machine health if provided
    m_health = 90.0
    m_hyd = 90.0
    m_age = 2.0
    if input_data.machine_id:
        mh = get_latest_machine_health(db, input_data.machine_id)
        m_health = mh["health_pct"]
        m_hyd = mh["hydraulic_health_pct"]
        m_age = mh.get("age_years", 2.0)

    weather_adverse = 1 if input_data.weather in ("Rainy", "Windy") else 0
    truck_present = 1 if input_data.truck_present else 0

    features = time_model_engine.vectorize_features(
        task_type=input_data.task_type,
        objective_quantity=input_data.objective_quantity,
        operator_confidence=op_conf,
        operator_sample_count=op_samples,
        machine_health_pct=m_health,
        machine_hydraulic_pct=m_hyd,
        machine_age_years=m_age,
        soil_moisture=input_data.soil_moisture or 0.2,
        weather_adverse=weather_adverse,
        truck_present=truck_present,
        truck_eta_min=input_data.truck_eta_min or 0.0,
        queue_length=input_data.queue_length or 0,
    )

    return time_model_engine.predict_vector(
        features, mission_id=None, task_type=input_data.task_type
    )
