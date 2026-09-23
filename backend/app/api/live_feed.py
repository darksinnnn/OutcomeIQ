"""
Live Telemetry WebSocket and REST Replay Endpoints.
"""

import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db, SessionLocal
from backend.app.db.models import Telemetry
from backend.app.modules._shared.telemetry_stream import (
    get_mission_telemetry,
    get_telemetry_window_summary,
)

router = APIRouter(prefix="/api/telemetry", tags=["Live Telemetry Feed"])


@router.get("/{mission_id}/ticks")
def get_ticks(mission_id: str, db: Session = Depends(get_db)):
    """Retrieve chronological recorded telemetry stream ticks for a mission."""
    records = get_mission_telemetry(db, mission_id)
    return [
        {
            "id": r.id,
            "mission_id": r.mission_id,
            "machine_id": r.machine_id,
            "operator_id": r.operator_id,
            "timestamp": r.timestamp,
            "engine_hours": r.engine_hours,
            "fuel_used_l": r.fuel_used_l,
            "load_cycles": r.load_cycles,
            "idle_minutes": r.idle_minutes,
            "seatbelt_status": r.seatbelt_status,
            "machine_moving": r.machine_moving,
            "machine_speed_kph": r.machine_speed_kph,
            "control_smoothness_score": r.control_smoothness_score,
            "safety_alert_triggered": r.safety_alert_triggered,
            "safety_signal_pattern": r.safety_signal_pattern,
        }
        for r in records
    ]


@router.get("/{mission_id}/summary")
def get_summary(mission_id: str, db: Session = Depends(get_db)):
    """Retrieve summarized telemetry window metrics."""
    return get_telemetry_window_summary(db, mission_id)


@router.websocket("/ws/{mission_id}")
async def telemetry_websocket(websocket: WebSocket, mission_id: str):
    """
    WebSocket endpoint for real-time telemetry streaming / replay.
    Streams telemetry ticks at steady interval for live dashboard demonstration.
    """
    await websocket.accept()
    db = SessionLocal()
    try:
        records = get_mission_telemetry(db, mission_id)
        if not records:
            await websocket.send_json({"error": f"No telemetry for mission {mission_id}"})
            await websocket.close()
            return

        # Stream records with interval
        for idx, r in enumerate(records):
            payload = {
                "tick_index": idx,
                "total_ticks": len(records),
                "timestamp": r.timestamp,
                "engine_hours": r.engine_hours,
                "fuel_used_l": r.fuel_used_l,
                "load_cycles": r.load_cycles,
                "idle_minutes": r.idle_minutes,
                "seatbelt_status": r.seatbelt_status,
                "machine_moving": r.machine_moving,
                "machine_speed_kph": r.machine_speed_kph,
                "control_smoothness_score": r.control_smoothness_score,
                "safety_alert_triggered": r.safety_alert_triggered,
                "safety_signal_pattern": r.safety_signal_pattern,
            }
            await websocket.send_json(payload)
            await asyncio.sleep(1.0)  # 1 second cadence between ticks

    except WebSocketDisconnect:
        pass
    finally:
        db.close()
