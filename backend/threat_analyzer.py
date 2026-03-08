# backend/threat_analyzer.py

def analyze_threat(content: str, detector, engine):

    deepfake_result = detector.detect_deepfake(content)
    deepfake_score = float(deepfake_result.get("confidence", 0))

    sentiment_result = engine.detect_urgency(content)
    sentiment_score = float(sentiment_result.get("urgency_score", 0))

    threat_level = (deepfake_score + sentiment_score) / 2

    final_confidence = (
        deepfake_score * 0.4 +
        sentiment_score * 0.3 +
        threat_level * 0.3
    )

    return {
        "deepfake_score": round(deepfake_score, 2),
        "sentiment_score": round(sentiment_score, 2),
        "threat_level": round(threat_level, 2),
        "confidence": round(final_confidence * 100, 2)
    }