import speech_recognition as sr

recognizer = sr.Recognizer()
microphone = sr.Microphone()

def calibrate() -> None:
    print("Calibrating microphone for ambient noise... please stay quiet.")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
    print("Calibration done.")

def listen_once(timeout=None, phrase_time_limit=8) -> sr.AudioData | None:
    with microphone as source:
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            return audio
        except sr.WaitTimeoutError:
            return None

def transcribe_audio(audio: sr.AudioData) -> str:
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"[STT error] Could not reach recognition service: {e}")
        return ""