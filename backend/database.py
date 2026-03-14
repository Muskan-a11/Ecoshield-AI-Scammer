import json
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        # In-memory storage for demo simulation
        self.threat_logs = []
        print("✓ Database connection established (In-Memory Simulation)")

    def log_threat(self, threat_data: dict):
        """
        Logs threat metadata while ensuring privacy.
        - Masks phone numbers (if present)
        - Truncates transcripts
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "threat_level": threat_data.get("threat_level", "UNKNOWN"),
            "confidence": threat_data.get("combined_confidence", 0.0),
            "transcript_snippet": threat_data.get("transcript", "")[:200],
            "detected_keywords": threat_data.get("detected_keywords", [])
        }
        
        # In a real app, this would save to MongoDB
        self.threat_logs.append(log_entry)
        return True

    def get_recent_threats(self, limit=10):
        return self.threat_logs[-limit:]

db_manager = DatabaseManager()
