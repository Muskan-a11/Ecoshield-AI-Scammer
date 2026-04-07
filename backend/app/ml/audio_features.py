"""
Audio feature extractor for synthetic / deepfake voice detection.

Uses librosa (already in requirements) to extract:
  - MFCCs  — speaker identity fingerprint
  - ZCR    — zero crossing rate (high ZCR → noisy/synthetic audio)
  - Spectral centroid — brightness of voice
  - RMS energy variance — natural human speech has dynamic energy variation

Returns a synthetic voice probability score (0–1).
"""

from __future__ import annotations
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)


def extract_audio_features(audio_path: str) -> Dict[str, Any]:
    """
    Extract acoustic features from a WAV file.

    Args:
        audio_path: Path to a 16kHz mono WAV file.

    Returns:
        {
            "synthetic_voice_probability": float,
            "zcr_mean": float,
            "spectral_centroid_mean": float,
            "rms_variance": float,
            "mfcc_std_mean": float,
        }
    """
    try:
        import librosa  # type: ignore

        y, sr = librosa.load(audio_path, sr=16000, mono=True)

        if len(y) < sr * 0.5:  # less than 0.5 seconds — skip
            return _empty_result()

        # 1. Zero Crossing Rate — synthetic voices tend to be smoother (lower ZCR)
        #    but TTS can also be very precise → higher ZCR peaks
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        zcr_mean = float(np.mean(zcr))

        # 2. Spectral Centroid — brightness; many TTS systems produce unnaturally
        #    consistent centroids
        centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        centroid_std = float(np.std(centroid))

        # 3. RMS Energy variance — human speech has natural energy variation;
        #    TTS/deepfakes are often too smooth
        rms = librosa.feature.rms(y=y)[0]
        rms_var = float(np.var(rms))

        # 4. MFCC spread — captures vocal tract characteristics
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_std_mean = float(np.mean(np.std(mfccs, axis=1)))

        # ── Synthetic voice heuristic ─────────────────────────────────────────
        # Low RMS variance + low centroid_std = suspiciously uniform voice
        score = 0.0

        if rms_var < 0.0005:          score += 0.30  # very flat energy
        elif rms_var < 0.002:         score += 0.10

        if centroid_std < 200:        score += 0.25  # unnaturally steady pitch
        elif centroid_std < 500:      score += 0.10

        if mfcc_std_mean < 5.0:       score += 0.25  # low timbral variation
        elif mfcc_std_mean < 10.0:    score += 0.10

        if zcr_mean > 0.15:           score += 0.20  # noisy / digitally processed

        score = round(min(score, 1.0), 4)

        logger.info(
            f"[AudioFeatures] zcr={zcr_mean:.4f}, centroid_std={centroid_std:.1f}, "
            f"rms_var={rms_var:.6f}, mfcc_std={mfcc_std_mean:.2f} → synth_prob={score:.3f}"
        )

        return {
            "synthetic_voice_probability": score,
            "zcr_mean": round(zcr_mean, 4),
            "spectral_centroid_mean": round(float(np.mean(centroid)), 2),
            "rms_variance": round(rms_var, 6),
            "mfcc_std_mean": round(mfcc_std_mean, 4),
        }

    except Exception as e:
        logger.error(f"[AudioFeatures] Feature extraction failed: {e}")
        return _empty_result()


def _empty_result() -> Dict[str, Any]:
    return {
        "synthetic_voice_probability": 0.0,
        "zcr_mean": 0.0,
        "spectral_centroid_mean": 0.0,
        "rms_variance": 0.0,
        "mfcc_std_mean": 0.0,
    }
