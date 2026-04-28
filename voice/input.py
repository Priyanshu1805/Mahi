import speech_recognition as sr

def listen():
    """Listens for a voice command and returns it as text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.5)
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("Could not request results; check your internet connection.")
        return ""
    except Exception as e:
        return ""
