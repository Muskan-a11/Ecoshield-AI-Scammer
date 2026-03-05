# ================================
# EchoShield API - Main Application
# ================================

from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel

# Internal Modules
from deepfake_detector import DeepfakeDetector
from sentiment_engine import SentimentEngine
from negotiator import Negotiator
from threat_analyzer import analyze_threat


# ================================
# App Initialization
# ================================

app = FastAPI(title="EchoShield API")

detector = DeepfakeDetector()
engine = SentimentEngine()
negotiator = Negotiator()


# ================================
# Request Models
# ================================

class ThreatRequest(BaseModel):
    content: str


class AnalyzeRequest(BaseModel):
    audio_data: str
    transcript: str


class ThreatResponse(BaseModel):
    deepfake_score: float
    sentiment_score: float
    threat_level: float
    confidence: float

# ================================
# Utility Functions
# ================================

def calibrate_confidence(score: float):
    """
    Applies calibration to confidence score
    to reduce overconfidence bias.
    """
    if score > 0.85:
        return round(score * 0.98, 2)
    elif score > 0.6:
        return round(score * 0.95, 2)
    return round(score, 2)


# ================================
# Health & Root Endpoints
# ================================

@app.get("/")
def root():
    return {"message": "EchoShield API Running"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }


# ================================
# Basic Testing Endpoints
# ================================

@app.post("/analyze", response_model=ThreatResponse)
def analyze(req: ThreatRequest):
    return analyze_threat(req.content)


@app.post("/test-deepfake")
def test_deepfake():
    return detector.detect_deepfake("sample_audio")


@app.post("/test-urgency")
def test_urgency():
    sample = "This is urgent. Your account will be suspended immediately."
    return engine.detect_urgency(sample)


# ================================
# Main Threat Analysis Endpoint
# ================================

@app.post("/api/analyze")
def analyze_threat_endpoint(request: AnalyzeRequest):

    # Step 1: Individual Analysis
    deepfake_result = detector.detect_deepfake(request.audio_data)
    urgency_result = engine.detect_urgency(request.transcript)

    # Step 2: Combine Scores
    combined_score = (
        deepfake_result.get("confidence", 0) +
        urgency_result.get("urgency_score", 0)
    ) / 2

    # Multi-signal amplification
    if deepfake_result["is_deepfake"] and urgency_result["urgency_detected"]:
        combined_score += 0.1

    # Step 3: Threat Level Classification
    if combined_score > 0.8:
        level = "CRITICAL"
    elif combined_score > 0.6:
        level = "HIGH"
    elif combined_score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Step 4: Generate Negotiation Strategy
    negotiation = negotiator.generate_response(level)

    # Step 5: Confidence Calibration
    combined_score = calibrate_confidence(combined_score)

    # Step 6: Final Response
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