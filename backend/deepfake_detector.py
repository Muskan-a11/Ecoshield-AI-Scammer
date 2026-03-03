import random

class DeepfakeDetector:

    def __init__(self):
        print("✓ Deepfake Detector loaded")

    def detect_deepfake(self, audio_data: str):
        confidence = round(random.uniform(0.2, 0.95), 2)

        is_deepfake = confidence > 0.6

        if confidence > 0.8:
            risk = "HIGH"
        elif confidence > 0.5:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        return {
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "risk_level": risk
        }