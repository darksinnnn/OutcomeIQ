"""
Automated tests for Phase 3:
- Outcome Guardian (focusing on on-schedule-low-quality scenario)
- What-If Lab (focusing on what-if-recovery scenario)
- Live Telemetry & Overview composite
- Trust & Safety language audit
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# 1. Outcome Guardian Tests
# ---------------------------------------------------------------------------

def test_outcome_guardian_on_time_low_quality_scenario():
    """
    Scenario 3: Mission is on schedule, but quality is degrading.
    Outcome Guardian must produce the signature headline:
    'You are on schedule, but this may not pass acceptance — rework risk rising.'
    """
    response = client.get("/api/outcome-guardian/MISSION-ON-TIME-LOW-QUALITY")
    assert response.status_code == 200
    data = response.json()

    assert "value" in data
    assert "confidence" in data
    assert "evidence" in data

    val = data["value"]
    signals = val["signals"]

    # Verify Time signal is GREEN
    assert signals["time"]["status"] == "green", (
        f"Expected time status 'green', got '{signals['time']['status']}'"
    )

    # Verify Quality or Acceptance is flagged
    assert signals["quality"]["status"] in ("amber", "red")
    assert signals["acceptance"]["status"] in ("amber", "red")

    # High rework probability
    assert val["rework_probability"] >= 0.70

    # Signature headline check
    headline = val["headline"].lower()
    assert "on schedule" in headline, f"Expected 'on schedule' in headline: {headline}"
    assert "rework" in headline or "acceptance" in headline


def test_outcome_guardian_six_signals():
    """Verify all 6 signals exist for any mission."""
    response = client.get("/api/outcome-guardian/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    signals = response.json()["value"]["signals"]
    for expected_key in ["time", "safety", "productivity", "fuel", "quality", "acceptance"]:
        assert expected_key in signals
        assert signals[expected_key]["status"] in ("green", "amber", "red")


# ---------------------------------------------------------------------------
# 2. What-If Lab Tests
# ---------------------------------------------------------------------------

def test_what_if_recovery_scenario():
    """
    Scenario: WHAT_IF_RECOVERY.
    Simulate adding a truck to eliminate haul delay.
    Must show substantial time recovery (> 10 min).
    """
    payload = {
        "mission_id": "MISSION-WHAT-IF-RECOVERY",
        "assumption_changed": {"add_truck": True},
    }
    response = client.post("/api/what-if/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "value" in data
    assert "confidence" in data
    assert "evidence" in data

    val = data["value"]
    delta = val["delta"]

    # Time recovered must be non-trivial
    assert delta["time_recovered_min"] > 10.0, (
        f"Expected time recovery > 10 min, got {delta['time_recovered_min']}"
    )
    assert delta["p50_after_min"] < delta["p50_before_min"]
    assert "recovers" in val["recommendation"].lower() or "recommended" in val["recommendation"].lower()


def test_what_if_operator_swap():
    """
    Simulate swapping operator to experienced lead.
    """
    payload = {
        "mission_id": "MISSION-OPERATOR-CONTEXT-MISMATCH",
        "assumption_changed": {"operator_id": "OP-1001"},
    }
    response = client.post("/api/what-if/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["value"]["predicted_after"]["p50_duration_min"] > 0


# ---------------------------------------------------------------------------
# 3. Overview & Live Telemetry Composite Tests
# ---------------------------------------------------------------------------

def test_list_missions():
    response = client.get("/api/missions")
    assert response.status_code == 200
    missions = response.json()
    assert len(missions) > 0


def test_list_operators_and_passport():
    response = client.get("/api/operators")
    assert response.status_code == 200
    ops = response.json()
    assert len(ops) >= 8

    # Check passport
    op_id = ops[0]["id"]
    passport_resp = client.get(f"/api/operators/{op_id}/passport")
    assert passport_resp.status_code == 200
    passport_data = passport_resp.json()
    assert "evidence_records" in passport_data
    assert len(passport_data["evidence_records"]) > 0


def test_live_operation_composite():
    """
    Verify single-pane composite feed for Live Operation screen.
    """
    response = client.get("/api/composite/live-operation/MISSION-FALSE-IDLE")
    assert response.status_code == 200
    data = response.json()

    assert "contract" in data
    assert "reality_engine" in data
    assert "time_model" in data
    assert "outcome_guardian" in data
    assert "telemetry_window" in data

    # Verify nested values
    assert data["reality_engine"]["value"]["explanation_class"] == "external_workflow"
    assert data["time_model"]["value"]["p50_duration_min"] > 0


# ---------------------------------------------------------------------------
# 4. Strict Trust & Safety Language Audit
# ---------------------------------------------------------------------------

def test_strict_trust_and_safety_audit():
    """
    Audit all responses for banned judgmental terms:
    ['lazy', 'fatigued', 'dangerous', 'inefficient']
    """
    banned_words = ["lazy", "fatigued", "dangerous", "inefficient"]

    test_endpoints = [
        "/api/reality-engine/MISSION-FALSE-IDLE",
        "/api/reality-engine/MISSION-OPERATOR-CONTEXT-MISMATCH",
        "/api/reality-engine/MISSION-ON-TIME-LOW-QUALITY",
        "/api/root-cause/MISSION-FALSE-IDLE",
        "/api/root-cause/MISSION-OPERATOR-CONTEXT-MISMATCH",
        "/api/outcome-guardian/MISSION-ON-TIME-LOW-QUALITY",
        "/api/operators/OP-1001/passport",
    ]

    for ep in test_endpoints:
        res = client.get(ep)
        assert res.status_code == 200
        text = res.text.lower()
        for banned in banned_words:
            assert banned not in text, f"Banned word '{banned}' detected in endpoint {ep}"
