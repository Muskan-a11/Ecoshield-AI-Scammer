from fastapi import FastAPI, WebSocket
from datetime import datetime, timezone
from pydantic import BaseModel
from deepfake_detector import DeepfakeDetector
from sentiment_engine import SentimentEngine
from negotiator import Negotiator
from ws_handler import websocket_handler
from database import db_manager

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="EchoShield API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "EchoShield API Running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc)
    }

detector = DeepfakeDetector()
engine = SentimentEngine()
negotiator = Negotiator()

@app.get("/test-deepfake")
def test_deepfake():
    return detector.detect_deepfake("sample_audio")

@app.get("/test-urgency")
def test_urgency():
    sample = "This is urgent. Your account will be suspended immediately."
    return engine.detect_urgency(sample)

class AnalyzeRequest(BaseModel):
    audio_data: str
    transcript: str

@app.post("/api/analyze")
def analyze_threat(request: AnalyzeRequest):
    try:
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

        negotiation = negotiator.generate_response(level)
        
        # Log to DB
        db_manager.log_threat({
            "threat_level": level,
            "combined_confidence": round(combined_score, 2),
            "transcript": request.transcript,
            "detected_keywords": urgency_result["detected_keywords"]
        })
    except Exception as e:
        print(f"Error analyzing threat: {e}")
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail="Internal Server Error")

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

@app.get("/api/threats")
def get_threats(limit: int = 10):
    return db_manager.get_recent_threats(limit)

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket_handler(websocket, client_id, detector, engine, negotiator, db_manager)

if __name__ == "__main__":
    import uvicorn
    print("============================================================")
    print("🛡️  EchoShield Server Starting...")
    print("============================================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)
