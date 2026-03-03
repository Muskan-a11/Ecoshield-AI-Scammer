from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="EchoShield API")

@app.get("/")
def root():
    return {"message": "EchoShield API Running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
from deepfake_detector import DeepfakeDetector

detector = DeepfakeDetector()

@app.post("/test-deepfake")
def test_deepfake():
    return detector.detect_deepfake("sample_audio")

from sentiment_engine import SentimentEngine

engine = SentimentEngine()

@app.post("/test-urgency")
def test_urgency():
    sample = "This is urgent. Your account will be suspended immediately."
    return engine.detect_urgency(sample)

from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    audio_data: str
    transcript: str


@app.post("/api/analyze")
def analyze_threat(request: AnalyzeRequest):

    deepfake_result = detector.detect_deepfake(request.audio_data)
    urgency_result = engine.detect_urgency(request.transcript)

    combined_score = (
        deepfake_result["confidence"] * 0.6 +
        urgency_result["urgency_score"] * 0.4
    )

    if combined_score > 0.8:
        level = "CRITICAL"
    elif combined_score > 0.6:
        level = "HIGH"
    elif combined_score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "deepfake_detection": deepfake_result,
        "urgency_detection": urgency_result,
        "overall_threat_assessment": {
            "threat_level": level,
            "combined_confidence": round(combined_score, 2),
            "requires_family_alert": level in ["HIGH", "CRITICAL"]
        }
    }