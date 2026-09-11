import re
import numpy as np
import sounddevice as sd
from kokoro_onnx import Kokoro
from settings import settings

kokoro = Kokoro(settings.KOKORO_MODEL_PATH, settings.KOKORO_VOICES_PATH)

WAKE_WORD_PATTERNS = { w: re.compile(rf"\b{re.escape(w)}\b", flags=re.IGNORECASE) for w in settings.WAKE_WORDS}

def speak(text: str) -> None:
    if not text.strip():
        return
    cleaned_text = re.sub(r'[^\w\s,]', '', text)
    samples, sample_rate = kokoro.create(cleaned_text, voice= settings.KOKORO_VOICE, speed= settings.KOKORO_SPEED, lang="en-us")
    sd.play(np.array(samples), sample_rate)
    sd.wait()

def extract_command(text: str):
    best_match = None  
    for word, pattern in WAKE_WORD_PATTERNS.items():
        match = pattern.search(text)
        if match and (best_match is None or match.start() < best_match[1].start()):
            best_match = (word, match)

    if best_match is None:
        return None, None

    word, match = best_match
    remainder = text[match.end():]
    remainder = remainder.strip(" ,.:;-\u2014")  # trim leading punctuation/space
    return word, remainder
