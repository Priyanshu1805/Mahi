# Final Test Script for OpenWakeWord
# Note: On Windows with Python 3.12, we use the ONNX framework.
# We also need to provide audio frames to the predict() method.

from openwakeword.model import Model
import numpy as np

# Initialize the model with ONNX (required for your environment)
model = Model(inference_framework="onnx")

print("OpenWakeWord is ready!")
print("This script uses a loop with empty audio to verify the model is running.")

# To test with a real microphone, you would need to capture audio with PyAudio
# and pass 1280 samples (at 16kHz) to the predict() method.

while True:
    # Creating 1280 samples of silence (16000 Hz * 0.08 seconds)
    dummy_audio = np.zeros(1280, dtype=np.int16)
    
    # Run prediction
    prediction = model.predict(dummy_audio)
    
    print(prediction)
    
    # Stop after 5 loops for this automated test
    break 
