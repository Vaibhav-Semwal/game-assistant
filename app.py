import threading
from ui.main import main_loop
from ui.assistant.hud import create_overlay

if __name__ == "__main__":
    assistant_thread = threading.Thread(target= main_loop, daemon=True)
    assistant_thread.start()

    overlay = create_overlay() 
    overlay.run()  
    print("\nStopped.")