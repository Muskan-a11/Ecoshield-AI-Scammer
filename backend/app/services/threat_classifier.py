from typing import Dict, Any
from app.models.call_log import ThreatLevel
import logging

logger = logging.getLogger(__name__)


def classify_threat(
    deepfake_confidence: float,
    is_deepfake: bool,
    urgency_score: float,
    urgency_detected: bool,
) -> Dict[str, Any]:
    """
    Combine deepfake and scam scores into a unified threat classification.
    
    Scoring formula:
    - Deepfake weight: 40%
    - Urgency/scam weight: 60%
    - Deepfake boolean adds flat 0.2 bonus
    """
    deepfake_weight = 0.40
    urgency_weight = 0.60

    combined = (deepfake_confidence * deepfake_weight) + (urgency_score * urgency_weight)

    # Boost if deepfake confirmed
    if is_deepfake:
        combined = min(combined + 0.20, 1.0)

    # Determine threat level
    if combined >= 0.85:
        level = ThreatLevel.CRITICAL
        alert_required = True
    elif combined >= 0.60:
        level = ThreatLevel.HIGH
        alert_required = True
    elif combined >= 0.35:
        level = ThreatLevel.MEDIUM
        alert_required = False
    else:
        level = ThreatLevel.LOW
        alert_required = False

    logger.info(
        f"Threat classification: score={combined:.3f}, level={level}, alert={alert_required}"
    )

    return {
        "overall_score": round(combined, 4),
        "threat_level": level,
        "alert_required": alert_required,
    }
