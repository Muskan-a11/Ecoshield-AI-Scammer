from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.scam_detector import detect_scam_tactics
from app.services.threat_classifier import classify_threat
from app.services.negotiator import generate_negotiator_strategy
from typing import Optional
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=dict)
async def analyze_transcript(
    request: dict,
    current_user = Depends(get_current_user),
):
    """Analyze a transcript string directly and return threat assessment."""
    from app.core.database import CallLog
    
    transcript = request.get("transcript", "")
    call_id = request.get("call_id")
    
    if not transcript or len(transcript) < 5:
        raise HTTPException(status_code=400, detail="Transcript too short")
    
    scam_result = await detect_scam_tactics(transcript)
    threat = classify_threat(
        deepfake_confidence=0.0,
        is_deepfake=False,
        urgency_score=scam_result["urgency_score"],
        urgency_detected=scam_result["urgency_detected"],
    )
    strategy = await generate_negotiator_strategy(transcript, threat["threat_level"])

    # Optionally update an existing call log
    if call_id:
        log = await CallLog.get(call_id)
        if log and log.user_id == current_user.id:
            log.transcript = transcript
            log.urgency_score = scam_result["urgency_score"]
            log.urgency_detected = scam_result["urgency_detected"]
            log.urgency_phrases_found = scam_result["phrases_found"]
            log.overall_threat_score = threat["overall_score"]
            log.threat_level = threat["threat_level"]
            log.negotiator_strategy = strategy
            await log.save()
            call_log_id = log.id
        else:
            call_log_id = "unknown"
    else:
        # Create new log entry — works for both MockCallLog and Beanie Document
        log_id = str(uuid4())
        from app.core.database import is_db_connected
        if is_db_connected():
            # Real Beanie Document — keyword args only
            log = CallLog(user_id=str(current_user.id))
        else:
            # MockCallLog — takes positional (call_log_id, user_id)
            log = CallLog(log_id, current_user.id)
        log.transcript = transcript
        log.urgency_score = scam_result["urgency_score"]
        log.urgency_detected = scam_result["urgency_detected"]
        log.urgency_phrases_found = scam_result["phrases_found"]
        log.overall_threat_score = threat["overall_score"]
        log.threat_level = threat["threat_level"]
        log.negotiator_strategy = strategy
        log.alert_sent = threat["alert_required"]
        await log.insert()
        call_log_id = log_id

    return {
        "call_log_id": call_log_id,
        "transcript": transcript,
        "is_deepfake": False,
        "deepfake_confidence": 0.0,
        "urgency_detected": scam_result["urgency_detected"],
        "urgency_score": scam_result["urgency_score"],
        "urgency_phrases_found": scam_result["phrases_found"],
        "overall_threat_score": threat["overall_score"],
        "threat_level": threat["threat_level"],
        "negotiator_strategy": strategy,
        "alert_required": threat["alert_required"],
    }


@router.get("/call-logs")
async def get_call_logs(
    limit: int = 20,
    current_user = Depends(get_current_user),
):
    """Get call logs for current user."""
    from app.core.database import CallLog
    
    logs = await CallLog.find({"user_id": current_user.id}).sort([("call_start", -1)]).limit(limit).to_list()
    return [
        {
            "id": log.id,
            "call_start": log.call_start.isoformat() if hasattr(log.call_start, 'isoformat') else str(log.call_start),
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
async def get_stats(current_user = Depends(get_current_user)):
    """Get user statistics."""
    from app.core.database import CallLog
    
    all_logs = await CallLog.find({"user_id": current_user.id}).to_list()
    total_calls = len(all_logs)
    # threat_level may be a ThreatLevel enum or a plain string — normalise to str
    scam_calls = sum(1 for l in all_logs if str(getattr(l.threat_level, 'value', l.threat_level)) in ["HIGH", "CRITICAL"])
    deepfake_calls = sum(1 for l in all_logs if l.is_deepfake)
    avg_threat = sum(l.overall_threat_score for l in all_logs) / total_calls if total_calls else 0

    threat_breakdown = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    for log in all_logs:
        level_str = str(getattr(log.threat_level, 'value', log.threat_level))
        threat_breakdown[level_str] = threat_breakdown.get(level_str, 0) + 1

    return {
        "total_calls_analyzed": total_calls,
        "scam_calls_detected": scam_calls,
        "deepfake_calls_detected": deepfake_calls,
        "average_threat_score": round(avg_threat, 3),
        "threat_breakdown": threat_breakdown,
    }
