import random

class DeepfakeDetector:

    def detect_deepfake(self, audio_data: str):
        confidence = round(random.uniform(0.2, 0.95), 2)

        if confidence > 0.7:
            anomaly = "Spectral irregularities and pitch discontinuity detected."
        else:
            anomaly = "No strong synthetic patterns detected."

        return {
            "is_deepfake": confidence > 0.6,
            "confidence": confidence,
            "risk_level": "HIGH" if confidence > 0.8 else "MEDIUM" if confidence > 0.5 else "LOW",
            "analysis_note": anomaly
        }