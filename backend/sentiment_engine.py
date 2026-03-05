class SentimentEngine:

    def __init__(self):
        self.keyword_weights = {
    "urgent": 0.2,
    "immediate": 0.2,
    "emergency": 0.2,
    "arrest": 0.35,
    "lawsuit": 0.35,
    "account suspended": 0.3,
    "wire money": 0.4,
    "verify identity": 0.25,
    "hurry": 0.15,
    "now": 0.1
}
        print("✓ Sentiment Engine initialized")

    def detect_urgency(self, transcript: str):
        transcript_lower = transcript.lower()
        found = []
        score = 0

        for word, weight in self.keyword_weights.items():
            if word in transcript_lower:
                found.append(word)
                score += weight

        score = min(score, 1.0)

        explanation = f"{len(found)} scam-indicative keywords detected."

        return {
            "urgency_detected": len(found) > 0,
            "urgency_score": round(score, 2),
            "risk_level": "HIGH" if score > 0.6 else "MEDIUM" if score > 0.3 else "LOW",
            "detected_keywords": found,
            "explanation": explanation
        }
        