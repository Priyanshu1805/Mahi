import pvporcupine
import pyaudio
import struct
import os
from dotenv import load_dotenv

load_dotenv()

# Get Access Key from .env
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "YOUR_PICOVOICE_ACCESS_KEY")
KEYWORD_PATH = "mahi.ppn" # Path to your trained wake word file

def detect_wake_word():
    """
    Listens for the wake word using a custom trained .ppn file.
    """
    if ACCESS_KEY == "YOUR_PICOVOICE_ACCESS_KEY":
        print("ERROR: Picovoice Access Key missing in .env!")
        return False

    # Check if the custom keyword file exists
    if os.path.exists(KEYWORD_PATH):
        try:
            porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[KEYWORD_PATH])
        except Exception as e:
            print(f"ERROR initializing with custom keyword: {e}")
            return False
    else:
        print(f"WARNING: {KEYWORD_PATH} not found. Falling back to built-in 'jarvis'.")
        porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["jarvis"])

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )

    print(f"MAHI: Awaiting activation (Listening for '{porcupine.sample_rate}' mode)...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            if porcupine.process(pcm) >= 0:
                print("MAHI: Wake word detected!")
                return True
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()