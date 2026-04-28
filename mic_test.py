# Real-time Microphone Test for OpenWakeWord
import pyaudio
import numpy as np
from openwakeword.model import Model

# Initialize OpenWakeWord
# Note: Using inference_framework="onnx" for compatibility
model = Model(inference_framework="onnx")

# Audio configuration
CHUNK = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("\n--- Listening for Wake Words ---")
print("Currently tracking:", list(model.models.keys()))
print("Speak 'Alexa', 'Hey Jarvis', or other supported words...")

try:
    while True:
        # Read audio data
        data = stream.read(CHUNK, exception_on_overflow=False)
        audio_data = np.frombuffer(data, dtype=np.int16)

        # Predict
        prediction = model.predict(audio_data)

        # Check if any wakeword is detected (threshold > 0.5)
        for wakeword, score in prediction.items():
            if score > 0.5:
                print(f"Detected: {wakeword} (score: {score:.2f})")

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
