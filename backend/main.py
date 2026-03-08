# ================================
# EchoShield API - Main Application
# ================================

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
import shutil
import os
import uuid

# Internal Modules
from deepfake_detector import DeepfakeDetector
from sentiment_engine import SentimentEngine
from negotiator import Negotiator
from threat_analyzer import analyze_threat
from audio_transcriber import transcribe_audio


# ================================
# App Initialization
# ================================

app = FastAPI(title="EchoShield API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy loaded AI engines
detector = None
engine = None
negotiator = None


# ================================
# Lazy Loading Functions
# ================================

def get_detector():
    global detector
    if detector is None:
        detector = DeepfakeDetector()
    return detector


def get_engine():
    global engine
    if engine is None:
        engine = SentimentEngine()
    return engine


def get_negotiator():
    global negotiator
    if negotiator is None:
        negotiator = Negotiator()
    return negotiator


# ================================
# Request Models
# ================================

class ThreatRequest(BaseModel):
    content: str


class AnalyzeRequest(BaseModel):
    audio_data: str
    transcript: str


# ================================
# Utility Functions
# ================================

def calibrate_confidence(score: float):

    if score > 0.85:
        return round(score * 0.98, 2)
    elif score > 0.6:
        return round(score * 0.95, 2)

    return round(score, 2)


# ================================
# Root & Health
# ================================

@app.get("/")
def root():
    return {"message": "EchoShield API Running 🚀"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }


# ================================
# Text Threat Analysis
# ================================

@app.post("/analyze")
def analyze_text(req: ThreatRequest):

    result = analyze_threat(
    req.content,
    get_detector(),
    get_engine()
)

    return {
        "input_text": req.content,
        "analysis": result
    }


# ================================
# Deepfake Test
# ================================

@app.post("/test-deepfake")
def test_deepfake():

    detector = get_detector()

    return detector.detect_deepfake("sample_audio")


# ================================
# Urgency Test
# ================================

@app.post("/test-urgency")
def test_urgency():

    engine = get_engine()

    sample = "This is urgent. Your account will be suspended immediately."

    return engine.detect_urgency(sample)


# ================================
# Combined AI Threat Analysis
# ================================

@app.post("/api/analyze")
def analyze_threat_endpoint(request: AnalyzeRequest):

    detector = get_detector()
    engine = get_engine()
    negotiator = get_negotiator()

    # Safety checks
    audio_data = request.audio_data or ""
    transcript = request.transcript or ""

    # Run models
    deepfake_result = detector.detect_deepfake(audio_data)
    urgency_result = engine.detect_urgency(transcript)

    # Extract scores safely
    deepfake_score = float(deepfake_result.get("confidence", 0))
    urgency_score = float(urgency_result.get("urgency_score", 0))

    # Combine scores
    combined_score = (deepfake_score + urgency_score) / 2

    # Multi-signal amplification
    if deepfake_result.get("is_deepfake", False) and urgency_result.get("urgency_detected", False):
        combined_score += 0.1

    # Threat classification
    if combined_score > 0.8:
        level = "CRITICAL"
    elif combined_score > 0.6:
        level = "HIGH"
    elif combined_score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Negotiation response
    negotiation = negotiator.generate_response(level)

    # Confidence calibration
    combined_score = calibrate_confidence(combined_score)

    return {
        "deepfake_detection": deepfake_result,
        "urgency_detection": urgency_result,
        "overall_threat_assessment": {
            "threat_level": level,
            "combined_confidence": round(combined_score, 2),
            "requires_family_alert": level in ["HIGH", "CRITICAL"]
        },
        "negotiation_strategy": negotiation
    }

# ================================
# Audio Upload Analysis
# ================================

@app.post("/api/analyze-audio")
async def analyze_audio(file: UploadFile = File(...)):

    temp_path = None

    try:

        os.makedirs("temp", exist_ok=True)

        temp_filename = f"{uuid.uuid4().hex}_{file.filename}"
        temp_path = os.path.join("temp", temp_filename)

        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        transcript = transcribe_audio(temp_path)

        analysis_result = analyze_threat(
            transcript,
            get_detector(),
            get_engine()
        )

        return {
            "transcript": transcript,
            "analysis": analysis_result
        }

    finally:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)