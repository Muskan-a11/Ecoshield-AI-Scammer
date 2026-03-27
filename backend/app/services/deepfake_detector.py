import os
import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Try PyTorch and librosa
try:
    import torch
    import torch.nn as nn
    import librosa
    TORCH_AVAILABLE = True
    logger.info("PyTorch available for deepfake detection.")
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch/librosa not available. Using heuristic deepfake detection.")


class SpectrogramCNN(nn.Module if TORCH_AVAILABLE else object):
    """
    Lightweight CNN that analyzes mel-spectrograms for deepfake voice artifacts.
    Real deepfake detectors (e.g., RawNet2, AASIST) would be used in production.
    This placeholder mimics the same interface.
    """

    def __init__(self):
        if TORCH_AVAILABLE:
            super().__init__()
            self.features = nn.Sequential(
                nn.Conv2d(1, 32, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(32, 64, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.MaxPool2d(2),
                nn.Conv2d(64, 128, kernel_size=3, padding=1),
                nn.ReLU(),
                nn.AdaptiveAvgPool2d((4, 4)),
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(128 * 4 * 4, 256),
                nn.ReLU(),
                nn.Dropout(0.5),
                nn.Linear(256, 1),
                nn.Sigmoid(),
            )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)


_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None and TORCH_AVAILABLE:
        _MODEL = SpectrogramCNN()
        model_path = os.getenv("DEEPFAKE_MODEL_PATH", "")
        if model_path and os.path.exists(model_path):
            _MODEL.load_state_dict(torch.load(model_path, map_location="cpu"))
            logger.info(f"Loaded deepfake model from {model_path}")
        else:
            logger.info("Using untrained SpectrogramCNN (placeholder). "
                        "Set DEEPFAKE_MODEL_PATH for a trained model.")
        _MODEL.eval()
    return _MODEL


def _extract_spectrogram(audio_path: str) -> np.ndarray:
    """Extract mel-spectrogram from audio file."""
    y, sr = librosa.load(audio_path, sr=16000, mono=True, duration=10.0)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_db


def _heuristic_deepfake_score(audio_bytes: bytes) -> float:
    """
    Heuristic fallback: analyze byte entropy as a very rough proxy.
    Real production would use a trained model.
    """
    import math
    if len(audio_bytes) < 100:
        return 0.1
    sample = audio_bytes[:4096]
    freq = {}
    for b in sample:
        freq[b] = freq.get(b, 0) + 1
    entropy = -sum((c / len(sample)) * math.log2(c / len(sample)) for c in freq.values())
    # Normalize to 0-1 range (max entropy for bytes is 8)
    return min(entropy / 8.0, 1.0) * 0.5  # scale down to reasonable range


async def detect_deepfake(audio_path: str, audio_bytes: bytes) -> Dict[str, Any]:
    """
    Analyze audio for deepfake/synthetic voice artifacts.
    Returns confidence score and boolean flag.
    """
    try:
        if TORCH_AVAILABLE:
            model = _get_model()
            mel_spec = _extract_spectrogram(audio_path)

            # Resize to fixed shape (128, 128)
            from PIL import Image
            import torchvision.transforms as T
            img = Image.fromarray(mel_spec.astype(np.float32))
            transform = T.Compose([
                T.Resize((128, 128)),
                T.ToTensor(),
            ])
            tensor = transform(img).unsqueeze(0)  # (1, 1, 128, 128)

            with torch.no_grad():
                confidence = model(tensor).item()
        else:
            confidence = _heuristic_deepfake_score(audio_bytes)

        is_deepfake = confidence > float(os.getenv("DEEPFAKE_THRESHOLD", "0.6"))
        logger.info(f"Deepfake score: {confidence:.3f}, is_deepfake: {is_deepfake}")

        return {
            "is_deepfake": is_deepfake,
            "confidence": round(confidence, 4),
        }

    except Exception as e:
        logger.error(f"Deepfake detection error: {e}")
        return {"is_deepfake": False, "confidence": 0.0}
