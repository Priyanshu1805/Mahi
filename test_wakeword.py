from openwakeword.model import Model
import numpy as np

# Initialize the model with ONNX framework (recommended for Windows/Python 3.12)
model = Model(inference_framework="onnx")

print("Model initialized. Waiting for predictions (using dummy data for test)...")

try:
    # The predict method usually expects audio data. 
    # We'll use a small buffer of zeros just to see if the model runs.
    dummy_audio = np.zeros(1280, dtype=np.int16)
    
    while True:
        prediction = model.predict(dummy_audio)
        print(prediction)
        # break after one prediction for the automated test
        break 
except Exception as e:
    print(f"Error during prediction: {e}")
