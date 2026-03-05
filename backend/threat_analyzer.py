# backend/threat_analyzer.py

from deepfake_detector import detect_deepfake
from sentiment_engine import analyze_sentiment
from negotiator import classify_threat

def analyze_threat(content: str):
    deepfake_score = detect_deepfake(content)
    sentiment_score = analyze_sentiment(content)
    threat_level = classify_threat(content)

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
