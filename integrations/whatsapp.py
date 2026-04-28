import os
import time

def send_whatsapp_message(number, message):
    """
    Sends a WhatsApp message via ADB by opening the wa.me link on the Android device.
    Note: This opens the chat with the message pre-filled.
    """
    # Format the message for the URL
    formatted_message = message.replace(" ", "%20")
    
    # Open WhatsApp chat
    os.system(f'adb shell am start -a android.intent.action.VIEW -d "https://wa.me/{number}?text={formatted_message}"')
    
    # Optional: Wait and simulate 'Enter' key to send (depends on device speed)
    time.sleep(2)
    os.system("adb shell input keyevent 22") # Right
    os.system("adb shell input keyevent 22") # Right (to reach send button)
    os.system("adb shell input keyevent 66") # Enter
    
    return f"WhatsApp command sent to device for {number}"
