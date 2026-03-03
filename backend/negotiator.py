import random

class Negotiator:

    def __init__(self):
        self.responses = {
            "STALL": [
                "Can you hold on? My system is loading.",
                "One moment, I need to check something."
            ],
            "SKEPTICAL": [
                "Can you verify your employee ID?",
                "Which department are you calling from?"
            ]
        }

    def generate_response(self, threat_level: str):

        if threat_level in ["HIGH", "CRITICAL"]:
            strategy = "STALL"
        else:
            strategy = "SKEPTICAL"

        return {
            "suggested_response": random.choice(self.responses[strategy]),
            "strategy": strategy
        }