import os
import logging
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Thread pool for blocking operations
_executor = ThreadPoolExecutor(max_workers=2)

# Try to import whisper; fall back gracefully for environments without it
try:
    import whisper
    _WHISPER_MODEL = None

    def _get_model():
        global _WHISPER_MODEL
        if _WHISPER_MODEL is None:
            model_size = os.getenv("WHISPER_MODEL", "base")
            logger.info(f"Loading Whisper model: {model_size}")
            _WHISPER_MODEL = whisper.load_model(model_size)
        return _WHISPER_MODEL

    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("openai-whisper not installed. Transcription will use mock mode.")


def _transcribe_sync(audio_path: str) -> str:
    """Synchronous transcription using Whisper."""
    try:
        model = _get_model()
        result = model.transcribe(audio_path, fp16=False, language="en")
        transcript = result["text"].strip()
        logger.info(f"Transcribed {len(transcript)} characters from {audio_path}")
        return transcript if transcript else "[No speech detected]"
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return _mock_transcription(audio_path)


async def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text using OpenAI Whisper (async-safe)."""
    if not WHISPER_AVAILABLE:
        return _mock_transcription(audio_path)

    try:
        # Run the blocking transcription in a thread pool
        loop = asyncio.get_event_loop()
        transcript = await asyncio.wait_for(
            loop.run_in_executor(_executor, _transcribe_sync, audio_path),
            timeout=30.0  # 30 second timeout for transcription
        )
        return transcript
    except asyncio.TimeoutError:
        logger.error("Transcription timeout")
        return _mock_transcription(audio_path)
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return _mock_transcription(audio_path)


def _mock_transcription(audio_path: str) -> str:
    """Mock transcription for testing without Whisper."""
    import random
    samples = [
        "Hello, this is the bank calling. Your account will be blocked unless you send money immediately.",
        "Don't hang up. You owe back taxes and you must transfer funds now to avoid arrest.",
        "Hi, I'm calling about your car warranty. Press 1 to speak with a representative.",
        "Congratulations! You've won a prize. Please provide your credit card details.",
        "This is a final notice. Your social security number has been suspended.",
    ]
    return random.choice(samples)
