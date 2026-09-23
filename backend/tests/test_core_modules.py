"""
Comprehensive tests for the Core 4 Modules:
- Mission Contract
- Time Model
- Reality Engine
- Root-Cause Engine
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Mission Contract Tests
# ---------------------------------------------------------------------------

def test_mission_contract_get():
    response = client.get("/api/mission-contract/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    data = response.json()
    assert "value" in data
    assert "confidence" in data
    assert "evidence" in data
    assert data["value"]["task_type"] == "Trenching"
    assert data["value"]["naive_estimated_time_min"] == 45.0
    assert len(data["evidence"]) >= 3


def test_mission_contract_validate():
    payload = {
        "project_id": "PRJ-001",
        "zone_id": "ZONE-A",
        "task_type": "Earth Excavation",
        "objective_quantity": 450.0,
        "objective_unit": "m3",
        "deadline": "2026-12-31T18:00:00",
        "quality_tolerance_cm": 5.0,
        "safety_constraints": ["no_entry_zone_c"],
        "assigned_operator_id": "OP-1001",
        "assigned_machine_id": "EXC-100",
    }
    response = client.post("/api/mission-contract/validate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["value"]["task_type"] == "Earth Excavation"
    assert data["value"]["naive_estimated_time_min"] == 60.0
    assert data["confidence"] >= 0.8
    assert len(data["evidence"]) >= 3


# ---------------------------------------------------------------------------
# 2. Time Model Tests
# ---------------------------------------------------------------------------

def test_time_model_prediction():
    response = client.get("/api/time-model/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    data = response.json()

    val = data["value"]
    p10 = val["p10_duration_min"]
    p50 = val["p50_duration_min"]
    p90 = val["p90_duration_min"]

    # Monotonic quantile check
    assert p10 <= p50 <= p90, f"Expected P10 <= P50 <= P90, got {p10}, {p50}, {p90}"
    assert data["confidence"] > 0.0 and data["confidence"] <= 1.0
    assert "expected_fuel_l" in val
    assert len(data["evidence"]) >= 2


def test_time_model_custom_prediction():
    payload = {
        "task_type": "Grading",
        "objective_quantity": 250.0,
        "weather": "Sunny",
        "soil_moisture": 0.15,
        "truck_present": True,
    }
    response = client.post("/api/time-model/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    val = data["value"]
    assert val["p10_duration_min"] <= val["p50_duration_min"] <= val["p90_duration_min"]


# ---------------------------------------------------------------------------
# 3. Reality Engine Tests
# ---------------------------------------------------------------------------

def test_reality_engine_false_idle_scenario():
    """
    Scenario 1: False-idle. Truck is absent, operator is normal.
    Must classify as 'external_workflow', NOT blame operator.
    """
    response = client.get("/api/reality-engine/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    data = response.json()
    val = data["value"]

    assert val["explanation_class"] == "external_workflow", (
        f"Expected 'external_workflow', got '{val['explanation_class']}'"
    )
    assert val["anomaly_detected"] is True
    assert "truck" in val["primary_driver"].lower()

    # Verify Trust & Safety language in headline and evidence
    banned = ["lazy", "fatigued", "dangerous", "inefficient"]
    for word in banned:
        assert word not in val["headline"].lower()
        for ev in data["evidence"]:
            assert word not in ev["detail"].lower()


def test_reality_engine_operator_context_mismatch_scenario():
    """
    Scenario 2: Operator context mismatch.
    Must identify 'operator_variation' due to unfamiliar context without insulting the operator.
    """
    response = client.get("/api/reality-engine/MISSION-OPERATOR-CONTEXT-MISMATCH")
    assert response.status_code == 200
    data = response.json()
    val = data["value"]

    assert val["explanation_class"] == "operator_variation"
    # Ensure evidence-based framing
    assert "unfamiliar" in val["headline"].lower() or "performance deviation" in val["headline"].lower()


# ---------------------------------------------------------------------------
# 4. Root-Cause Engine Tests
# ---------------------------------------------------------------------------

def test_root_cause_false_idle_scenario():
    """
    In FALSE_IDLE, truck bottleneck must be ranked as primary cause.
    """
    response = client.get("/api/root-cause/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    data = response.json()
    val = data["value"]

    assert val["primary_cause"] == "truck"
    top_contributor = val["contributors"][0]
    assert top_contributor["cause"] == "truck"
    assert top_contributor["probability"] > 0.40

    # Ensure total probability sums to ~1.0
    total_prob = sum(c["probability"] for c in val["contributors"])
    assert abs(total_prob - 1.0) < 0.05


def test_root_cause_operator_context_scenario():
    """
    In OPERATOR_CONTEXT_MISMATCH, operator context is top contributor.
    """
    response = client.get("/api/root-cause/MISSION-OPERATOR-CONTEXT-MISMATCH")
    assert response.status_code == 200
    data = response.json()
    val = data["value"]

    assert val["primary_cause"] == "operator"
    top_contributor = val["contributors"][0]
    assert top_contributor["cause"] == "operator"
    assert top_contributor["probability"] >= 0.35
