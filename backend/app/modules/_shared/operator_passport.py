"""
Operator Passport — Persistent Evidence Store.

CRITICAL TRUST & SAFETY RULE (Architecture.md §6):
Demonstrated capability evidence in context, NOT a surveillance score.
Never emit strings like 'lazy', 'fatigued', 'dangerous', or 'inefficient'.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.db.models import Operator, OperatorCapabilityEvidence


def get_operator(db: Session, operator_id: str) -> Optional[Operator]:
    """Retrieve operator by ID."""
    return db.query(Operator).filter(Operator.id == operator_id).first()


def get_context_evidence(
    db: Session,
    operator_id: str,
    task_type: str,
    weather_bucket: str,
    material: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve demonstrated capability evidence for a specific context.
    If exact material is not matched, falls back to the broader (task_type, weather_bucket).
    """
    query = db.query(OperatorCapabilityEvidence).filter(
        OperatorCapabilityEvidence.operator_id == operator_id,
        OperatorCapabilityEvidence.task_type == task_type,
        OperatorCapabilityEvidence.weather_bucket == weather_bucket,
    )

    if material:
        evidence = query.filter(OperatorCapabilityEvidence.material == material).first()
        if evidence:
            return _format_evidence(evidence)

    # Fallback to general material
    evidence = query.first()
    if evidence:
        return _format_evidence(evidence)

    # Cold-start default: unobserved context
    return {
        "operator_id": operator_id,
        "task_type": task_type,
        "weather_bucket": weather_bucket,
        "sample_count": 0,
        "success_count": 0,
        "confidence": 0.05,
        "avg_time_delta_pct": None,
        "avg_quality_success_pct": None,
        "is_cold_start": True,
        "evidence_label": "Unobserved operational context — baseline observation required",
    }


def get_all_operator_evidence(db: Session, operator_id: str) -> List[Dict[str, Any]]:
    """Retrieve full passport evidence history for an operator."""
    records = db.query(OperatorCapabilityEvidence).filter(
        OperatorCapabilityEvidence.operator_id == operator_id
    ).all()
    return [_format_evidence(r) for r in records]


def _format_evidence(record: OperatorCapabilityEvidence) -> Dict[str, Any]:
    """Format evidence record respecting trust & safety guidelines."""
    success_pct = (
        round((record.success_count / record.sample_count) * 100, 1)
        if record.sample_count > 0
        else 0.0
    )
    confidence_pct = round(record.confidence * 100, 1)
    
    label = (
        f"{record.task_type} ({record.weather_bucket}) — {confidence_pct}% confidence, "
        f"based on {record.sample_count} comparable missions ({record.success_count} successful)"
    )

    return {
        "id": record.id,
        "operator_id": record.operator_id,
        "task_type": record.task_type,
        "weather_bucket": record.weather_bucket,
        "material": record.material,
        "sample_count": record.sample_count,
        "success_count": record.success_count,
        "success_rate_pct": success_pct,
        "avg_time_delta_pct": record.avg_time_delta_pct,
        "avg_quality_success_pct": record.avg_quality_success_pct,
        "confidence": record.confidence,
        "last_verified_at": record.last_verified_at,
        "is_cold_start": record.sample_count == 0,
        "evidence_label": label,
    }
