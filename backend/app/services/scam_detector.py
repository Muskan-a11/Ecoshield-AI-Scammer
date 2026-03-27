import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Urgency phrase patterns with weights
URGENCY_PATTERNS = [
    # High-weight critical patterns
    (r"\bsend\s+money\s+immediately\b", 0.95),
    (r"\btransfer\s+funds?\s+now\b", 0.95),
    (r"\byour\s+account\s+will\s+be\s+(blocked|suspended|closed|terminated)\b", 0.90),
    (r"\bdon'?t\s+hang\s+up\b", 0.85),
    (r"\byou\s+will\s+be\s+arrested\b", 0.90),
    (r"\bwarrant\s+(has\s+been\s+issued|out\s+for\s+your\s+arrest)\b", 0.90),
    (r"\byour\s+social\s+security\s+number\s+has\s+been\s+suspended\b", 0.92),
    (r"\birs\b.*\b(owe|debt|legal\s+action)\b", 0.88),
    # Medium-weight patterns
    (r"\bact\s+now\b", 0.65),
    (r"\blimited\s+time\b", 0.55),
    (r"\burgent\s+(action|matter)\b", 0.70),
    (r"\b(gift\s+card|google\s+play|itunes)\s+(payment|pay)\b", 0.85),
    (r"\bdo\s+not\s+tell\s+(anyone|your\s+family)\b", 0.88),
    (r"\bkeep\s+this\s+confidential\b", 0.80),
    (r"\byour\s+(computer|device)\s+has\s+been\s+(hacked|infected|compromised)\b", 0.80),
    (r"\bverify\s+your\s+(account|identity|credit\s+card)\b", 0.65),
    (r"\bcongratulations\s+you\s+(have\s+)?(won|been\s+selected)\b", 0.70),
    (r"\bfinal\s+(notice|warning)\b", 0.75),
    (r"\bimmediate\s+(action|payment)\b", 0.80),
    (r"\btax\s+refund\b", 0.55),
    (r"\bprovide\s+your\s+(credit\s+card|bank\s+account|routing\s+number)\b", 0.85),
    # Low-weight patterns
    (r"\bspecial\s+offer\b", 0.30),
    (r"\byou\s+owe\b", 0.55),
    (r"\boverdue\s+payment\b", 0.60),
    (r"\bback\s+taxes\b", 0.65),
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [
    (re.compile(pattern, re.IGNORECASE), weight, pattern)
    for pattern, weight, *_ in [(p[0], p[1]) for p in URGENCY_PATTERNS]
]


def _normalize_text(text: str) -> str:
    """Clean and normalize input text."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text


async def detect_scam_tactics(transcript: str) -> Dict[str, Any]:
    """
    Analyze transcript for scam tactics using pattern matching and NLP heuristics.
    Returns urgency score and list of detected phrases.
    """
    if not transcript or len(transcript.strip()) < 5:
        return {
            "urgency_detected": False,
            "urgency_score": 0.0,
            "phrases_found": [],
        }

    normalized = _normalize_text(transcript)
    phrases_found: List[str] = []
    scores: List[float] = []

    for compiled_pattern, weight, _ in zip(
        [c[0] for c in COMPILED_PATTERNS],
        [c[1] for c in URGENCY_PATTERNS],
        URGENCY_PATTERNS,
    ):
        matches = compiled_pattern.findall(normalized)
        if matches:
            for match in matches:
                phrase = match if isinstance(match, str) else " ".join(match)
                if phrase not in phrases_found:
                    phrases_found.append(phrase)
            scores.append(weight)

    if not scores:
        urgency_score = 0.0
    else:
        # Weighted combination: max score + bonus for multiple detections
        max_score = max(scores)
        bonus = min(0.15 * (len(scores) - 1), 0.30)
        urgency_score = min(max_score + bonus, 1.0)

    urgency_detected = urgency_score > 0.4

    logger.info(
        f"Scam detection: score={urgency_score:.3f}, "
        f"detected={urgency_detected}, patterns={len(scores)}"
    )

    return {
        "urgency_detected": urgency_detected,
        "urgency_score": round(urgency_score, 4),
        "phrases_found": phrases_found[:10],  # cap at 10
    }
