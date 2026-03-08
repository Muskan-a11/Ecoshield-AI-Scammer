# backend/threat_analyzer.py

from backend.deepfake_detector import DeepfakeDetector
from backend.sentiment_engine import SentimentEngine
from backend.negotiator import Negotiator


def analyze_threat(content: str):
    deepfake_detector = DeepfakeDetector()
    deepfake_score = deepfake_detector.detect(content)
    sentiment_engine = SentimentEngine()
    sentiment_score = sentiment_engine.analyze(content)
    negotiator = Negotiator()
    threat_level = negotiator.classify(content)

    final_confidence = (
        deepfake_score * 0.4 +
        sentiment_score * 0.3 +
        threat_level * 0.3
    )

    return {
        "deepfake_score": deepfake_score,
        "sentiment_score": sentiment_score,
        "threat_level": threat_level,
        "confidence": round(final_confidence * 100, 2)
    }
