from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User
from app.models.call_log import CallLog, ThreatResult, AnalyzeTextRequest
from app.services.scam_detector import detect_scam_tactics
from app.services.threat_classifier import classify_threat
from app.services.negotiator import generate_negotiator_strategy
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=ThreatResult)
async def analyze_transcript(
    request: AnalyzeTextRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze a transcript string directly and return threat assessment."""
    scam_result = await detect_scam_tactics(request.transcript)
    threat = classify_threat(
        deepfake_confidence=0.0,
        is_deepfake=False,
        urgency_score=scam_result["urgency_score"],
        urgency_detected=scam_result["urgency_detected"],
    )
    strategy = await generate_negotiator_strategy(request.transcript, threat["threat_level"])

    # Optionally update an existing call log
    if request.call_id:
        log = await CallLog.get(request.call_id)
        if log and log.user_id == str(current_user.id):
            log.transcript = request.transcript
            log.urgency_score = scam_result["urgency_score"]
            log.urgency_detected = scam_result["urgency_detected"]
            log.urgency_phrases_found = scam_result["phrases_found"]
            log.overall_threat_score = threat["overall_score"]
            log.threat_level = threat["threat_level"]
            log.negotiator_strategy = strategy
            await log.save()
            call_log_id = str(log.id)
        else:
            call_log_id = "unknown"
    else:
        # Create new log entry
        log = CallLog(
            user_id=str(current_user.id),
            transcript=request.transcript,
            urgency_score=scam_result["urgency_score"],
            urgency_detected=scam_result["urgency_detected"],
            urgency_phrases_found=scam_result["phrases_found"],
            overall_threat_score=threat["overall_score"],
            threat_level=threat["threat_level"],
            negotiator_strategy=strategy,
            alert_sent=threat["alert_required"],
        )
        await log.insert()
        call_log_id = str(log.id)

    return ThreatResult(
        call_log_id=call_log_id,
        transcript=request.transcript,
        is_deepfake=False,
        deepfake_confidence=0.0,
        urgency_detected=scam_result["urgency_detected"],
        urgency_score=scam_result["urgency_score"],
        urgency_phrases_found=scam_result["phrases_found"],
        overall_threat_score=threat["overall_score"],
        threat_level=threat["threat_level"],
        negotiator_strategy=strategy,
        alert_required=threat["alert_required"],
    )


@router.get("/call-logs")
async def get_call_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    """Get call logs for current user."""
    logs = (
        await CallLog.find(CallLog.user_id == str(current_user.id))
        .sort(-CallLog.call_start)
        .limit(limit)
        .to_list()
    )
    return [
        {
            "id": str(log.id),
            "call_start": log.call_start,
            "threat_level": log.threat_level,
            "overall_threat_score": log.overall_threat_score,
            "is_deepfake": log.is_deepfake,
            "urgency_detected": log.urgency_detected,
            "transcript": log.transcript,
            "negotiator_strategy": log.negotiator_strategy,
            "caller_number": log.caller_number,
        }
        for log in logs
    ]


@router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
    """Get user statistics."""
    all_logs = await CallLog.find(CallLog.user_id == str(current_user.id)).to_list()
    total_calls = len(all_logs)
    scam_calls = sum(1 for l in all_logs if l.threat_level in ["HIGH", "CRITICAL"])
    deepfake_calls = sum(1 for l in all_logs if l.is_deepfake)
    avg_threat = sum(l.overall_threat_score for l in all_logs) / total_calls if total_calls else 0

    threat_breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for log in all_logs:
        threat_breakdown[log.threat_level] = threat_breakdown.get(log.threat_level, 0) + 1

    return {
        "total_calls_analyzed": total_calls,
        "scam_calls_detected": scam_calls,
        "deepfake_calls_detected": deepfake_calls,
        "average_threat_score": round(avg_threat, 3),
        "threat_breakdown": threat_breakdown,
    }
