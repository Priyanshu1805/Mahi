import pyttsx3
import threading

# Use a lock to prevent concurrent access to the engine
engine_lock = threading.Lock()

def speak(text):
    """
    Converts text to speech using pyttsx3.
    Initializes the engine locally to avoid threading issues.
    """
    print(f"MAHI: {text}")
    
    def _speak():
        with engine_lock:
            try:
                # Initialize engine inside the thread for stability
                engine = pyttsx3.init()
                engine.setProperty('rate', 180)
                engine.say(text)
                engine.runAndWait()
                # Stop the engine to release resources
                engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")

    # Run TTS in a separate short-lived thread to avoid blocking the main AI loop
    # but still use a lock to avoid overlapping speech
    tts_thread = threading.Thread(target=_speak)
    tts_thread.start()
    tts_thread.join() # Wait for speech to finish if we want it to be synchronous
