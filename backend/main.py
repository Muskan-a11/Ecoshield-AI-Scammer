from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from deepfake_detector import DeepfakeDetector
from sentiment_engine import SentimentEngine
from negotiator import Negotiator

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

detector = DeepfakeDetector()

@app.post("/test-deepfake")
def test_deepfake():
    return detector.detect_deepfake("sample_audio")

engine = SentimentEngine()

@app.post("/test-urgency")
def test_urgency():
    sample = "This is urgent. Your account will be suspended immediately."
    return engine.detect_urgency(sample)

class AnalyzeRequest(BaseModel):
    audio_data: str
    transcript: str

negotiator = Negotiator()

@app.post("/api/analyze")
def analyze_threat(request: AnalyzeRequest):

    deepfake_result = detector.detect_deepfake(request.audio_data)
    urgency_result = engine.detect_urgency(request.transcript)

    combined_score = (deepfake_result.get("confidence", 0) + urgency_result.get("urgency_score", 0)) / 2
    
    if deepfake_result["is_deepfake"] and urgency_result["urgency_detected"]:
        combined_score += 0.1  # multi-signal amplification

    if combined_score > 0.8:
        level = "CRITICAL"
    elif combined_score > 0.6:
        level = "HIGH"
    elif combined_score > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    negotiation = negotiator.generate_response(level)

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
