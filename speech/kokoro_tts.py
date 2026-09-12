import re
import numpy as np
import sounddevice as sd
import time
import threading
from pynput import keyboard
from kokoro_onnx import Kokoro
from settings import settings
from ui.assistant.hud import ui_set_state

kokoro = Kokoro(settings.KOKORO_MODEL_PATH, settings.KOKORO_VOICES_PATH)

WAKE_WORD_PATTERNS = { w: re.compile(rf"\b{re.escape(w)}\b", flags=re.IGNORECASE) for w in settings.WAKE_WORDS}

interrupt_event = threading.Event()

def start_interrupt_listener() -> None:
    def on_press(key):
        char = getattr(key, "char", None)
        if char and char.lower() == settings.INTERRUPT_KEY:
            interrupt_event.set()
 
    keyboard.Listener(on_press=on_press, daemon=True).start()

def speak(text: str) -> None:
    if not text.strip():
        return
    cleaned_text = re.sub(r'[^\w\s,]', '', text)
    ui_set_state("speaking", text)
    interrupt_event.clear()
    samples, sample_rate = kokoro.create(cleaned_text, voice= settings.KOKORO_VOICE, speed= settings.KOKORO_SPEED, lang="en-us")
    sd.play(np.array(samples), sample_rate)

    while sd.get_stream().active and not interrupt_event.is_set():          # for precaution
        time.sleep(0.05)
 
    if interrupt_event.is_set(): 
        ui_set_state("idle")
        sd.stop()
        print(f"[Interrupted] Speech stopped by '{settings.INTERRUPT_KEY.upper()}' key press.")
    interrupt_event.clear()

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
