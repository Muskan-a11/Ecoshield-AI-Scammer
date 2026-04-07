"""
NLP-based scam classifier using DistilBERT (or a lighter fallback).

Loads a pre-trained HuggingFace model fine-tuned for scam/spam classification.
Falls back gracefully to a keyword-scoring approach if transformers is not installed.
"""

from __future__ import annotations
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

# ─── Try to load transformers ─────────────────────────────────────────────────
_pipeline = None
_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"  # public HF model
# For production, swap with a scam-specific fine-tuned model, e.g.:
#   "madhurjindal/autonlp-Gibberish-Detector-492513457" or your own fine-tuned BERT

def _load_model():
    global _pipeline
    if _pipeline is not None:
        return True
    try:
        from transformers import pipeline  # type: ignore
        # Use a sentiment model as a proxy — positive = safe, negative = threat
        # In production replace with a scam-fine-tuned checkpoint
        _pipeline = pipeline(
            "text-classification",
            model=_MODEL_NAME,
            truncation=True,
            max_length=512,
        )
        logger.info(f"[NLP] Loaded DistilBERT pipeline ({_MODEL_NAME})")
        return True
    except Exception as e:
        logger.warning(f"[NLP] Transformers not available, using fallback: {e}")
        return False


# ─── Scam indicator keywords for fallback ────────────────────────────────────
_SCAM_KEYWORDS = [
    "irs", "arrest", "warrant", "suspended", "blocked", "gift card",
    "send money", "transfer funds", "act now", "limited time", "verify account",
    "social security", "bank account", "credit card", "urgent", "immediately",
    "don't hang up", "final notice", "overdue", "tax refund", "congratulations you won",
    "do not tell", "keep confidential", "bitcoin", "wire transfer",
]


def _fallback_classify(text: str) -> float:
    """Keyword-based scam scoring as fallback when transformers unavailable."""
    text_lower = text.lower()
    hits = sum(1 for kw in _SCAM_KEYWORDS if kw in text_lower)
    # Sigmoid-like scaling: 0 keywords → 0.05, 5+ keywords → 0.90+
    score = min(0.05 + hits * 0.17, 0.98)
    return round(score, 4)


async def classify_scam(transcript: str) -> Dict[str, Any]:
    """
    Classify transcript for scam probability.

    Returns:
        {
            "scam_probability": float,   # 0.0 – 1.0
            "ml_available": bool,
            "label": str,               # "SCAM" | "SAFE"
            "confidence": float,
        }
    """
    if not transcript or len(transcript.strip()) < 4:
        return {"scam_probability": 0.0, "ml_available": False, "label": "SAFE", "confidence": 1.0}

    model_loaded = _load_model()

    if model_loaded and _pipeline is not None:
        try:
            result = _pipeline(transcript[:512])[0]
            label = result["label"]  # "POSITIVE" or "NEGATIVE" for SST-2
            confidence = float(result["score"])

            # SST-2: NEGATIVE sentiment → more scam-like (threats, urgency)
            # For a real scam model, map directly to SCAM/SAFE
            scam_prob = confidence if label == "NEGATIVE" else 1.0 - confidence
            scam_prob = round(scam_prob, 4)

            logger.info(f"[NLP] DistilBERT: label={label}, conf={confidence:.3f}, scam_prob={scam_prob:.3f}")
            return {
                "scam_probability": scam_prob,
                "ml_available": True,
                "label": "SCAM" if scam_prob > 0.55 else "SAFE",
                "confidence": confidence,
            }
        except Exception as e:
            logger.error(f"[NLP] Model inference failed: {e}")

    # Fallback
    score = _fallback_classify(transcript)
    logger.info(f"[NLP] Fallback classifier: score={score:.3f}")
    return {
        "scam_probability": score,
        "ml_available": False,
        "label": "SCAM" if score > 0.55 else "SAFE",
        "confidence": score,
    }
