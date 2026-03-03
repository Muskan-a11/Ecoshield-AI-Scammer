class SentimentEngine:

    def __init__(self):
        self.keywords = [
            "urgent", "immediate", "emergency",
            "arrest", "suspended", "wire money",
            "hurry", "now"
        ]
        print("✓ Sentiment Engine initialized")

    def detect_urgency(self, transcript: str):
        transcript_lower = transcript.lower()
        found = []

        for word in self.keywords:
            if word in transcript_lower:
                found.append(word)

        score = min(len(found) * 0.15, 1.0)

        return {
            "urgency_detected": len(found) > 0,
            "urgency_score": round(score, 2),
            "risk_level": "HIGH" if score > 0.6 else "MEDIUM" if score > 0.3 else "LOW",
            "detected_keywords": found
        }