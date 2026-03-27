import io
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from typing import Optional
from app.core.security import get_current_user
from app.models.user import User
from app.models.call_log import CallLog, ThreatResult
from app.services.transcription import transcribe_audio
from app.services.deepfake_detector import detect_deepfake
from app.services.scam_detector import detect_scam_tactics
from app.services.threat_classifier import classify_threat
from app.services.negotiator import generate_negotiator_strategy
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/stream-audio", response_model=ThreatResult)
async def stream_audio_chunk(
    audio: UploadFile = File(...),
    call_id: Optional[str] = Form(None),
    chunk_index: int = Form(0),
    caller_number: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    """Receive audio chunk, transcribe, analyze, and return threat result."""
    audio_bytes = await audio.read()

    # Save chunk temporarily for processing
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        # Transcription
        transcript = await transcribe_audio(tmp_path)

        # Deepfake detection
        deepfake_result = await detect_deepfake(tmp_path, audio_bytes)

        # Scam tactic detection
        scam_result = await detect_scam_tactics(transcript)

        # Threat classification
        threat = classify_threat(
            deepfake_result["confidence"],
            deepfake_result["is_deepfake"],
            scam_result["urgency_score"],
            scam_result["urgency_detected"],
        )

        # Negotiator strategy
        strategy = await generate_negotiator_strategy(transcript, threat["threat_level"])

        # Upsert call log
        if call_id:
            log = await CallLog.get(call_id)
        else:
            log = None

        if not log:
            log = CallLog(
                user_id=str(current_user.id),
                caller_number=caller_number,
            )

        log.transcript = (log.transcript or "") + " " + transcript
        log.deepfake_confidence = deepfake_result["confidence"]
        log.is_deepfake = deepfake_result["is_deepfake"]
        log.urgency_score = scam_result["urgency_score"]
        log.urgency_detected = scam_result["urgency_detected"]
        log.urgency_phrases_found = scam_result["phrases_found"]
        log.overall_threat_score = threat["overall_score"]
        log.threat_level = threat["threat_level"]
        log.negotiator_strategy = strategy
        log.audio_chunks_received += 1
        log.alert_sent = threat["alert_required"]

        await log.save()

        return ThreatResult(
            call_log_id=str(log.id),
            transcript=transcript,
            is_deepfake=deepfake_result["is_deepfake"],
            deepfake_confidence=deepfake_result["confidence"],
            urgency_detected=scam_result["urgency_detected"],
            urgency_score=scam_result["urgency_score"],
            urgency_phrases_found=scam_result["phrases_found"],
            overall_threat_score=threat["overall_score"],
            threat_level=threat["threat_level"],
            negotiator_strategy=strategy,
            alert_required=threat["alert_required"],
        )
    finally:
        os.unlink(tmp_path)


@router.post("/analyze-audio", response_model=ThreatResult)
async def analyze_uploaded_audio(
    audio: UploadFile = File(...),
    caller_number: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
):
    """Analyze a complete uploaded audio recording."""
    audio_bytes = await audio.read()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        transcript = await transcribe_audio(tmp_path)
        deepfake_result = await detect_deepfake(tmp_path, audio_bytes)
        scam_result = await detect_scam_tactics(transcript)
        threat = classify_threat(
            deepfake_result["confidence"],
            deepfake_result["is_deepfake"],
            scam_result["urgency_score"],
            scam_result["urgency_detected"],
        )
        strategy = await generate_negotiator_strategy(transcript, threat["threat_level"])

        log = CallLog(
            user_id=str(current_user.id),
            caller_number=caller_number,
            transcript=transcript,
            deepfake_confidence=deepfake_result["confidence"],
            is_deepfake=deepfake_result["is_deepfake"],
            urgency_score=scam_result["urgency_score"],
            urgency_detected=scam_result["urgency_detected"],
            urgency_phrases_found=scam_result["phrases_found"],
            overall_threat_score=threat["overall_score"],
            threat_level=threat["threat_level"],
            negotiator_strategy=strategy,
            audio_chunks_received=1,
            alert_sent=threat["alert_required"],
        )
        await log.insert()

        return ThreatResult(
            call_log_id=str(log.id),
            transcript=transcript,
            is_deepfake=deepfake_result["is_deepfake"],
            deepfake_confidence=deepfake_result["confidence"],
            urgency_detected=scam_result["urgency_detected"],
            urgency_score=scam_result["urgency_score"],
            urgency_phrases_found=scam_result["phrases_found"],
            overall_threat_score=threat["overall_score"],
            threat_level=threat["threat_level"],
            negotiator_strategy=strategy,
            alert_required=threat["alert_required"],
        )
    finally:
        os.unlink(tmp_path)
