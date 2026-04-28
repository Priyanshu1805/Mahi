import subprocess
import os
import sys
import wave
import threading
import pyaudio
import numpy as np
from playsound import playsound
from openwakeword.model import Model

import requests
import json
from integrations import android, gmail, calendar
from remote import server
import traceback

# Use standard print as it is thread-safe in Python 3 for single calls
def safe_print(*args, **kwargs):
    print(*args, **kwargs)

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
WHISPER_EXE   = r"whisper_bin\Release\whisper-cli.exe"
WHISPER_MODEL = r"whisper.cpp\models\ggml-base.en.bin"
PIPER_EXE     = r"piper_temp\piper\piper.exe"
PIPER_MODEL   = r"en_US-lessac-medium.onnx"
WAKE_WORD     = "hey_jarvis"   # Say "Hey Jarvis" to activate Mahi
OLLAMA_URL    = "http://127.0.0.1:11434/api/generate"
MIC_INDEX     = None           # Use None for default, or an index from list_mic.py
THRESHOLD     = 0.20           # Higher sensitivity for soft voices

CHUNK          = 1280
RATE           = 16000
RECORD_SECONDS = 4

# ─────────────────────────────────────────────
# UI – runs in a separate thread
# ─────────────────────────────────────────────
_ui_ready = threading.Event()
_ui_bridge = None   # set once Qt is up

def _run_ui():
    global _ui_bridge
    try:
        from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QFrame
        from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
        from PyQt5.QtGui import QFont, QPalette, QColor

        class Bridge(QObject):
            status_changed = pyqtSignal(str)

        _ui_bridge = Bridge()
        _ui_ready.set()

        class HUD(QWidget):
            def __init__(self):
                super().__init__()
                self.setWindowTitle("MAHI OS - HUD")
                self.setFixedSize(700, 300)
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.setAttribute(Qt.WA_TranslucentBackground)
                
                # Main container with glassmorphism-ish look
                self.container = QFrame(self)
                self.container.setGeometry(10, 10, 680, 280)
                self.container.setStyleSheet("""
                    QFrame {
                        background-color: rgba(10, 15, 25, 200);
                        border: 2px solid #00d4ff;
                        border-radius: 20px;
                    }
                """)

                lay = QVBoxLayout(self.container)

                self.header = QLabel("● MAHI CORE ONLINE ●")
                self.header.setStyleSheet("color: #00d4ff; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', sans-serif;")
                self.header.setAlignment(Qt.AlignLeft)
                
                self.title = QLabel("MAHI AI")
                self.title.setStyleSheet(
                    "color: #ffffff; font-size: 60px; font-weight: 900; font-family: 'Arial Black';"
                )
                self.title.setAlignment(Qt.AlignCenter)

                self.status = QLabel("SYSTEM IDLE")
                self.status.setStyleSheet(
                    "color: #007777; font-size: 24px; font-family: 'Consolas', monospace;"
                )
                self.status.setAlignment(Qt.AlignCenter)

                self.footer = QLabel("V.2.0 | ADB CONNECTED | OLLAMA READY")
                self.footer.setStyleSheet("color: #005566; font-size: 10px; font-family: sans-serif;")
                self.footer.setAlignment(Qt.AlignRight)

                lay.addWidget(self.header)
                lay.addStretch()
                lay.addWidget(self.title)
                lay.addWidget(self.status)
                lay.addStretch()
                lay.addWidget(self.footer)

                # Pulse animation
                self._opacity = 1.0
                self._fading = True
                t = QTimer(self)
                t.timeout.connect(self._pulse)
                t.start(50)

                _ui_bridge.status_changed.connect(self._set_status)

            def _pulse(self):
                if self._fading:
                    self._opacity -= 0.02
                    if self._opacity <= 0.4: self._fading = False
                else:
                    self._opacity += 0.02
                    if self._opacity >= 1.0: self._fading = True
                
                # Update header pulse
                self.header.setStyleSheet(f"color: rgba(0, 212, 255, {int(self._opacity*255)}); font-size: 14px; font-weight: bold;")

            def _set_status(self, text):
                self.status.setText(text.upper())
                color = "#00d4ff"
                if "LISTENING" in text.upper(): color = "#ff3333"
                elif "THINKING" in text.upper(): color = "#ffaa00"
                elif "SPEAKING" in text.upper(): color = "#00ff88"
                self.status.setStyleSheet(f"color: {color}; font-size: 24px; font-family: 'Consolas';")
                self.container.setStyleSheet(f"QFrame {{ background-color: rgba(10, 15, 25, 200); border: 2px solid {color}; border-radius: 20px; }}")

            def mousePressEvent(self, event):
                self.oldPos = event.globalPos()

            def mouseMoveEvent(self, event):
                delta = QPoint(event.globalPos() - self.oldPos)
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.oldPos = event.globalPos()

        app = QApplication(sys.argv)
        from PyQt5.QtCore import QPoint
        win = HUD()
        win.show()
        app.exec_()
    except Exception as e:
        print(f"[UI Error] {e}")
        _ui_ready.set()

def set_status(text):
    """Call this from the main thread to update the HUD."""
    print(f"  [STATUS] {text}")
    if _ui_bridge is not None:
        try:
            _ui_bridge.status_changed.emit(text)
        except Exception:
            pass

# ─────────────────────────────────────────────
# CORE FUNCTIONS
# ─────────────────────────────────────────────

def record_audio_from_stream(stream, filename):
    """Captures audio from an already open stream and saves it."""
    safe_print("  [STATUS] Listening...")
    frames = []
    # Record for the duration
    for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
        try:
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
        except:
            break

    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
    safe_print(f"  >> Captured command to {filename}")


def transcribe(filename):
    """Uses Whisper to convert the recorded WAV file into text."""
    set_status("Transcribing...")
    result = subprocess.run(
        [WHISPER_EXE, "-m", WHISPER_MODEL, "-f", filename, "-nt"],
        capture_output=True, text=True, timeout=30
    )
    text = result.stdout.strip()
    print(f"  >> You said: {text!r}")
    return text


def ask_ai(prompt):
    """Sends the user's text to Ollama and gets a response, handling direct commands first."""
    set_status("Thinking...")
    
    # Handle direct commands first (super fast)
    cmd = prompt.lower()
    if "battery" in cmd:
        return f"The battery level is {android.get_battery_level()}."
    if "screenshot" in cmd:
        return android.take_screenshot()
    if "email" in cmd or "gmail" in cmd:
        return gmail.read_emails()
    if "calendar" in cmd or "event" in cmd:
        return calendar.get_events()
    if "list apps" in cmd or "installed apps" in cmd:
        return f"Here are your apps: {android.list_installed_apps()}"

    # Default to Ollama API for everything else
    payload = {
        "model": "llama3",
        "prompt": f"System: Your name is Mahi. You are a concise, helpful AI assistant. Respond briefly. User: {prompt}",
        "stream": False
    }
    try:
        # Increased timeout to 120s because LLMs can take time to load initially
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            reply = response.json().get("response", "")
            print(f"  >> Mahi: {reply}")
            return reply
        else:
            print(f"  [Ollama Error] Status {response.status_code}: {response.text}")
            return "Sorry, I am having trouble connecting to my brain."
    except Exception as e:
        print(f"  [Ollama Connection Error] {e}")
        return "Brain connection failed. Please check if Ollama is running."


def speak(text):
    """Uses Piper for TTS and Pygame for reliable audio playback."""
    set_status("Speaking...")
    import pygame
    out_path = os.path.abspath("out.wav")
    try:
        # Generate speech using Piper
        proc = subprocess.Popen(
            [PIPER_EXE, "--model", PIPER_MODEL, "--output_file", out_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        proc.communicate(input=text.encode("utf-8"), timeout=30)
        proc.wait()

        # Play speech using Pygame (more robust than playsound)
        if os.path.exists(out_path):
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(out_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload() # Free the file for next use
        else:
            print("  [TTS Error] Audio file not generated!")
    except Exception as e:
        print(f"  [TTS Error] {e}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Start UI Thread
    ui_thread = threading.Thread(target=_run_ui, daemon=True)
    ui_thread.start()

    # 2. Start Remote HUD Server
    server_thread = threading.Thread(target=server.run_server, daemon=True)
    server_thread.start()

    # Wait briefly for UI initialization
    _ui_ready.wait(timeout=3)

    safe_print("\n[1/3] Loading OpenWakeWord model...")
    try:
        oww_model = Model(inference_framework="onnx")
        safe_print("[2/3] Model loaded:", list(oww_model.models.keys()))
    except Exception as e:
        safe_print(f"[ERROR] Could not load OpenWakeWord: {e}")
        sys.exit(1)

    safe_print("[3/3] Opening persistent microphone...")
    try:
        pa = pyaudio.PyAudio()
        mic = pa.open(format=pyaudio.paInt16, channels=1, rate=RATE,
                      input=True, frames_per_buffer=CHUNK, input_device_index=MIC_INDEX)
        set_status("SYSTEM READY")
    except Exception as e:
        safe_print(f"[ERROR] Could not open mic: {e}")
        sys.exit(1)

    safe_print(f"\n=== MAHI READY === Say 'Hey Jarvis' to activate. Ctrl+C to quit.\n")

    try:
        while True:
            # Check for remote commands from the Dashboard Queue
            if not server.command_queue.empty():
                remote_cmd = server.command_queue.get()
                safe_print(f"\n[REMOTE] Received command: {remote_cmd}")
                response = ask_ai(remote_cmd)
                speak(response)

            # Read audio data from persistent stream
            try:
                data = mic.read(CHUNK, exception_on_overflow=False)
            except OSError as e:
                safe_print(f"  [Mic error] {e} — retrying...")
                continue

            audio = np.frombuffer(data, dtype=np.int16)
            
            # Predict Wake Word
            try:
                preds = oww_model.predict(audio)
            except Exception as e:
                safe_print(f"  [Prediction Error] {e}")
                continue

            if not preds: continue
            score = preds.get(WAKE_WORD, 0)
            
            # Monitor Mic Levels
            peak = np.max(np.abs(audio))
            if peak >= 32760:
                 safe_print(f"!!! WARNING: Mic is CLIPPING (Level: {peak}).   ", end="\r")
            elif peak > 500: 
                 safe_print(f"Mic Level: {peak} | WakeWord Score: {score:.3f}   ", end="\r")

            # Handle Wake Word Activation
            if score > THRESHOLD:
                safe_print(f"\n[WAKE WORD] Detected! (score={score:.2f})")

                try:
                    # RECORD COMMAND (Using the SAME stream, no stop/start)
                    record_audio_from_stream(mic, "input.wav")
                    
                    command = transcribe("input.wav")

                    if command.strip() and "[BLANK_AUDIO]" not in command:
                        response = ask_ai(command)
                        speak(response)
                    else:
                        safe_print("  >> Nothing heard or transcription failed. Listening again...")
                        set_status("SYSTEM READY")
                except Exception as e:
                    safe_print(f"  [Pipeline error] {e}")
                    traceback.print_exc()
                    set_status("ERROR")

                set_status("SYSTEM READY")
                safe_print(f"\n=== Listening for wake word...\n")

    except KeyboardInterrupt:
        safe_print("\nShutting down Mahi gracefully.")
    except Exception as e:
        safe_print(f"\n[CRITICAL ERROR] {e}")
        traceback.print_exc()
    finally:
        try:
            mic.stop_stream()
            mic.close()
            pa.terminate()
        except:
            pass