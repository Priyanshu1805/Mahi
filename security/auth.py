from voice.input import listen
from voice.output import speak

def confirm(action):
    speak(f"MAHI is requesting permission for {action}. Should I proceed?")
    ans = listen().lower()
    return "yes" in ans or "proceed" in ans or "allow" in ans