import speech_recognition as sr
import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 180)

def speak(text):
    """Converts text to speech using pyttsx3."""
    print("Mahi:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listens for a voice command and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except Exception as e:
        # Return an empty string if recognition fails
        return ""
