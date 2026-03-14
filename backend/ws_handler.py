from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def city_connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket, client_id: str, detector, engine, negotiator, db):
    await manager.city_connect(websocket)
    print(f"✓ WebSocket client connected: {client_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Extract data
            audio_data = message.get("audio_data", "")
            transcript = message.get("transcript", "")
            
            # Real-time analysis pipeline
            deepfake_result = await asyncio.to_thread(detector.detect_deepfake, audio_data)
            urgency_result = await asyncio.to_thread(engine.detect_urgency, transcript)
            
            combined_score = (
                deepfake_result["confidence"] * 0.6 +
                urgency_result["urgency_score"] * 0.4
            )
            
            level = "LOW"
            if combined_score > 0.8: level = "CRITICAL"
            elif combined_score > 0.6: level = "HIGH"
            elif combined_score > 0.4: level = "MEDIUM"
            
            negotiation = await asyncio.to_thread(negotiator.generate_response, level)
            
            response = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "ANALYSIS_COMPLETE",
                "analysis_results": {
                    "deepfake_detection": deepfake_result,
                    "urgency_detection": urgency_result,
                    "overall_threat_assessment": {
                        "threat_level": level,
                        "combined_confidence": round(combined_score, 2),
                        "requires_family_alert": level in ["HIGH", "CRITICAL"]
                    }
                },
                "negotiator_response": negotiation
            }
            
            # Log to DB
            def log_db():
                db.log_threat({
                    "threat_level": level,
                    "combined_confidence": combined_score,
                    "transcript": transcript,
                    "detected_keywords": urgency_result["detected_keywords"]
                })
            await asyncio.to_thread(log_db)
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"WebSocket client disconnected: {client_id}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
        manager.disconnect(websocket)
