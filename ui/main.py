import queue
import threading

from speech.kokoro_tts import extract_command, speak, start_interrupt_listener
from speech.stt import calibrate, listen_once, transcribe_audio
from tools.alarm import start_watcher
from settings import settings

from agent.graph import graph
from ui.assistant.hud import ui_set_state,  ui_shutdown

def handle_command(command_text: str) -> bool:
    if "stop" in command_text or "exit" in command_text:
        speak("Goodbye.")
        return False

    result = graph.invoke({"user_input": command_text})
    print(f"[AGENT]: {result['response']}\n")
    speak(result['response'])
    return True

def converse() -> bool:
    while True:
        ui_set_state("listening")
        audio = listen_once(timeout= settings.FOLLOWUP_LISTEN_SECONDS, phrase_time_limit=10)
        if audio is None:
            ui_set_state("idle")
            return True

        text = transcribe_audio(audio)
        if not text: 
            continue 
        if not handle_command(text):
            return False

def main_loop():
    calibrate()
    start_watcher(30)
    start_interrupt_listener()
    print("AI Agent started.")
    print(f"Listening for wake word(s): {', '.join(settings.WAKE_WORDS)} ...")
    print("You can also just type a command into the terminal at any time.\n")
 
    typed_input_queue: "queue.Queue[str]" = queue.Queue()
 
    def terminal_listener():
        while True:
            try:
                typed = input()
            except EOFError:
                break
            typed = typed.strip()
            if typed: typed_input_queue.put(typed.lower())
 
    threading.Thread(target=terminal_listener, daemon=True).start()
 
    running = True
    while running:
        try: typed_text = typed_input_queue.get_nowait()
        except queue.Empty: typed_text = None
 
        if typed_text is not None:
            print(f"[Typed]: {typed_text}")
            running = handle_command(typed_text)
            if running: running = converse()
            continue
 
        ui_set_state("idle")
        audio = listen_once(timeout=1, phrase_time_limit=8)
        if audio is None: continue  # no voice, loop back and check typed input
 
        text = transcribe_audio(audio)
        if not text: continue
 
        print(f"[Heard]: {text}")
 
        wake_word, command_text = extract_command(text)
        if wake_word is None: continue  # no wake word, keep listening 
 
        print(f"Wake word '{wake_word}' detected.")
 
        if not command_text:
            speak("Yes? I'm listening.")
            ui_set_state("listening")
            command_audio = listen_once(timeout=6, phrase_time_limit=10)
            if command_audio is None:
                speak("I didn't catch that.")
                continue
            command_text = transcribe_audio(command_audio)
            if not command_text:
                speak("Sorry, I couldn't understand that.")
                continue
 
        running = handle_command(command_text)
        if running: running = converse()
    ui_shutdown()